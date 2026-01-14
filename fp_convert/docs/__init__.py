import logging
import os
import pytz
import re
from datetime import datetime
from pathlib import Path
from pylatex import (
    Command,
    Document,
    Foot,
    Head,
    LongTable,
    MultiColumn,
    Package,
    PageStyle,
)
from pylatex.utils import NoEscape as NE
from pylatex.utils import escape_latex as EL
from pylatex.utils import bold, italic
from pylatex.position import Center, VerticalSpace
from pylatex.basic import MediumText
from pylatex.base_classes import LatexObject
from pylatex.section import (
    Paragraph,
    Section,
    Subparagraph,
    Subsection,
    Subsubsection,
)
from freeplane import Mindmap, Node
from typing import List, Dict, Callable, Optional, Union

from fp_convert.config import (
    Config, config_classes,
)

from fp_convert.utils.helpers import (
    DocContext,
    DocInfo,
    get_label,
    get_fpc_block_type,
    param_pat,
    ensure_directory_exists,
    get_processed_note_lines,
    is_ignore_type,
    retrieve_note_lines,
    trunc80,
)

from fp_convert.errors import (
    IncorrectInitialization,
    InvalidFPCBlockTypeException,
    InvalidFilePathException,
    InvalidRefException,
    InvalidTypeException,
    MaximumSectionDepthException,
    MissingFileException,
)
class GeneralDoc(Document):
    """
    The main document container for building any document using fp-convert.
    For specific documents, use this class as the base class.
    """

    def __init__(
        self,
        mm_file: Union[str, Path],
        builders: Dict[str, Callable],
        logger: Optional[logging.Logger] = None,
        documentclass: str = "article",
        working_dir: Union[str, Path] = ".",
        docinfo: Optional[DocInfo] = None,
        config: Optional[Config] = None,
        font_family: Optional[List] = None,
    ):
        """
        The argument mm_file should be a path to a Freeplane Mindmap file.
        The builders dictionary holds various builder-functions required to
        construct the document.
        The logger is a Python logger object to be used for logging messages.
        The argument docinfo should be a DocInfo object, containing the details
        The documentclass is the LaTeX document-type to be used to construct
        the document. By default it is "article".
        The working_dir is the directory in which the document is to be built.
        The argument docinfo should be a DocInfo object, containing the details
        of the document being generated. If docinfo is not supplied, then the
        root node of the mindmap must contain required information to build it.
        Additional arguments are: config and font_family. Config itself may be
        composed of multiple components like Main, Stopframe, Table, DBSchema,
        etc. It is possible to build a Config object separately and supply
        that instead of using the default config used by this class.

        :param mm_file: A string containing the path to a Freeplane Mindmap
            file. It is a mandatory argument.
        :param builders: A dictionary mapping the value of attribute fpcBlockType
            to the corresponding block-builder function. It must be supplied to
            build any document.
        :param logger: A logger to be used for logging messages.
        :param documentclass: The LaTeX document-type to be used to construct
            this document. The default is "article" type.
        :param working_dir: The directory in which the document is to be built.
        :param docinfo: A DocInfo object, containing the document related
            information. If it is supplied, it would override the one obtained
            from the supplied mindmap's root node.
        :param config: A Config instance that defines document styling including
            page geometry, colors, and other formatting parameters required for
            various blocks in this document. The default value supplied is None,
            which indicates that the default values for all parameters should
            be used.
        :param font_family: The font-family to be used used while constructing the
            PDF document.
        """
        super().__init__(
            Path(mm_file).stem,
            documentclass=documentclass
        )

        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.WARNING)

        # Not keeping these attributes in ctx at the moment which may change
        # later.
        self.mm_file = Path(mm_file)
        self.mm = Mindmap(str(self.mm_file))
        self.blocks = list()  # List of blocks which would be rendered to PDF

        # Level specific LaTeX section blocks
        self.sections: List[None|Command] = [
            None,
            Section,
            Subsection,
            Subsubsection,
            Paragraph,
            Subparagraph,
        ]

        # First load default builder-functions into builders dict
        self.builders: Dict[str, Callable] = dict()
        self.builders.update(builders)

        default_configs = [cc() for cc in config_classes]
            
        # Use user-supplied configuration, or the default one
        if config:
            self.config = config
            for co in default_configs:
                self.config.add_component(co)
        else:
            self.config = Config(*default_configs)

        # Choose right value of DocInfo for this invocation. Either the
        # DocInfo object is supplied exernally, or it is to be rerieved
        # from the mindmap.
        if docinfo:
            if not isinstance(docinfo, DocInfo):
                raise IncorrectInitialization(
                    "Supplied argument 'docinfo' is not an instance of "
                    "DocInfo class")
            docinfo_v = docinfo
        elif self.mm.rootnode.notes:
            docinfo_v = DocInfo(self.mm.rootnode.notes)
        else:
            raise IncorrectInitialization(
                "No document-information found in the supplied mindmap."
            )

        # Initialize document context object to hold context specific details
        self.ctx = DocContext(docinfo_v)
        self.ctx.working_dir = Path(working_dir)
        ensure_directory_exists(self.ctx.working_dir)
        self.ctx.images_dir = Path(working_dir, "images")
        ensure_directory_exists(self.ctx.images_dir)

        # Create LongTable object to render the changeset-content
        self.ctx.changeset_table = LongTable(r"l c p{0.75\linewidth}")

        self.packages: List[str] = [
            ("geometry", tuple()),
            ("amssymb", tuple()),
            ("xcolor", ("dvipsnames", "table")),
            ("tcolorbox", ("most",)),
            ("placeins", ("section",)),
            ("titlesec", tuple()),
            ("ulem", tuple()),  # for strikethrough
            ("xspace", tuple()),
            ("fontawesome5", tuple()),
            ("makecell", tuple()),
            ("fontenc", ("OT1",)),
            ("booktabs", tuple()),
            ("longtable", tuple()),
            ("marginnote", tuple()),
            ("hyperref", tuple()),
            ("multirow", tuple()),
            ("tabularx", tuple()),
            ("enumitem", tuple()),
            ("mdframed", ("framemethod=TikZ",)),
            ("ragged2e", ("raggedrightboxes",)),
            # ("roboto", ("sfdefault",)),
        ]
        self.preambles: Dict[str, List[Union[NE, LatexObject, str]]] = dict()
        self.preambles["main"] = [  # Commonly needed preamble-blocks in a list
            NE(rf"\setcounter{{secnumdepth}}{{{self.config.main.max_sec_depth}}}"),
            NE(rf"\setcounter{{tocdepth}}{{{self.config.main.toc_depth}}}"),
            NE(rf"\setlength{{\parindent}}{{{self.config.main.par_indent}}}"),
            NE(rf"\titleformat{{\paragraph}}{self.config.main.par_title_format}"),
            NE(
                rf"\titlespacing*{{\paragraph}}{self.config.main.par_title_spacing}"
            ),  # noqa
            NE(
                rf"\titleformat{{\subparagraph}}{self.config.main.subpar_title_format}"
            ),  # noqa
            NE(
                rf"\titlespacing*{{\subparagraph}}{self.config.main.subpar_title_spacing}"
            ),  # noqa
            NE(rf"\definecolor{{mccol}}{self.config.main.mc_color}"),
            NE(
                r"\newcommand\margincomment[1]{\RaggedRight{"
                r"\marginpar{\hsize1.7in\tiny\color{mccol}{#1}}}}"
            ),
            NE(
                r"\mdfdefinestyle{StopFrame}{linecolor="
                rf"{self.ctx.regcol(self.config.stopframe.line_color)}, outerlinewidth="
                rf"{self.config.stopframe.outer_line_width}, "
                rf"roundcorner={self.config.stopframe.round_corner_size},"
                rf"rightmargin={self.config.stopframe.outer_right_margin},"
                rf"innerrightmargin={self.config.stopframe.inner_right_margin},"
                rf"leftmargin={self.config.stopframe.outer_left_margin},"
                rf"innerleftmargin={self.config.stopframe.inner_left_margin},"
                rf"backgroundcolor={self.config.stopframe.background_color}}}"
            ),
            NE(
                fr"""
\newcommand{{\celltarget}}[2]{{\mbox{{\hypertarget{{#1}}{{}}#2}}}}
\hypersetup{{
pdftitle={{{self.ctx.docinfo["doc_title"]}}},
pdfsubject={{{self.ctx.docinfo["doc_title"]}}},
pdfauthor={{{self.ctx.docinfo["doc_author"]}}},
pdfcreator={{"fp-convert using pylatex, freeplane-io, and LaTeX with hyperref"}},
%pdfpagemode=FullScreen,
colorlinks=true,
linkcolor={self.ctx.regcol(self.config.main.link_color)},
filecolor={self.ctx.regcol(self.config.main.file_color)},
urlcolor={self.ctx.regcol(self.config.main.url_color)},
pdftoolbar=true,
pdfpagemode=UseNone,
pdfstartview=FitH
}}"""
            ),
            # Setting headheight
            NE(rf"\setlength\headheight{{{self.config.main.head_height}}}"),
            # Styling the geometry of the document
            #
            NE(
                rf"""
\geometry{{
a4paper,
%total={{170mm,257mm}},
left={self.config.main.left_margin},
inner={self.config.main.inner_margin},
right={self.config.main.right_margin},
outer={self.config.main.outer_margin},
top={self.config.main.top_margin},
bottom={self.config.main.bottom_margin},
}}"""
            ),
            NE(r"\tcbuselibrary{skins, breakable, theorems, listings}"),
            NE(
                rf"""
\rowcolors{{2}}%
{{{self.ctx.regcol(self.config.table.rowcolor_1)}}}%
{{{self.ctx.regcol(self.config.table.rowcolor_2)}}}%
"""
            ),
            NE(r"\renewcommand{\arraystretch}{1.5}%"),
            NE(r"\newlist{dbitemize}{itemize}{3}"),
            NE(r"\setlist[dbitemize,1]{label=\textbullet,leftmargin=0.2cm}"),
            NE(r"\setlist[dbitemize,2]{label=$\rightarrow$,leftmargin=1em}"),
            NE(r"\setlist[dbitemize,3]{label=$\diamond$}"),

            NE(
                r"""
\makeatletter
{\tiny % Capture font definitions of \tiny
\xdef\f@size@tiny{\f@size}
\xdef\f@baselineskip@tiny{\f@baselineskip}

\small % Capture font definitions of \small
\xdef\f@size@small{\f@size}
\xdef\f@baselineskip@small{\f@baselineskip}

\normalsize % Capture font definitions for \normalsize
\xdef\f@size@normalsize{\f@size}
\xdef\f@baselineskip@normalsize{\f@baselineskip}
}

% Define new \tinytosmall font size
\newcommand{\tinytosmall}{%
  \fontsize
    {\fpeval{(\f@size@tiny+\f@size@small)/2}}
    {\fpeval{(\f@baselineskip@tiny+\f@baselineskip@small)/2}}%
  \selectfont
}

% Define new \smalltonormalsize font size
\newcommand{\smalltonormalsize}{%
  \fontsize
    {\fpeval{(\f@size@small+\f@size@normalsize)/2}}
    {\fpeval{(\f@baselineskip@small+\f@baselineskip@normalsize)/2}}%
  \selectfont
}
\makeatother

% Define macro to save current font size for later using \savedlastfontsize
\makeatletter
\newcommand{\savecurrentfontsize}{\let\savedlastfontsize\@currsize}
\makeatother
"""
            ),
            # Additional preamble-blocks for other modules can be added
            # here in future.
        ]  # Main preamble-blocks end here
            
        if font_family:
            if len(font_family) < 2:
                raise IncorrectInitialization(
                    "font_family must contain at least 2 elements: [name, options]"
                )
            self.packages.append((font_family[0], font_family[1]))
        else:
            self.packages.append(("utopia", tuple()))

    def build_section_content(self, node: Node):
        """
        Build the section-content as one or more paragraphs using notes
        associated with the supplied node.

        Parameters
        ----------
        node: Node
            The node whose note-texts are to be converted to section-content.
        
        Returns
        -------
        list[LatexObject|NE]|list[]
            A list of LaTeX objects or NoEscape objects, if notes exist;
            else an empty list.
        """
        # ret = [
        #     x for pair in zip(lines, [Command("par")] * (len(lines) - 1)) \
        #         for x in pair] + [lines[-1]] if lines else []
        ret = list()
        lines = get_processed_note_lines(node, self.ctx)
        for lst in lines:
            ret.extend(lst)
            ret.append(Command("par"))
        if ret:
            ret[-1] = ""  # remove last \par to prevent unnecessary newline
        return ret

    # def reset(self):
    #     self.logger.debug("Resetting the document-building block. You " \
    #     "can call traverse_and_build() again to rebuild the document.")
    #     self.blocks = list()

    def traverse_and_build(
        self,
        node: Optional[Node] = None,
        depth: int = 1,
        max_depth: int = 5
    ):
        """
        Traverse the mindmap nodes and build the components of the
        document in blocks. This method starts from the root node by default.
        Optionally another node can be specified to start the traversal from.

        If reset() method is called, then this method can be called again to
        traverse the mindmap and rebuild the content of the document.

        Parameters
        ----------
        node: Node
            The current node to traverse. If None, starts from root-node.
        depth: int
            Depth of the node supplied in the mindmap. Default is 1.
        max_depth: int
            Maximum depth of nodes to traverse. Default is 5.
        """
        if node is None:
            node = self.mm.rootnode
            depth = 1
        
        if len(node.children):  # If node has children
            if depth > max_depth:
                raise MaximumSectionDepthException(
                    f"Maximum depth ({depth}) of sections reached for ndoe: "
                    f"'{node}'. Move this node to a lower level by "
                    "rearranging the structure/sections of your document in "
                    "the mindmap."
                )

            for child in node.children:
                # Ignore the node, if marked to ignore
                if is_ignore_type(child):
                    continue

                # block_type = child.attributes.get("fpcBlockType", None)
                block_type = get_fpc_block_type(child, "default")

                if block_type:
                    if block_type in self.builders:
                        # Build appropriate list of blocks based on suitable
                        # builder-callable and extend document's blocks with it.
                        blocks = self.builders[block_type](
                            child, self, depth, self.builders)
                        if len(blocks):
                            self.blocks.extend(blocks)
                    else:  # Exception for unknown fpcBlockType value
                        raise InvalidFPCBlockTypeException(
                            f"Unknown fpcBlockType '{block_type}' found for node "
                            f"'{child}' with id {child.id}. Please fix the "
                            "mindmap and try again."
                        )
                else:  # Missing fpcBlockType value means it is a default-block
                    self.blocks.extend(
                        self.builders["default"](
                            child, self, depth, self.builders))
                    # self.blocks.append(self.sections[depth](NE(EL(str(child))), label=False))

                    # Build section-content from the notes of the node
                    # self.blocks.extend(
                    #     self.build_section_content(child)
                    # )

                # Similarly build content from child's children too
                # self.traverse_and_build(child, depth+1, max_depth)

    def get_absolute_file_path(self, file_path: str | Path) -> Path:
        """
        Fetch absolute file path, if file exists and a file path relative to
        the mindmap file is provided.

        Parameters:
            file_path: str|Path
        
        Returns:
            Path: A Path object containing the absolute file-path.
        """
        if not file_path:
            raise InvalidFilePathException("Supplied file path is either None or empty.")
        if not Path(file_path).is_absolute():
            # The path could be relative to the folder having mindmap file
            abs_path = Path(self.mm_file.parent.absolute(), file_path)

            if not abs_path.is_file():
                raise MissingFileException(
                    f"A required file ({file_path}) is missing. Either use an "
                    "absolute file path, or a path relative to the mindmap "
                    "itself. Also the corresponding file must exist already."
                )
            return abs_path
        return Path(file_path)

    def build_headers_and_footers(self) -> PageStyle:
        """
        Creates fancy header/footers for the pages of the document.

        Parameters: None
        Returns: PageStyle
            Returns a PageStyle object containing the details of headers and
            footers.
        """
        headfoot = PageStyle(
            "header",
            header_thickness=self.config.main.header_thickness,
            footer_thickness=self.config.main.footer_thickness,
            data=NE(
                rf"""
\renewcommand{{\headrule}}%
{{\color{{{self.ctx.regcol(self.config.main.header_line_color)}}}%
\hrule width \headwidth height \headrulewidth}}
\renewcommand{{\footrule}}%
{{\color{{{self.ctx.regcol(self.config.main.footer_line_color)}}}%
\hrule width \headwidth height \footrulewidth}}"""
            ),
        )

        lheader = cheader = rheader = lfooter = cfooter = rfooter = None
        credits_marked = False

        if self.ctx.docinfo.get("l_header_image", None):
            lheader = NE(
                rf"""
\includegraphics[%
height={self.config.main.l_header_image_height}]%
{{{self.get_absolute_file_path(self.ctx.docinfo['l_header_image'])}}}"""
            )
        elif self.ctx.docinfo.get("l_header_text", None):
            lheader = NE(rf"{self.ctx.docinfo['l_header_text']}")
        if lheader:
            with headfoot.create(Head("L")):
                headfoot.append(lheader)

        if self.ctx.docinfo.get("c_header_image", None):
            cheader = NE(
                rf"""
\includegraphics[%
height={self.config.main.c_header_image_height}]%
{{{self.get_absolute_file_path(self.ctx.docinfo['c_header_image'])}}}"""
            )
        elif self.ctx.docinfo.get("c_header_text", None):
            cheader = NE(rf"{self.ctx.docinfo['c_header_text']}")
        if cheader:
            with headfoot.create(Head("C")):
                headfoot.append(cheader)

        if self.ctx.docinfo.get("r_header_image", None):
            rheader = NE(
                rf"""
\includegraphics[%
height={self.config.main.r_header_image_height}]%
{{{self.get_absolute_file_path(self.ctx.docinfo['r_header_image'])}}}"""
            )
        elif self.ctx.docinfo.get("r_header_text", None):
            rheader = NE(rf"{self.ctx.docinfo['r_header_text']}")
        if rheader:
            with headfoot.create(Head("R")):
                headfoot.append(rheader)

        if self.ctx.docinfo.get("l_footer_image", None):
            lfooter = NE(
                rf"""
\includegraphics[%
height={self.config.main.l_footer_image_height}]%
{{{self.get_absolute_file_path(self.ctx.docinfo['l_footer_image'])}}}"""
            )
        elif self.ctx.docinfo.get("l_footer_text", None):
            if self.ctx.docinfo['l_footer_text'] != "%%":
                lfooter = NE(rf"{self.ctx.docinfo['l_footer_text']}")
        else:
            lfooter = NE(fr"\tiny{{{DocInfo.credits}}}")  # Credit-text
            credits_marked = True

        if lfooter:
            with headfoot.create(Foot("L", data=Command("normalcolor"))):
                headfoot.append(lfooter)

        if self.ctx.docinfo.get("c_footer_image", None):
            cfooter = NE(
                rf"""
\includegraphics[%
height={self.config.main.c_footer_image_height}]%
{{{self.get_absolute_file_path(self.ctx.docinfo['c_footer_image'])}}}"""
            )
        elif self.ctx.docinfo.get("c_footer_text", None):
            if self.ctx.docinfo['c_footer_text'] != "%%":
                cfooter = NE(rf"{self.ctx.docinfo['c_footer_text']}")
        elif not credits_marked:
            cfooter = NE(fr"\tiny{{{DocInfo.credits}}}")
            credits_marked = True

        if cfooter:
            with headfoot.create(Foot("C", data=Command("normalcolor"))):
                headfoot.append(cfooter)

        if self.ctx.docinfo.get("r_footer_image", None):
            rfooter = NE(
                rf"""
\includegraphics[%
height={self.config.main.r_footer_image_height}]%
{{{self.get_absolute_file_path(self.ctx.docinfo['r_footer_image'])}}}"""
            )
        elif self.ctx.docinfo.get("r_footer_text", None):
            if self.ctx.docinfo['r_footer_text'] != "%%":
                rfooter = NE(fr"\small{{{self.ctx.docinfo['r_footer_text']}}}")
        elif not credits_marked:
            rfooter = NE(fr"\tiny{{{DocInfo.credits}}}")
            credits_marked = True

        if rfooter:
            with headfoot.create(Foot("R", data=Command("normalcolor"))):
                headfoot.append(rfooter)

        return headfoot

    def build_changeset_note_lines(self, node: Node) -> List[str]:
        """
        Return a list of LaTeX objects representing the note-lines for the sections pertaining
        to the changeset section of the document. It should be supplied with a node which is
        either the base-node of the changeset section, or one of its children named |additions|
        or |deletions|.
        Parameters
        ----------
        node : Node
            The node for which the changeset note-lines are to be built.

        Returns
        -------
        List[str]
            A list of strings representing the content of note-lines of changeset nodes.
        """
        retblocks = list()
        if node.notes:
            for note in retrieve_note_lines(node.notes): # node.notes:
                retblocks.append(NE("\\noindent"))
                segments = re.split(param_pat, note)
                if len(segments) > 1:  # Docinfo parameters are present
                    for segment in segments:
                        if not re.fullmatch(param_pat, f"{segment}"):
                            retblocks.append(segment)
                        else:
                            key = segment[1:-1]
                            if key in self.ctx.docinfo.docinfo_tpl:
                                retblocks.append(
                                    self.ctx.docinfo[
                                        self.ctx.docinfo.docinfo_tpl[key]])
                            else:
                                raise InvalidRefException(
                                    f"Node [{str(node)}(ID: {node.id})] contains "
                                    f"a reference for {segment} which is not a valid "
                                    "parameter expected in the document-info usually "
                                    "found in the notes associated with the root node "
                                    "of the mindmap."
                                )
                else:
                    retblocks.append(note)
                retblocks.append(NE(r"\par"))
        return retblocks

    def build_changeset_table(self, cslist: List) -> LatexObject:
        """
        Build a LaTeX table containing the references to the additions or deletions
        made in the mindmap to generate the current version of the document. A node
        containing |additions| or |deletions| must be supplied as input to this
        method.

        Parameters
        ----------
        changeset : A list of changeset-tuples for which tabular view is to be built.

        Returns
        -------
        LatexObject
            A LaTeX objects representing a changeset table.
        """
        # tab = LongTable(r"l c p{0.75\linewidth}")
        tab = self.ctx.changeset_table  # It was created earlier in the constructor
        tab.add_hline(
            color=self.ctx.regcol(
                self.config.dbschema.tbl2_header_line_color))
        header_text = list()
        header_text.append(
            NE(
                fr"""\textcolor{{{self.ctx.regcol(
                    self.config.dbschema.tbl2_header_text_color)}}}%
                {{\tinytosmall{{{EL(italic("No."))}}}}}"""
            )
        )
        header_text.append(
            NE(
                fr"""\textcolor{{{self.ctx.regcol(
                    self.config.dbschema.tbl2_header_text_color)}}}%
                {{\tinytosmall{{{EL(italic("Type"))}}}}}"""
            )
        )
        header_text.append(
            NE(
                fr"""\textcolor{{{self.ctx.regcol(
                    self.config.dbschema.tbl2_header_text_color)}}}%
                {{\tinytosmall{{{EL(italic("Changes"))}}}}}"""
            )
        )
        tab.add_row(
            header_text,
            color=self.ctx.regcol(
                self.config.dbschema.tbl2_header_row_color
            )
        )
        tab.add_hline(color=self.ctx.regcol(
            self.config.dbschema.tbl2_header_line_color))
        tab.end_table_header()
        tab.add_hline(color=self.ctx.regcol(
            self.config.dbschema.tbl2_header_line_color))
        tab.add_row(
            (
                MultiColumn(
                    3, align="r",
                    data=NE(r"\faEllipsisH \xspace \faArrowRight")
                ),
            )
        )
        tab.add_hline(
            color=self.ctx.regcol(
                self.config.dbschema.tbl2_header_line_color
            )
        )
        tab.end_table_footer()
        tab.add_hline(
            color=self.ctx.regcol(
                self.config.dbschema.tbl2_header_line_color
            )
        )
        tab.end_table_last_footer()

        for idx, item in enumerate(cslist):
            sr_no = NE(
                fr"\tinytosmall{{\hyperlink{{{get_label(
                    item[0].id
                )}}}{{{idx+1}}}}}"
            )
            flag = None
            if item[1] == "D":
                flag = NE(
                    fr"""\textcolor{{{self.ctx.regcol(
                        self.config.main.del_mark_color
                    )}}}%
{{\tiny{{{self.config.main.del_mark_flag}\xspace {self.config.main.del_mark_text}}}}}"""
                )
            elif item[1] == "A":
                flag = NE(
                    fr"""\textcolor{{{self.ctx.regcol(
                        self.config.main.new_mark_color
                    )}}}%
{{\tiny{{{self.config.main.new_mark_flag}\xspace {self.config.main.new_mark_text}}}}}"""
                )
            else:
                raise InvalidTypeException(
                    "Invalid change-type found in changeset. Valid types are A and D only."
                )
            cs_text = NE(
                fr"\tinytosmall{{{EL(trunc80(str(item[0])))}}}"
            )
            tab.append(NE(fr"\hypertarget{{CSREF:{idx}}}{{}}"))
            tab.add_row((sr_no, flag, cs_text))
        return tab

    def build_changeset_section(self, node: Node) -> List[str]:
        """
        Build a set of tables along with its section-text, containing the
        details of the applicable changeset between two versions of the
        document. It is required to mark a change-set node with an inverted
        red triangle icon to build a change-set sction in the document.

        Parameters
        ----------
        node : Node
            The node for which the changeset tables are to be built.

        Returns
        -------
        List[str]
            A list of strings equivalent to render LaTeX elements representing
            the changeset table.
        """
        retblocks = list()
        if not len(self.ctx.changeset): # Nothing to be done
            return retblocks

        if node.notes:
            retblocks.extend(self.build_changeset_note_lines(node))
        retblocks.append(NE("\\begin{center}\\vspace{-0.5cm}"))
        retblocks.append(self.build_changeset_table(self.ctx.changeset))
        retblocks.append(NE("\\end{center}"))
        return retblocks


    def generate_pdf(
        self,
        filepath: Union[str, Path] = None,
        clean: bool = True,
        clean_tex: bool = True) -> None:
        """
        Generate PDF content from the mindmap associated with this object.

        Parameters
        ----------
        filepath : str|Path
            The path to the file to which the document is to be written.
        clean : bool
            Do not leave build files behind.
        clean_tex : bool
            If True, the intermediate TeX file is removed.

        Returns
        -------
        None
        """

        doc = Document()
        for pkg in self.packages:
            doc.packages.append(Package(pkg[0], options=pkg[1]))
        doc_version = self.ctx.docinfo.get("doc_version", "")
        doc_title = self.ctx.docinfo.get(
            "doc_title", "<Missing Document Title>")
        doc_author = self.ctx.docinfo.get(
            "doc_author", "<Missing Document Author>")
        doc_date = self.ctx.docinfo.get("doc_date", NE(r"\today"))
        head_foot = self.build_headers_and_footers()
        doc.preamble.append(head_foot)
        doc.change_document_style("header")
        doc.append(
            NE(r"""
\begin{titlepage}
\centering
\vspace*{\fill}"""))

        if self.ctx.docinfo.get("tp_top_logo", None):
            doc.append(
                NE(fr"""
\includegraphics[%
height={self.config.main.tp_top_logo_height}]%
{{{self.get_absolute_file_path(self.ctx.docinfo['tp_top_logo'])}}}\\
\vspace*{{{self.config.main.tp_top_logo_vspace}}}"""))

        doc.append(
            NE(fr"""
\huge \bfseries {doc_title}\\
    \vspace*{{0.2cm}}
\small (Version: {doc_version})\\
    \vspace*{{0.2cm}}
\large {doc_author}\\
{doc_date}\\
\normalsize"""))

        if self.ctx.docinfo.get("tp_bottom_logo", None):
            doc.append(
                NE(fr"""
\vspace*{{{self.config.main.tp_bottom_logo_vspace}}}
\includegraphics[%
height={self.config.main.tp_bottom_logo_height}]%
{{{self.get_absolute_file_path(self.ctx.docinfo['tp_bottom_logo'])}}}\\"""))

        doc.append(
            NE(r"""
\vspace*{\fill}
\end{titlepage}
"""))

        doc.append(NE(r"\tableofcontents"))
        doc.append(NE(r"\newpage"))
        doc.append(NE(r"\justify"))

        max_sec_depth = self.config.main.max_sec_depth
        if max_sec_depth > 6:
            max_sec_depth = 6
        self.traverse_and_build(self.mm.rootnode, 1, max_sec_depth)

        # Build preamble-block for this document
        for k, v in self.preambles.items():
            for pt in v:
                doc.preamble.append(pt)

        # If track changes are required to be collated into a section and if no
        # node is marked already to hold the changeset entries (by annotating
        # it with an icon of inverted red triangle), then append such a section
        # at the end of the document.
        if self.ctx.docinfo["trackchange_section"]:
            if self.ctx.changeset_node:
                # cslist = self.build_changeset_section(self.ctx.changeset_node)
                # for item in cslist:
                #     self.ctx.changeset_section.append(item)
                self.ctx.changeset_section.extend(
                    self.build_changeset_section(self.ctx.changeset_node)
                )
            else:
                cs_section = Section(self.ctx.docinfo["trackchange_section"])
                cs_section.append(NE("\\begin{center}\\vspace{-0.5cm}"))
                cs_section.append(
                    self.build_changeset_table(self.ctx.changeset))
                cs_section.append(NE("\\end{center}"))
                self.blocks.append(cs_section)

        # Include in the document all the colors encountered so far
        for color in self.ctx.colors:
            doc.add_color(color[0], color[1], color[2])

        for obj in self.blocks:
            doc.append(obj)

        with doc.create(Center()):
            doc.append(VerticalSpace(".5cm"))
            doc.append(MediumText(bold(r"* * * * *")))

            # docinfo based timezone is preferred
            if self.ctx.docinfo.get("timezone", None):
                tz = self.ctx.docinfo["timezone"]
            else:  # then comes option of confuguration based timezone
                tz = self.config.main.timezone
            retrieval_date = datetime.now(
                pytz.timezone(tz)).strftime("%d %B, %Y at %I:%M:%S %p %Z")
            doc.append(NE("\n"))
            doc.append((
                NE(fr"\tiny{{(Document prepared on {retrieval_date})}}")))

        # Create folder to store images, if any
        if not filepath:
            raise InvalidFilePathException(
                "File path is not specified. Please provide a valid file path "
                "to save the generated PDF document."
            )
        file_path = Path(filepath)
        if file_path.suffix.lower() == ".pdf":
            file_path = file_path.with_suffix("")
        curr_dir = os.getcwd()
        try:
            os.chdir(str(self.ctx.working_dir))
            doc.generate_pdf(str(file_path), clean=clean, clean_tex=clean_tex)
        finally:
            os.chdir(curr_dir)
