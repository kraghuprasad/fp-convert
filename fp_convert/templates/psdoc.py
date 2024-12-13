# trunk-ignore-all(isort)
#!/usr/bin/env python

import os
import re
import shutil
from pathlib import Path
from typing import Optional, List
from cairosvg import svg2pdf

from freeplane import Mindmap, Node
from peek import peek
from pylatex.section import (
    Section,
    Subsection,
    Subsubsection,
    Paragraph,
    Subparagraph,
)
from pylatex import (
    Command,
    Document,
    Figure,
    Foot,
    Head,
    Itemize,
    Label,
    MdFramed,
    Package,
    PageStyle,
    Tabular,
)
from pylatex.utils import bold
from pylatex.utils import NoEscape as NE
from pylatex.base_classes import LatexObject

from fp_convert import FPDoc
from fp_convert.errors import (
    IncorrectInitialization,
    InvalidRefException,
    MaximumListDepthException,
    MissingFileException,
    UnsupportedFileException,
)
from fp_convert.utils.helpers import DocInfo, get_label, retrieve_note_lines
from fp_convert.utils.decorators import track_processed_nodes

"""
Following classes specify the default values for various parameters of Program
Specifications Document (PSD).
It is possible to construct and reconfigure them, before constructing the PSD
template. Then those reconfigured classes can be supplied to the constructor of
the template.
"""


class Config:
    """
    Following controls the document-specific configuration parameters.
    """

    toc_depth = 3  # Maximum depth required for the table of contents listing
    sec_depth = 5  # Maximum depth allowed while sectioning this document
    par_title_format = (
        r"[hang]{\normalfont\normalsize\bfseries}{\theparagraph}{1em}{}"  # noqa
    )
    par_title_spacing = r"{0pt}{3.25ex plus 1ex minus .2ex}{.75em}"
    subpar_title_format = (
        r"[hang]{\normalfont\normalsize\bfseries}{\thesubparagraph}{1em}{}"  # noqa
    )
    subpar_title_spacing = r"{0pt}{3.25ex plus 1ex minus .2ex}{.75em}"
    sf_outer_line_width = "1pt"  # Stop-Frame outer line-width size
    sf_round_corner_size = "3pt"  # Stop-Frame rounded corner's size
    sf_outer_left_margin = "5pt"  # Stop-Frame outer left margin width
    sf_inner_left_margin = "5pt"  # Stop-Frame inner left margin width
    sf_outer_right_margin = "5pt"  # Stop-Frame outer right margin width
    sf_inner_right_margin = "5pt"  # Stop-Frame inner right margin width
    header_thickness = "0.4"  # Header line thickness
    footer_thickness = "0.4"  # Footer line thickness
    figure_width = r"0.6\textwidth"  # Width of the figure, in LaTeX


class Geometry:
    """
    Following attributes define various geometry specific parameters of the
    page.
    """

    left_margin = "1.25in"
    inner_margin = "1.25in"  # Applicable only in twosided mode
    right_margin = "1.25in"
    outer_margin = "1.25in"  # Applicable only in twosided mode
    top_margin = "1.5in"
    bottom_margin = "1.5in"
    head_height = "20pt"
    par_indent = "0pt"
    l_header_image_height = "0.8cm"
    c_header_image_height = "0.5cm"
    r_header_image_height = "0.5cm"
    l_footer_image_height = "0.5cm"
    c_footer_image_height = "0.6cm"
    r_footer_image_height = "0.5cm"


class Table:
    """
    Following colors are defined for the default tables laid out in PSD.
    """

    header_color = ("burlywood",)
    rowcolor_1 = "gray!25"
    rowcolor_2 = "white"
    line_color = "red"


class Colours:
    """
    Following colours are defined for styling the PSD.
    """

    header_line_color = "red"
    footer_line_color = "red"
    # link_color = "{rgb}{0.63, 0.79, 0.95}"
    link_color = "gray"
    url_color = "cyan"
    file_color = "magenta"
    mc_color = "{rgb}{0,0.5,0}"  # Colour of margin comments
    sf_line_color = "red"  # Stop-Frame line-color
    sf_background_color = "red!5!white"  # Stop-Frame background-color


class Theme:
    """
    A class to hold the overall theme of the document.
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        geometry: Optional[Geometry] = None,
        table: Optional[Table] = None,
        colours: Optional[Colours] = None,
    ):
        # Use default values of respective paramaters, if supplied ones
        # are None.
        self.config = config if config else Config()
        self.geometry = geometry if geometry else Geometry()
        self.table = table if table else Table()
        self.colours = colours if colours else Colours()


class PSDoc(FPDoc):
    """
    It defines the parameters required to generate a project specifications
    document.
    """

    # Reference patterns which match %ref%, and %refN% in mindmap-text where
    # N is a number. These are used in the node as well as in their note-texts
    # whenever a reference is needed to another node via an arrow-links.
    ref_pat = re.compile("%(ref[0-9]*)%")

    def __init__(
        self,
        mm_file: str|Path,
        documentclass: str = "article",
        working_dir: Optional[str|Path] = ".",
        docinfo: Optional[DocInfo] = None,
        theme: Optional[Theme] = None,
        lmodern: bool = False,
    ):
        """
        The argument mm_file should be a path to a Freeplane Mindmap file.
        The argument docinfo should be a DocInfo object, containing the details
        of the document being generated. Either mm_file, or docinfo must be
        supplied. If a mindmap file path is given, then corresponding DocInfo
        is created automatically. Otherwise precreated DocInfo object is
        required, which in turn was initialized with a mindmap.  It takes the
        theme as its argument to construct the PSD template.  It is possible to
        build a Theme object separately and supply that instead of using the
        default theme provided by this template.

        :param mm_file: A string containing the path to a Freeplane Mindmap
            file. It is a mandatory argument.
        :param docinfo: A DocInfo object, containing the document related
            information. If it is supplied, it would override the one obtained
            from the supplied mindmap's root node.
        :param theme: A Theme instance that defines document styling including
            page geometry, colors, and other formatting parameters.
            constructing the document. The styles, geometry of the page,
            colors etc. are defined in this class. If none is supplied, then
            default values are used.
        :param lmodern: A boolean indicating whether to use Latin Modern
            fonts in the resultant LaTeX document. Default value of it is
            False.
        """
        super().__init__(
            Path(mm_file).stem,
            documentclass=documentclass,
            lmodern=lmodern)

        # If user-supplied theme is absent, use default one
        self.theme = theme if theme else Theme()

        self.mm_file = Path(mm_file)
        self.working_dir = Path(working_dir)
        self.images_dir = Path(working_dir, "images")
        self.mm = Mindmap(self.mm_file)
        if docinfo:
            if not isinstance(docinfo, DocInfo):
                raise IncorrectInitialization(
                    "Supplied argument 'docinfo' is not an instance of"
                    "DocInfo class")
            self.docinfo = docinfo
        elif self.mm.rootnode.notes:
            self.docinfo = DocInfo(self.mm.rootnode.notes)
        else:
            raise IncorrectInitialization(
                "No document-information found in the mindmap supplied."
            )

        self.packages = (
            ("geometry", tuple()),
            ("amssymb", tuple()),
            ("xcolor", ("dvipsnames", "table")),
            ("tcolorbox", ("most",)),
            ("placeins", ("section",)),
            ("titlesec", tuple()),
            ("xspace", tuple()),
            ("fontenc", ("T1",)),
            ("hyperref", tuple()),
            ("mdframed", ("framemethod=TikZ",)),
            ("ragged2e", ("raggedrightboxes",)),
            ("roboto", ("sfdefault",)),
        )

        self.preambletexts = (
            NE(rf"\setcounter{{secnumdepth}}{{{self.theme.config.sec_depth}}}"),
            NE(rf"\setcounter{{tocdepth}}{{{self.theme.config.toc_depth}}}"),
            NE(rf"\setlength{{\parindent}}{{{self.theme.geometry.par_indent}}}"),
            NE(rf"\titleformat{{\paragraph}}{self.theme.config.par_title_format}"),
            NE(
                rf"\titlespacing*{{\paragraph}}{self.theme.config.par_title_spacing}"
            ),  # noqa
            NE(
                rf"\titleformat{{\subparagraph}}{self.theme.config.subpar_title_format}"
            ),  # noqa
            NE(
                rf"\titlespacing*{{\subparagraph}}{self.theme.config.subpar_title_spacing}"
            ),  # noqa
            NE(rf"\definecolor{{mccol}}{self.theme.colours.mc_color}"),
            NE(
                r"\newcommand\margincomment[1]{\RaggedRight{"
                r"\marginpar{\hsize1.7in\tiny\color{mccol}{#1}}}}"
            ),
            NE(
                r"\mdfdefinestyle{StopFrame}{linecolor="
                rf"{self.theme.colours.sf_line_color}, outerlinewidth="
                rf"{self.theme.config.sf_outer_line_width}, "
                rf"roundcorner={self.theme.config.sf_round_corner_size},"
                rf"rightmargin={self.theme.config.sf_outer_right_margin},"
                rf"innerrightmargin={self.theme.config.sf_inner_right_margin},"
                rf"leftmargin={self.theme.config.sf_outer_left_margin},"
                rf"innerleftmargin={self.theme.config.sf_inner_left_margin},"
                rf"backgroundcolor={self.theme.colours.sf_background_color}}}"
            ),
            NE(
                fr"""
\hypersetup{{
pdftitle={{{self.docinfo["doc_title"]}}},
pdfsubject={{{self.docinfo["doc_title"]}}},
pdfauthor={{{self.docinfo["doc_author"]}}},
pdfcreator={{"fp-convert using pylatex, freeplane-io, and LaTeX with hyperref"}},
%pdfpagemode=FullScreen,
colorlinks=true,
linkcolor={self.theme.colours.link_color},
filecolor={self.theme.colours.file_color},
urlcolor={self.theme.colours.url_color}
}}"""
            ),
            # Setting headheight
            NE(rf"\setlength\headheight{{{self.theme.geometry.head_height}}}"),
            # Styling the geometry of the document
            #
            NE(
                rf"""
\geometry{{
a4paper,
%total={{170mm,257mm}},
left={self.theme.geometry.left_margin},
inner={self.theme.geometry.inner_margin},
right={self.theme.geometry.right_margin},
outer={self.theme.geometry.outer_margin},
top={self.theme.geometry.top_margin},
bottom={self.theme.geometry.bottom_margin},
}}"""
            ),
            NE(
                rf"""
\rowcolors{{2}}%
{{{self.theme.table.rowcolor_1}}}%
{{{self.theme.table.rowcolor_2}}}%
"""
            ),
        )  # End of the tuple named preambletexts

        self.colors = (
            ("burlywood", "HTML", "DEB887"),
        )

    def fetch_notes_elements(self, node: Node):
        """
        Fetches the notes-section of the supplied node, and returns a list of
        suitable LaTeX objects containing the content of the notes-section.
        The returned content is built by processing (expanding) any macros that
        are present in the notes.

        Parameters
        ----------
        node : Node
            The node from which notes are to be collected.

        Returns
        -------
        List[LatexObject]
            A list of LaTeX objects (paragraph, framed box, or similar)
            obtained from the notes-section of the node. The content is built
            after all macros in the notes are expanded.
        """
        ret = list()
        if node.notes:
            # If stop-sign is present, then style a framed box accordingly
            if node.icons and "stop-sign" in node.icons:
                # segment.append(MdFramed(em(str(node.notes), node), options="style=StopFrame"))
                mdf = MdFramed()
                mdf.options = "style=StopFrame"
                #lines = self.expand_macros(str(node.notes), node)
                lines = retrieve_note_lines(str(node.notes))
                for line in lines:
                    #mdf.append(fr"\small{{{line}}}")
                    for item in self.expand_macros(line, node):
                        mdf.append(Command("small", item))
                ret.append(mdf)
            else:
                text_lines = retrieve_note_lines(node.notes)
                for line in text_lines:
                    for item in self.expand_macros(line, node):
                        ret.append(item)
                    ret.append(Command("par"))
        return ret

    def expand_macros(self, text: str, node: Node):
        """
        Function to expand macros to get applicable reference-details.
        It is usually used to retrieve the reference-links from supplied node,
        and patch it in the returned content.

        Parameters
        ----------
        text : str
            The text from which the macros are to be extracted as well as
            expanded.
        node : Node
            The current node which would be searched to identify other nodes
            to which it refers to.

        Returns
        -------
        list[LatexObject]
            A list of LaTeX objects representing the content after expanding the
            macros.
        """
        ret = list()
        segments = re.split(PSDoc.ref_pat, text)

        if len(segments) > 1:  # References are present in the supplied text
            refs = dict()
            if node.arrowlinks:
                for idx, node_to in enumerate(node.arrowlinks):
                    #refs[f"%ref{idx+1}%"] = rf"\autoref{{{get_label(node_to.id)}}}"
                    refs[f"ref{idx+1}"] = Command("autoref", get_label(node_to.id))
            else:
                raise InvalidRefException(
                    f"Node [{str(node)}(ID: {node.id})] without any"
                    "outgoing arrow-link is using a node-reference in its text"
                    "or notes."
                )

            if len(refs) == 1:
                for segment in segments:
                    if not re.fullmatch(PSDoc.ref_pat, f"%{segment}%"):
                        ret.append(segment)
                    else:
                        if segment in {"ref", "ref1"}:
                            ret.append(refs["ref1"])
                            ret.append(Command("xspace"))
                        else:
                            raise InvalidRefException(
                                f"Node [{str(node)}(ID: {node.id})] with"
                                "single outgoing arrow-link is using a"
                                "node-reference index more than 1"
                                f"({segment}) in its text or notes."
                            )
            else:  # Multiple outgoing arrow-links are present
                for segment in segments:
                    if not re.fullmatch(PSDoc.ref_pat, segment):
                        ret.append(segment)
                    else:
                        try:
                            ret.append(refs[segment])
                            ret.append(Command("xspace"))
                        except KeyError:
                            # trunk-ignore(ruff/B904)
                            raise InvalidRefException(
                                f"Node [{str(node)}(ID: {node.id})] with"
                                "multiple outgoing arrow-links is using an"
                                f"invalid node-reference ({segment}) in its"
                                "text or notes."
                            )

            # Add a label to this node for back reference
            ret.append(NE(rf"\label{{R{get_label(node.id)}}}"))

        else:  # No references are present in the supplied text
            ret.append(segments[0])

        return ret

    def get_absolute_file_path(self, file_path: str|Path):
        """
        Fetch absolute file path - if file exists - if a file path relative to
        the mindmap file is provided.

        Parameters:
            file_path: str|Path
        """
        if not Path(file_path).is_absolute():
            # The path could be relative to the folder having mindmap file
            abs_path = Path(self.mm_file.parent.absolute(), file_path)

        if not abs_path.is_file():
            raise MissingFileException(
                f"A required file ({file_path}) is missing. Either use an"
                "absolute file path, or a path relative to the mindmap"
                "itself. Also the file must exist already."
            )
        return abs_path


    def build_latex_figure(self, node: Node):
        """
        Build a center-aligned LaTeX figure object from the content of the
        supplied node.

        Parameters
        ----------
        node : Node
            The node of the mindmap from which the figure is to be built.

        Returns
        -------
        list[LatexObject]
            A list of LaTeX objects like image, caption, etc. representing
            the content obtained from the supplied node.
        """
        if not node.imagepath:  # No imagepath found
            return NE("")

        img_path = self.get_absolute_file_path(Path(node.imagepath))

        ret = list()
        f_ext = img_path.suffix.lower()
        if f_ext == ".svg":  # SVG images need conversion to PDF
            if not self.images_dir.is_dir():
                os.makedirs(self.images_dir, exist_ok=True)
            new_img_path = Path(self.images_dir, img_path.stem, ".pdf")
            # Convert SVG image to PDF
            svg2pdf(url=img_path, write_to=new_img_path)

        # Other images must be either of type JPEG, or PNG only
        elif f_ext not in {".jpg", ".png", ".jpeg"}:
            raise UnsupportedFileException(
                f"File {node.imagepath} is not of type embeddable to PDF"
                 "document. Please use an image file of type JPG, PNG, or SVG."
            )
        else:  # Use original absolute image path
            new_img_path = img_path

        fig = Figure(position="!htb")
        fig.append(
            NE(
                fr"""
\begin{{center}}%
\tcbox{{\includegraphics[%
width={self.theme.config.figure_width}]{{{new_img_path}}}}}%
\end{{center}}%"""
            )
        )  # Build a boxed figure
        fig.add_caption(str(node))
        fig.append(NE(rf"\label{{{get_label(node.id)}}}"))
        ret.append(fig)

        # Add back references, if this node is being pointed to by other nodes
        # of the mindmap.
        for referrer in node.arrowlinked:
            ret.append(
                NE(
                    rf"""
\margincomment{{\tiny{{$\Lsh$ \autoref{{R{get_label(referrer.id)}}}}}%
\newline}}%
"""
                )
            )  # Add a margin comment
        return ret

    def build_table_and_notelist(self, node: Node):
        """
        Build a list of LatexObjects suitable for building a LaTeX table and
        the list of notes associated with the supplied node.

        """
        if node.children:
            col1 = dict()  # Collection of table-data
            notes = list()  # Collection of notes (if they exist)

            for field in node.children:
                if field:
                    # peek(f"Field is {field}")
                    # doc.processed_nodes.add(field.id)
                    col1[str(field)] = {
                        str.strip(
                            str(d).split(":")[0]): str.strip(
                                str(d).split(":")[1])
                        for d in field.children
                    }
                    if field.notes:
                        note_lines = retrieve_note_lines(field.notes)
                        field_notes = list()
                        for line in note_lines:
                            line_blocks = list()
                            for item in self.expand_macros(line, field):
                                line_blocks.append(item)
                            field_notes.append(line_blocks)
                        notes.append((field, field_notes))

            col_hdrs = sorted(list({e for d in col1.values() for e in d.keys()}))

            # Build table-content first
            tab = Tabular("l" * (1 + len(col_hdrs)), pos="c")
            # tab.add_caption(node, label=get_label("TAB:", node.id))
            tab.add_hline(color=self.theme.table.line_color)
            row = [NE(f"{bold(node)}"),]
            row.extend([bold(hdr) for hdr in col_hdrs])
            tab.add_row(*row, color=self.theme.table.header_color, strict=True)
            tab.add_hline(color=self.theme.table.line_color)
            for field in sorted(col1.keys()):
                row = [field, ]
                for col in col_hdrs:
                    row.append(col1[field].get(col, ""))
                tab.add_row(row)
            tab.add_hline(color=self.theme.table.line_color)

            # Then check if notes are to be collected for the same node
            if notes:
                return [tab, notes]
            return [tab, ]
        # Empty list is returned by default, if nothing else is there
        return list()

    def build_table_from_child_nodes(self, node: Node):
        tab_notes = self.build_table_and_notelist(node)
        ret = list()
        if len(tab_notes) >= 1:
            ret.append(NE(r"\begin{center}"))  # Center align
            ret.append(tab_notes[0])
            ret.append(NE(r"\end{center}"))
            if len(tab_notes) > 1:  # Note-text is to be rendered
                itmz = Itemize()
                # peek(tab_notes[1:])
                for h, c in tab_notes[1]:
                    # peek(f"Header: {h}")
                    # peek(f"Content: {c}")
                    if len(c) == 1:  # Single line note is to be rendered
                        itmz.add_item(NE(f"{bold(h)}: "))
                        for i in c[0]:
                            itmz.append(i)
                    else:  # Multiline notes are rendered as unordered list
                        itmz.add_item(NE(f"{bold(h)}:\n"))
                        item = Itemize()
                        for i in c:
                            item.append(Command("item"))
                            for j in i:
                                item.append(j)
                        itmz.append(item)
                ret.append(itmz)
        return ret

    def build_stop_notes(self, node: Node):
        """
        Build a stop-note block in LaTeX and return it.
        """
        mdf = MdFramed()
        mdf.options = "style=StopFrame"
        note_lines = retrieve_note_lines(node.notes)
        items = self.expand_macros(note_lines[0], node)
        for item in items:
            #mdf.append(NE(fr"\small{{{item}}}"))
            mdf.append(Command("small", item))
        for line in note_lines[1:]:
            mdf.append("\n")
            for item in self.expand_macros(line, node):
                #mdf.append(NE(fr"\small{{{line}}}"))
                mdf.append(Command("small", item))
        return mdf

    @track_processed_nodes
    def build_verbatim_list(self, node: Node):
        """
        Build a non-nested list of parts with the contents of the children
        printed in verbatim mode.
        """
        if node.children:
            itmz = Itemize()
            for child in node.children:
                p = ""
                # If no notes are present, then item-element should start with
                # [] to avoid bullets
                if child.notes:
                    # Print notes first, above the verbatim text
                    lines = self.expand_macros(str(child.notes), child)
                    for line in lines:
                        p = f"{p}%\n{line}"

                    # Now print the verbatim text contained in that node
                    p = f"{p}%\n\\begin{{verbatim}}\n{str(child)}\n\\end{{verbatim}}"
                    #p = f"{p}%\n{str(child)}"
                    #lines = str(child).split("\n")
                    #for line in lines:
                    #    p = f"{p}%\n{line}"
                    #p = f"{p}%\n\\end{{verbatim}}"
                    #p += "\n\\begin{verbatim}" + \
                    #    self.expand_macros(str(child), child) + \
                    #    '\\end{verbatim}'
                else:
                    # To avoid bullet, starting the item with []
                    #p += '[]\\begin{verbatim}' + str(child) + '\\end{verbatim}'
                    p = f"{p}%\n[]\\begin{{verbatim}}\n{str(child)}\\end{{verbatim}}"

                # Add back references, if this node is being pointed to by other
                # nodes (sinks for arrows)
                for referrer in node.arrowlinked:
                    p += NE(
                        fr"\margincomment{{\tiny{{$\Lsh$ \autoref{{{get_label(
                            referrer.id)}}}}}}}")

                itmz.add_item(NE(p))
            return [itmz,]
        return list()

    #@track_processed_nodes
    def build_list_recursively(self, node: Node, level: int):
        """
        Build and return a list of lists as long as child nodes are present
        in the supplied node.
        """
        if level == 4:
            raise MaximumListDepthException("Maximum depth of list reached.")

        if node.children:
            itmz =  Itemize()
            for child in node.children:
                # For the purpose of debugging only
                #peek("  "*level, f"[{child.id}]", child)
                #peek("  "*level, f"[imagepath]", child.imagepath)
                #peek("  "*level, f"[icons]", child.icons)
                content = str(child).split(":", 1)
                if len(content) == 2:
                    itmz.add_item(NE(f"{bold(content[0])}: "))
                    texts = self.expand_macros(content[1], child)
                    for text in texts:
                        itmz.append(text)
                else:
                    texts = self.expand_macros(str(child), child)
                    itmz.add_item(texts[0])
                    for text in texts[1:]:
                        itmz.append(text)

                # If notes exists in supplied node, then include it too
                if child.notes:
                    if child.icons and "stop-sign" in child.icons:
                        itmz.append(self.build_stop_notes(child))
                    else:
                        note_lines = retrieve_note_lines(child.notes)
                        for line in note_lines:
                            itmz.append(Command("par"))
                            for item in self.expand_macros(line, child):
                                itmz.append(item)

                # Add a label so that other nodes can refer to it.
                #p = p + NE(r"\label{" + get_label(child.id) + "}")
                #p.append(NE(fr"\label{{{get_label(child.id)}}}"))
                itmz.append(Command("label", get_label(child.id)))

                # Add back references, if this node is being pointed to
                # by other nodes (sinks for arrows)
                for referrer in child.arrowlinked:
                    #referrer_block = NE(r"\margincomment{\tiny{$\Lsh$ \autoref{" + get_label(referrer.id) + "}}}")
                    itmz.append(NE(
                        fr"\margincomment{{\tiny{{$\Lsh$ \autoref{{{get_label(
                            referrer.id)}}}}}}}"))

                if child.children:
                    if child.icons and 'links/file/generic' in child.icons:  # Table is to be built
                        for obj in self.build_table_from_child_nodes(child):
                            itmz.append(obj)

                    # Else check if children should be formatted verbatim
                    elif 'links/file/json' in child.icons or \
                    'links/file/xml' in child.icons or \
                    'links/file/html' in child.icons:
                        for item in self.build_verbatim_list(child):
                            itmz.append(item)

                    # Expecting a plain list, or list of list, or listof lists ...
                    else:
                        item = self.build_list_recursively(child, level+1)
                        itmz.append(item)
            return itmz
        return None

    @track_processed_nodes
    def traverse_children(
        self, node: Node, level: int, blocks: List[LatexObject]
    ):
        """
        Traverse the node-tree and build document sections based on node depth.

        This function recursively traverses a node-tree, creating LaTeX sections,
        subsections, and other document elements based on the node depth.
        It handles:
        - Creating sections up to 5 levels deep (section to subparagraph)
        - Adding labels for cross-referencing
        - Processing node notes and appending them to sections
        - Handling images marked with 'image' icon

        Parameters
        ----------
        node : Node
            The current freeplane node being processed
        level : int
            The current depth in the node tree (determines section levels)
        blocks : List[LatexObject]
            A list containing the instances of LatexObject to be used to
            build the document.
        """
        stop_traversing = False  # Flag to stop traversing the node tree
        if node:
            # For the purpose of debugging only
            #peek("  " * level, f"[{node.id}]", node)
            #if node.imagepath:
            #    peek("  " * level, f"[{node.id}]", node.imagepath)
            #if node.icons:
            #    peek("  " * level, f"[{node.id}]", node.icons)

            if level == 1:
                blocks.append(Section(str(node), label=Label(get_label(node.id))))
                #blocks.append(Section(str(node)))
            elif level == 2:
                blocks.append(Subsection(str(node), label=Label(get_label(node.id))))
                #blocks.append(Subsection(str(node)))
            elif level == 3:
                blocks.append(Subsubsection(str(node), label=Label(get_label(node.id))))
                #blocks.append(Subsubsection(str(node)))
            elif level == 4:
                blocks.append(Paragraph(str(node), label=Label(get_label(node.id))))
                #blocks.append(Paragraph(str(node)))
            elif level == 5:
                blocks.append(
                    Subparagraph(NE(f"{node}"), label=Label(get_label(node.id)))
                )
                #blocks.append(Subparagraph(str(node)))
            else:
                # Now ignore all nodes beyond subparagraph (level=5).
                # One more level (Subsubparagraph) is possible to be used but
                # not using at present.
                return

            notes_elements = self.fetch_notes_elements(node)
            blocks.extend(notes_elements)

            # Build LaTeX image, if icon of the node indicates that
            if node.icons and "image" in node.icons:
                fig = self.build_latex_figure(node)
                if fig:
                    blocks.extend(fig)

            if node.children:  # Non-section specific things are handled here
                # If a list is to be built from node and its children
                if node.icons and "list" in node.icons:
                    blocks.append(self.build_list_recursively(node, 1))
                    stop_traversing = True  # No more section processing needed

                # If a table is to be built from the node and its children
                elif node.icons and "links/file/generic" in node.icons:
                    tab = self.build_table_from_child_nodes(node)
                    if tab:
                        blocks.extend(tab)
                    stop_traversing = True  # No more section processing needed

                # If some verbatim block is to be build for node's children
                elif node.icons and (
                    "links/file/json" in node.icons
                    or "links/file/xml" in node.icons
                    or "links/file/html" in node.icons):
                    blocks.extend(self.build_verbatim_list(node))
                # Remaining children of the node get processed in next
                # recursive iteration of this method where sections and
                # subsections etc. are getting built.

            if (
                stop_traversing
            ):  # No more section-level processing is required
                return

            # Recurse for all child nodes of this node for section level
            # processing
            for child in node.children:
                self.traverse_children(child, level + 1, blocks)

        return list()  # If no valid node is supplied, do nothing


    def build_headers_and_footers(self):
        """
        Creates fancy header/footers for the pages.

        Parameters: None
        """
        headfoot = PageStyle(
            "header",
            header_thickness=self.theme.config.header_thickness,
            footer_thickness=self.theme.config.footer_thickness,
            data=NE(
                rf"""
\renewcommand{{\headrule}}{{\color{{{self.theme.colours.header_line_color }}}\hrule width \headwidth height \headrulewidth}}
\renewcommand{{\footrule}}{{\color{{{self.theme.colours.footer_line_color}}}\hrule width \headwidth height \footrulewidth}}"""
            ),
        )

        lheader, cheader, rheader, lfooter, cfooter, rfooter = \
            (None for i in range(6))

        if self.docinfo.get("l_header_image", None):
            lheader = NE(
                rf"""
\includegraphics[%
height={self.theme.geometry.l_header_image_height}]%
{{{self.get_absolute_file_path(self.docinfo['l_header_image'])}}}"""
            )
        elif self.docinfo.get("l_header_text", None):
            lheader = NE(rf"{self.docinfo['l_header_text']}")
        if lheader:
            with headfoot.create(Head("L")):
                headfoot.append(lheader)

        if self.docinfo.get("c_header_image", None):
            cheader = NE(
                rf"""
\includegraphics[%
height={self.theme.geometry.c_header_image_height}]%
{{{self.get_absolute_file_path(self.docinfo['c_header_image'])}}}"""
            )
        elif self.docinfo.get("c_header_text", None):
            cheader = NE(rf"{self.docinfo['c_header_text']}")
        if cheader:
            with headfoot.create(Head("C")):
                headfoot.append(cheader)

        if self.docinfo.get("r_header_image", None):
            rheader = NE(
                rf"""
\includegraphics[%
height={self.theme.geometry.r_header_image_height}]%
{{{self.get_absolute_file_path(self.docinfo['r_header_image'])}}}"""
            )
        elif self.docinfo.get("r_header_text", None):
            rheader = NE(rf"{self.docinfo['r_header_text']}")
        if rheader:
            with headfoot.create(Head("R")):
                headfoot.append(rheader)

        if self.docinfo.get("l_footer_image", None):
            lfooter = NE(
                rf"""
\includegraphics[%
height={self.theme.geometry.l_footer_image_height}]%
{{{self.get_absolute_file_path(self.docinfo['l_footer_image'])}}}"""
            )
        elif self.docinfo.get("l_footer_text", None):
            lfooter = NE(rf"{self.docinfo['l_footer_text']}")
        if lfooter:
            with headfoot.create(Foot("L", data=Command("normalcolor"))):
                headfoot.append(lfooter)

        if self.docinfo.get("c_footer_image", None):
            cfooter = NE(
                rf"""
\includegraphics[%
height={self.theme.geometry.c_footer_image_height}]%
{{{self.get_absolute_file_path(self.docinfo['c_footer_image'])}}}"""
            )
        elif self.docinfo.get("c_footer_text", None):
            cfooter = NE(rf"{self.docinfo['c_footer_text']}")
        if cfooter:
            with headfoot.create(Foot("C", data=Command("normalcolor"))):
                headfoot.append(cfooter)

        if self.docinfo.get("r_footer_image", None):
            rfooter = NE(
                rf"""
\includegraphics[%
height={self.theme.geometry.r_footer_image_height}]%
{{{self.get_absolute_file_path(self.docinfo['r_footer_image'])}}}"""
            )
        elif self.docinfo.get("r_footer_text", None):
            rfooter = NE(rf"{self.docinfo['r_footer_text']}")
        if rfooter:
            with headfoot.create(Foot("R", data=Command("normalcolor"))):
                headfoot.append(rfooter)

        return headfoot


    def generate_pdf(
        self, output_file_path,
        clean: Optional[bool]=True, clean_tex: Optional[bool]=True):
        """
        Generate PDF document from the supplied content of the mindmap.

        Parameters
        ----------
        output_file : str
            The file name (with path if required) to which the generated PDF
            is to be saved.
        """

        # Create a LaTeX Document object and start using it to add content
        doc = Document()

        for item in self.packages:  # Populate default preamble-items
            doc.packages.append(Package(item[0], options=item[1]))

        for item in self.preambletexts:  # Populate default preamble-items
            doc.preamble.append(item)

        for color in self.colors:
            doc.add_color(color[0], color[1], color[2])

        if self.docinfo.get("doc_version", None):
            title_and_version = rf"{self.docinfo["doc_title"]}\newline\small{{(Version {self.docinfo["doc_version"]})}}"
        else:
            title_and_version = rf"{self.docinfo["doc_title"]}"
        doc.preamble.append(Command("title", NE(title_and_version)))

        if self.docinfo.get("doc_author", None):
            author = self.docinfo["doc_author"]
            doc.preamble.append(Command("author", author))

        if self.docinfo.get("doc_date", None):
            date = self.docinfo["doc_date"]
        else:
            date = NE(r"\today")
        doc.preamble.append(Command("date", date))

        headfoot = self.build_headers_and_footers()
        doc.preamble.append(headfoot)
        doc.change_document_style("header")

        doc.append(NE(r"\maketitle"))
        doc.append(NE(r"\tableofcontents"))
        doc.append(NE(r"\newpage"))
        doc.append(NE(r"\justify"))


        # Then populate mindmap-specific preamble-items
        #doc.preamble.append(Command("title", self.docinfo["doc_title"]))
        #doc.preamble.append(Command("author", self.docinfo["doc_author"]))
        #doc.preamble.append(Command("date", self.docinfo["doc_date"]))
                # Create a list to hold the instances of LatexObject built using the
        # content of the mindmap.
        blocks = list()
        for child in self.mm.rootnode.children:
            self.traverse_children(child, 1, blocks)

        for obj in blocks:
            doc.append(obj)

        # Create folder to store images, if any
        peek(output_file_path)
        file_path = Path(output_file_path)
        if file_path.suffix.lower() == ".pdf":
            file_path = file_path.with_suffix("")
        curr_dir = os.getcwd()
        os.chdir(self.working_dir)
        doc.generate_pdf(file_path, clean=clean, clean_tex=clean_tex)
        os.chdir(curr_dir)
