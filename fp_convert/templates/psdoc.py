#!/usr/bin/env python
import os
import re
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

import pytz
import yaml
from cairosvg import svg2pdf
from freeplane import Mindmap, Node

#from peek import peek
from pylatex import (
    Center,
    Command,
    Document,
    Enumerate,
    Figure,
    Foot,
    Head,
    HugeText,
    Itemize,
    Label,
    LongTable,
    MdFramed,
    MiniPage,
    MultiColumn,
    Package,
    PageStyle,
    Tabular,
    Tabularx,
    VerticalSpace,
)
from pylatex.base_classes import LatexObject
from pylatex.section import Paragraph, Section, Subparagraph, Subsection, Subsubsection
from pylatex.utils import NoEscape as NE
from pylatex.utils import bold
from pylatex.utils import escape_latex as EL
from pylatex.utils import italic, verbatim

from fp_convert import FPDoc
from fp_convert.errors import (
    IncorrectInitialization,
    InvalidNodeException,
    InvalidParameterException,
    InvalidRefException,
    InvalidRefTypeException,
    InvalidTypeException,
    MaximumListDepthException,
    MaximumSectionDepthException,
    MissingHeaderException,
    MissingValueException,
    UnsupportedFileException,
)
from fp_convert.utils.decorators import track_processed_nodes
from fp_convert.utils.helpers import (
    DBTable,
    DBTableField,
    DocInfo,
    get_label,
    retrieve_note_lines,
    special_truncator_factory,
)

# Create truncator functions for strings with limited size
trunc80 = special_truncator_factory(80)
trunc32 = special_truncator_factory(32)
trunc18 = special_truncator_factory(18)

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
    sf_inner_left_margin = "10pt"  # Stop-Frame inner left margin width
    sf_outer_right_margin = "5pt"  # Stop-Frame outer right margin width
    sf_inner_right_margin = "30pt"  # Stop-Frame inner right margin width
    header_thickness = "0.4"  # Header line thickness
    footer_thickness = "0.4"  # Footer line thickness
    figure_width = r"0.6\textwidth"  # Width of the figure, in LaTeX
    new_mark_text = "NEW"  # Text marking newly added nodes
    new_mark_flag = r"\faPlus"  # FontAwesome icon for new-markings
    del_mark_text = "CUT"  # Text marking nodes for removal
    del_mark_flag = r"\faCut"  # FontAwesome icon for del-markings
    timezone = "UTC"  # Timezone for all timestamps used in the document


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

    # Vertical space between top logo and title-text in the title page
    tp_top_logo_vspace = "5cm"
    tp_top_logo_height = "3cm"  # Height of top logo on title page

    # Vertical space between bottom logo and title-text in the title page
    tp_bottom_logo_vspace = "7cm"
    tp_bottom_logo_height = "1.5cm"  # Height of bottom logo on title page

    l_header_image_height = "0.7cm"
    c_header_image_height = "0.5cm"
    r_header_image_height = "0.5cm"
    l_footer_image_height = "0.5cm"
    c_footer_image_height = "0.5cm"
    r_footer_image_height = "0.5cm"

class Table:
    """
    Following colors are defined for the default tables laid out in PSD.
    """
    header_text_color = "darkblue"
    header_row_color = "babyblueeyes!80"
    footer_row_color = "babyblueeyes!10"
    rowcolor_1 = "babyblueeyes!35"
    rowcolor_2 = "babyblueeyes!20"
    line_color = "cornflowerblue"

class DataTable:
    """
    Following colors are defined for the database tables laid out in PSD.
    """
    tab1_header_row_color = "spirodiscoball!20!white"
    tab1_header_line_color = "fpcblue2"
    tab1_header_text_color = "darkblue"
    tab1_body_line_color = "gray!30"
    tab2_header_row_color = "fpcblue1"
    tab2_header_line_color = "fpcblue2"
    tab2_header_text_color = "darkblue"
    tab2_rowcolor_1 = "white"
    tab2_rowcolor_2 = "tealblue!7!white"

class Colors:
    """
    Following colors are defined for styling the PSD.
    """
    header_line_color = "airforceblue"
    footer_line_color = "airforceblue"
    link_color = "celestialblue"
    url_color = "ceruleanblue"
    file_color = "magenta"
    mc_color = "{rgb}{0,0.5,0}"  # Color of margin comments
    sf_line_color = "cadmiumred"  # Stop-Frame line-color
    sf_background_color = "red!5!white"  # Stop-Frame background-color
    new_mark_color = "cobalt"  # Color of markers for newly created nodes
    del_mark_color = "red!80!gray"  # Color of markers for nodes marked for deletion


class Theme:
    """
    A class to hold the overall theme of the document.
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        geometry: Optional[Geometry] = None,
        table: Optional[Table] = None,
        datatable: Optional[DataTable] = None,
        colors: Optional[Colors] = None,
    ):
        # Use default values of respective paramaters, if supplied ones
        # are None.
        self.config = config if config else Config()
        self.geometry = geometry if geometry else Geometry()
        self.table = table if table else Table()
        self.datatable = datatable if datatable else DataTable()
        self.colors = colors if colors else Colors()


class Doc(FPDoc):
    """
    It defines the parameters required to generate a project specifications
    document.
    """

    # Reference patterns which match %ref%, and %refN% in mindmap-text where
    # N is a number. These are used in the node as well as in their note-texts
    # whenever a reference is needed to another node via an arrow-links.
    ref_pat = re.compile("(%ref[0-9]*%)")
    param_pat = re.compile("(%[^ %]+%)")

    def __init__(
        self,
        mm_file: str|Path,
        documentclass: str = "article",
        working_dir: Optional[str|Path] = ".",
        docinfo: Optional[DocInfo] = None,
        theme: Optional[Theme] = None,
        font_family: Optional[List] = None,
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
        :font_family: The font-family and its details to be used in the PDF
            document.
        """
        super().__init__(
            Path(mm_file).stem,
            documentclass=documentclass)

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

        # Container to hold colorspecs of colors used in the document
        self.colors = list()

        # Container to hold all nodes for which hypertarget has been made
        self.hypertargets = set()

        # Container to hold nodes with additions and deletions markers
        self.changeset = list()  # List of tuple of change-set nodes and their type
        self.changeset_section = None
        self.changeset_node = None

        self.packages = [
            ("geometry", tuple()),
            ("amssymb", tuple()),
            ("xcolor", ("dvipsnames", "table")),
            ("tcolorbox", ("most",)),
            ("placeins", ("section",)),
            ("titlesec", tuple()),
            ("xspace", tuple()),
            ("fontawesome5", tuple()),
            ("makecell", tuple()),
            ("fontenc", ("OT1",)),
            ("longtable", tuple()),
            ("marginnote", tuple()),
            ("hyperref", tuple()),
            ("multirow", tuple()),
            ("tabularx", tuple()),
            ("enumitem", tuple()),
            ("mdframed", ("framemethod=TikZ",)),
            ("ragged2e", ("raggedrightboxes",)),
#            ("roboto", ("sfdefault",)),
        ]
        if font_family:
            self.packages.append((font_family[0], font_family[1]))
        else:
            self.packages.append(("utopia", tuple()))

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
            NE(rf"\definecolor{{mccol}}{self.theme.colors.mc_color}"),
            NE(
                r"\newcommand\margincomment[1]{\RaggedRight{"
                r"\marginpar{\hsize1.7in\tiny\color{mccol}{#1}}}}"
            ),
            NE(
                r"\mdfdefinestyle{StopFrame}{linecolor="
                rf"{self.regcol(self.theme.colors.sf_line_color)}, outerlinewidth="
                rf"{self.theme.config.sf_outer_line_width}, "
                rf"roundcorner={self.theme.config.sf_round_corner_size},"
                rf"rightmargin={self.theme.config.sf_outer_right_margin},"
                rf"innerrightmargin={self.theme.config.sf_inner_right_margin},"
                rf"leftmargin={self.theme.config.sf_outer_left_margin},"
                rf"innerleftmargin={self.theme.config.sf_inner_left_margin},"
                rf"backgroundcolor={self.theme.colors.sf_background_color}}}"
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
linkcolor={self.regcol(self.theme.colors.link_color)},
filecolor={self.regcol(self.theme.colors.file_color)},
urlcolor={self.regcol(self.theme.colors.url_color)},
pdftoolbar=true,
pdfpagemode=UseNone,
pdfstartview=FitH
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
{{{self.regcol(self.theme.table.rowcolor_1)}}}%
{{{self.regcol(self.theme.table.rowcolor_2)}}}%
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
"""
            ),

        )  # End of the tuple named preambletexts


    def get_hypertarget(self, node: Node):
        """
        Generate the hypertarget for the supplied node.

        Parameters:
            node: Node
                The node for which the hypertarget is to be generated.

        Returns:
            LateXObject
                The hypertarget object generated for the supplied node.
        """
        if node not in self.hypertargets:
            self.hypertargets.add(node)
            return Command("hypertarget", arguments=(get_label(node.id), ""))
        return None

    def get_applicable_flags(self, node: Node):
        """
        Check if node has any applicable flags like for deletion or addition of
        text-blocks or graphical elements etc. and return a list with appropriate
        flags, icons or notes. If no flags are present, then return an empty list.

        Parameters:
            node: Node
                The node whose applicable flags are to be checked and evaluated.

        Returns:
            list[tuple(str, str, int)]
                A list of tuples of the following form:
                (flag-text, flag-type, index-position in the list)
                The last argument indicates the position of the entry in list like
                change-set so that a back reference to it can be included in the document
                at the pertinent location.
        """
        ret = list()

        # Check for deletion flag first and if not found then check for addition
        # as these two cases are mutually exclusive.
        if node.icons:
            if "button_cancel" in node.icons:
                flag = NE(
                    fr"""\textcolor{{{self.regcol(self.theme.colors.del_mark_color)}}}{{%
{{\rotatebox{{10}}{{\tiny{{\textbf{{{self.theme.config.del_mark_text}}}}}}}}}%
{{{self.theme.config.del_mark_flag}}}}}""")

                # Register the node for deletion
                self.changeset.append((node, "D"))
                ret.append((flag, "D", len(self.changeset)-1))

            elif "addition" in node.icons:
                flag = NE(
                    fr"""\textcolor{{{self.regcol(self.theme.colors.new_mark_color)}}}{{%
{{\rotatebox{{10}}{{\tiny{{\textbf{{{self.theme.config.new_mark_text}}}}}}}}}%
{{{self.theme.config.new_mark_flag}}}}}""")

                # Register the node for addition
                self.changeset.append((node, "A"))
                ret.append((flag, "A", len(self.changeset)-1))

        # If required, more flags can be handled here before returning
        return ret

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
                mdf = MdFramed()
                mdf.options = "style=StopFrame"
                lines = retrieve_note_lines(str(node.notes))
                for line in lines:
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
        segments = re.split(Doc.ref_pat, text)

        if len(segments) > 1:  # References are present in the supplied text
            refs = dict()
            if node.arrowlinks:
                for idx, node_to in enumerate(node.arrowlinks):
                    refs[fr"%ref{idx+1}%"] = Command(
                        "hyperlink",
                        arguments=(get_label(node_to.id), trunc32(str(node_to))))
            else:
                raise InvalidRefException(
                    f"Node [{str(node)}(ID: {node.id})] without any "
                    "outgoing arrow-link is using a node-reference in its text "
                    "or notes."
                )

            if len(refs) == 1:
                for segment in segments:
                    if not re.fullmatch(Doc.ref_pat, fr"{segment}"):
                        ret.append(segment)
                    else:
                        if segment in {r"%ref%", r"%ref1%"}:
                            ret.append(refs[r"%ref1%"])
                            ret.append(Command("xspace"))
                        else:
                            raise InvalidRefException(
                                f"Node [{str(node)}(ID: {node.id})] with "
                                "single outgoing arrow-link is using a "
                                "node-reference index more than 1 "
                                f"({segment}) in its text or notes."
                            )
            else:  # Multiple outgoing arrow-links are present
                for segment in segments:
                    if not re.fullmatch(Doc.ref_pat, segment):
                        ret.append(segment)
                    else:
                        try:
                            ret.append(refs[segment])
                            ret.append(Command("xspace"))
                        except KeyError:
                            # trunk-ignore(ruff/B904)
                            raise InvalidRefException(
                                f"Node [{str(node)}(ID: {node.id})] with "
                                "multiple outgoing arrow-links is using an "
                                f"invalid node-reference ({segment}) in its "
                                "text or notes."
                            )

            # Add a label to this node for back reference
            hypertarget = self.get_hypertarget(node)
            if hypertarget:
                ret.append(hypertarget)

        else:  # No references are present in the supplied text
            ret.append(segments[0])

        return ret

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
            new_img_path = Path(self.images_dir, img_path.stem+".pdf")

            # Convert SVG image to PDF
            svg2pdf(url=str(img_path), write_to=str(new_img_path))

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
        ret.append(fig)
        return ret

    def build_number_table_and_notelist(self, node: Node):
        """
        Build a list of LatexObjects suitable for building a LaTeX number-table
        and the list of notes associated with the supplied node.

        """
        if node.children:
            rows = list()         # List of rows with column-values
            notes = list()        # List of notes (if they exist)
            headers = list()      # List of table-headers
            totals = dict()       # Dict for storing sum of column-values
            alignments = ["l", ]  # Alignment specifications for column-values

            # Dict for storing valid table-properties
            tabprops = {
                "column1": "",  # Header for first column
            }

            if str.lower(str(node.children[0])) != "|headers|":
                raise MissingHeaderException(
                    "First child of the number-table "
                    "({node}) must be |headers|.")

            # Collect table-properties, if any
            if node.children[0].notes:
                note_lines = retrieve_note_lines(str(node.children[0].notes))
                for line in note_lines:
                    try:
                        key, val = [str.strip(x) for x in line.split(":", 1)]
                        key = str.lower(key)
                        if key in tabprops:
                            tabprops[key] = val
                    except ValueError:  # Ignore lines not of the form key: val
                        pass

            # Build a list of column-headers
            if node.children[0].children:
                for item in node.children[0].children:
                    headers.append(str(item))
                    if item.icons:
                        if "emoji-1F18E" in item.icons: # Left align the text
                            alignments.append("l")
                        else:
                            alignments.append("r") # Right align the numbers
                            if "emoji-2795" in item.icons: # Summing required
                                totals[str(item)] = 0
                    else:
                        alignments.append("r")
            else:
                raise MissingHeaderException(
                    "No children defined for the node named |headers| in "
                    f"the number-table ({node})."
                )

            for field in node.children[1:]:
                row = [NE(fr"\small{{{EL(field)}}}"""), ]
                if field.children:
                    for aln, hdr, val in zip(alignments[1:], headers, field.children):
                        row.append(NE(fr"\small{{{EL(val)}}}"""))
                        if aln == "r": # Do for numbers only
                            if hdr in totals:
                                totals[hdr] += Decimal(str(val))

                    if len(row) != (len(headers) + 1):
                        raise MissingValueException(
                            'Field-count mismatch in number-table '
                            f'"{str(field)}" for its row "{str(item)}". '
                            'According to its |headers|, there should '
                            f'have been {len(headers)} children for this '
                            f'node, but found {len(row)-1} instead.')
                else:  # No fields for this node, and hence empty row
                    for item in headers:
                        row.append("")
                rows.append(row)

                if field.notes:
                    note_lines = retrieve_note_lines(str(field.notes))
                    field_notes = list()
                    for line in note_lines:
                        line_blocks = list()
                        for item in self.expand_macros(line, field):
                            line_blocks.append(item)
                        field_notes.append(line_blocks)
                    notes.append((field, field_notes))

            # Build table-content first
            tab = Tabular("".join(alignments), pos="c")
            tab.add_hline(color=self.regcol(self.theme.table.line_color))
            row = [
                NE(
                    fr"""
\small{{\color{{{self.regcol(self.theme.table.header_text_color)}}}%
\textsf{{{bold(tabprops["column1"])}}}}}"""
                ),
            ]
            row.extend(
                [
                    NE(fr"""
\small{{\color{{{self.regcol(self.theme.table.header_text_color)}}}%
\textsf{{{bold(hdr)}}}}}"""
                    ) for hdr in headers
                ]
            )
            tab.add_row(
                *row,
                color=self.regcol(self.theme.table.header_row_color),
                strict=True)
            tab.add_hline(color=self.regcol(self.theme.table.line_color))
            for row in rows:
                tab.add_row(*row)
            tab.add_hline(color=self.regcol(self.theme.table.line_color))

            # If summing required, then add a row for totals
            if totals:
                row = [NE(fr"""
\small{{\color{{{self.regcol(self.theme.table.header_text_color)}}}%
\textsf{{{bold("Total")}}}}}"""), ]
                for hdr in headers:
                    if totals.get(hdr, None):
                        row.append(NE(fr"""
\small{{\color{{{self.regcol(self.theme.table.header_text_color)}}}%
\textsf{{{bold(totals[hdr])}}}}}"""))
                    else:
                        row.append("")
                tab.add_row(
                    *row,
                    color=self.regcol(self.theme.table.footer_row_color),
                    strict=True
                )
                tab.add_hline(color=self.regcol(self.theme.table.line_color))

            # Then check if notes are to be collected for the same node
            if notes:
                return [tab, notes]
            return [tab, ]

        # Empty list is returned by default, if nothing else is there
        return list()

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
                    col1[str(field)] = {
                        str.strip(
                            str(d).split(":")[0]): str.strip(
                                str(d).split(":")[1])
                        for d in field.children
                    }
                    if field.notes:
                        note_lines = retrieve_note_lines(str(field.notes))
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
            tab.add_hline(color=self.regcol(self.theme.table.line_color))
            tab.add_hline(color=self.regcol(self.theme.table.line_color))
            col1_hdr = re.sub(r":$", "", str(node))
            row = [
                NE(
                    fr"""
\small{{\color{{{self.regcol(self.theme.table.header_text_color)}}}%
\textsf{{{col1_hdr}}}}}"""
                ),
            ]
            row.extend(
                [
                    NE(fr"""
\small{{\color{{{self.regcol(self.theme.table.header_text_color)}}}%
\textsf{{{hdr}}}}}"""
                    ) for hdr in col_hdrs
                ]
            )
            tab.add_row(
                *row,
                color=self.regcol(self.theme.table.header_row_color),
                strict=True)
            tab.add_hline(color=self.regcol(self.theme.table.line_color))
            for field in sorted(col1.keys()):
                row = [field, ]
                for col in col_hdrs:
                    row.append(col1[field].get(col, ""))
                tab.add_row(row)
            tab.add_hline(color=self.regcol(self.theme.table.line_color))

            # Then check if notes are to be collected for the same node
            if notes:
                return [tab, notes]
            return [tab, ]
        # Empty list is returned by default, if nothing else is there
        return list()

    def build_table_from_child_nodes(self, node: Node):
        """
        Build a list of LaTeX object capable of rendering a table from the
        supplied node and its children.
        """
        if "emoji-1F522" in node.icons:  # Numerical table required
            tab_notes = self.build_number_table_and_notelist(node)
        else:  # Textual table required
            tab_notes = self.build_table_and_notelist(node)
        ret = list()

        hypertarget = self.get_hypertarget(node)
        if hypertarget:
            ret.append(hypertarget)

        if len(tab_notes) >= 1:
            ret.append(NE(r"\begin{center}"))  # Center align
            ret.append(tab_notes[0])
            ret.append(NE(r"\end{center}"))
            if len(tab_notes) > 1:  # Note-text is to be rendered
                itmz = Itemize()
                for h, c in tab_notes[1]:
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
        note_lines = retrieve_note_lines(str(node.notes))
        items = self.expand_macros(note_lines[0], node)
        for item in items:
            mdf.append(Command("small", item))
        for line in note_lines[1:]:
            mdf.append("\n")
            for item in self.expand_macros(line, node):
                mdf.append(Command("small", item))
        return mdf


    def build_list_recursively(self, node: Node, level: int):
        """
        Build and return a list of lists as long as child nodes are present
        in the supplied node.
        """
        if level == 4:
            raise MaximumListDepthException(
                f"Maximum depth of list reached at node: {node}. "
                "The number of nested lists should not go beyond 3.")

        if node.children:
            if "emoji-1F522" in node.icons:  # Ordered list
                lst =  Enumerate()
            else:  # Unordered list is the default
                lst =  Itemize()

            for child in node.children:
                # Do not process items which are annotated with broken-line icon
                if child.icons and "broken-line" in child.icons:
                    continue

                # If any flags are present in the node, then include
                # corresponding LaTeX elements to mark it in the document.
                flags = self.get_applicable_flags(child)


                # If flags present, or others refer it, then create hypertarget
                hypertarget = None
                if len(flags) or child.arrowlinked:
                    hypertarget = self.get_hypertarget(child)

                flagdata = [
                    (x, f"CSREF:{z}", z)
                        for x, y, z in flags if y == 'A' or y == 'D'
                ]
                flagtexts = [x for x, y, z in flagdata]

                content = str(child).split(":", 1)
                if len(content) == 2:
                    if len(flagdata):
                        lst.add_item(NE(fr'{"".join(flagtexts)}\xspace {bold(EL(content[0]))}'))
                    else:
                        lst.add_item(NE(fr'{bold(EL(content[0]))}'))

                    # Add a colon after first part, but only if there exists
                    # some text in the second part of the content.
                    if not str.strip(content[1]) == "":
                        lst.append(": ")

                    texts = self.expand_macros(content[1], child)
                    for text in texts:
                        lst.append(text)
                else:
                    texts = self.expand_macros(str(child), child)
                    if len(flags):
                        lst.add_item(NE(fr'{" ".join(flagtexts)}\xspace {texts[0]}'))
                    else:
                        lst.add_item(texts[0])
                    for text in texts[1:]:
                        lst.append(text)

                # If required, then add a hypertarget
                if hypertarget:
                    lst.append(hypertarget)

                # If required, then add a hyperlink back to the changeset or other sections
                # from where this node is being pointed to.
                if len(flagdata) and self.docinfo["trackchange_section"]:
                    for x, y, z in flagdata:
                        lst.append(
                            NE(fr"\margincomment{{\tiny{{$\Lsh$ \hyperlink{{{y}}}{{{self.docinfo["trackchange_section"]}: {z+1}}}}}}}")
                        )

                # If notes exists in supplied node, then include it too
                if child.notes:
                    if child.icons and "stop-sign" in child.icons:
                        lst.append(self.build_stop_notes(child))
                    else:
                        note_lines = retrieve_note_lines(str(child.notes))
                        for line in note_lines:
                            lst.append(Command("par"))
                            for item in self.expand_macros(line, child):
                                lst.append(item)

                # Add back references, if this node is being pointed to
                # by other nodes (sinks for arrows)
                for referrer in child.arrowlinked:
                    lst.append(NE(
                        fr"\margincomment{{\tiny{{$\Lsh$ \hyperlink{{{get_label(
                            referrer.id)}}}{{{trunc18(
                                str(referrer)
                            )}}}}}}}"))

                if child.children:
                    if child.icons and 'links/file/generic' in child.icons:  # Table is to be built
                        for obj in self.build_table_from_child_nodes(child):
                            lst.append(obj)

                    # Else check if children should be formatted verbatim
                    elif 'links/file/json' in child.icons or \
                    'links/file/xml' in child.icons or \
                    'links/file/html' in child.icons:
                        for item in self.build_verbatim_list(child):
                            lst.append(item)

                    # Expecting a plain list, or list of list, or listof lists ...
                    else:
                        item = self.build_list_recursively(child, level+1)
                        lst.append(item)
            return lst
        return list()

    def build_db_schema(self, node: Node):
        """
        Build a database schema representation in LaTeX using the supplied
        node and its children.

        Parameters
        ----------
        node : Node
            The node using which the DB schema is to be constructed.

        Returns
        -------
        List[LatexObject]
            A list of LaTeX objects built from the supplied node and its
            children.
        """
        ret = list()
        if not node:
            return ret

        if node.children:
            dbtables = list()
            for table in node.children:
                dbtable = DBTable(str(table))
                dbtable.label = get_label(table.id)  # LaTeX label for table
                dbtable.node = table  # To identify and build cross-references

                if table.notes:
                    dbtable.notes = retrieve_note_lines(str(table.notes))
                if table.children:
                    for field in table.children:
                        tbfield = DBTableField(
                            mangled_info=str.strip(str(field))
                        )

                        tbfield.node = field  # To build cross-references
                        if field.notes:
                            tbfield.notes = retrieve_note_lines(field.notes)
                        dbtable.append_field(tbfield)
                dbtables.append(dbtable)

        if not dbtables:
            return ret

        longtab = LongTable(r"p{0.6\textwidth} p{0.34\textwidth}", pos="t")
#        longtab.add_hline(color=self.regcol(self.theme.datatable.tab1_header_line_color))

        # Ordering of attributes of fields in displayed table
        fields = OrderedDict()
        fields["name"] = "field"
        fields["field_type"] = "type"
        fields["unique"] = "unique"
        fields["null"] = "null"
        fields["default"] = "default"

        # Build blocks for tables
        for idx, dbtable in enumerate(dbtables):
            longtab.add_row(
                [NE(fr"\textbf{{\textcolor{{{self.regcol(self.theme.datatable.tab1_header_text_color)}}}{{{idx+1}. {EL(dbtable.name)}}}}}"), ""],
                color=self.regcol(self.theme.datatable.tab1_header_row_color))
#            longtab.add_hline(color=self.regcol(self.theme.datatable.tab1_header_line_color))
            longtab.append(NE(r"\rowcolor{white}"))

            mp1 = MiniPage(width=r"\linewidth", pos="t")
            mp1.append(NE(r"\small"))
            mp1.append(NE(fr'\hypertarget{{{dbtable.label}}}{{}}'))
            mp1.append(NE(fr"\rowcolors{{2}}{{{self.regcol(self.theme.datatable.tab2_rowcolor_1)}}}"))
            mp1.append(NE(fr"{{{self.regcol(self.theme.datatable.tab2_rowcolor_2)}}}"))
            tab_mp1 = Tabularx(NE(r">{\raggedright\arraybackslash}l l X X l"), width_argument=NE(r"\linewidth"), pos="t")
            tab_mp1.add_hline(color=self.regcol(self.theme.datatable.tab2_header_line_color))

            header_text = list()
            for f in fields.keys():
                header_text.append(
                    NE(
                        fr"\textcolor{{{self.regcol(self.theme.datatable.tab2_header_text_color)}}}{{{EL(italic(fields[f]))}}}"
                    )
                )

            tab_mp1.add_row(
                header_text,
                color=self.regcol(
                    self.theme.datatable.tab2_header_row_color
                )
            )
            tab_mp1.add_hline(color=self.regcol(self.theme.datatable.tab2_header_line_color))

            # Build blocks for fields
            field_notes = OrderedDict()
            for tbfield in dbtable:
                if tbfield.notes:  # Preserve notes from table-fields
                    field_notes[tbfield.name] = tbfield.notes
                row_text = list()
                for f in fields.keys():
                    if f == "name":
                        cell_content = verbatim(getattr(tbfield, f))
                        if tbfield.pk:
                            cell_content = fr"{cell_content} \tiny{{\faKey }}"
                        if tbfield.ai:
                            cell_content = fr"{cell_content} \tiny{{\faArrowUp}}"
                        if tbfield.node.arrowlinked:
                            cell_content = fr"\hypertarget{{{get_label(tbfield.node.id)}}}{{{cell_content}}}"
                            margin_notes = list()
                            for arrowlink in tbfield.node.arrowlinked:
                                margin_notes.append(fr"\tiny{{$\Lsh$ \hyperlink{{{get_label(arrowlink.id)}}}{{{EL(arrowlink.parent)}: {EL(arrowlink).split(":")[0]}}}}}")
                            if len(margin_notes) > 0:
                                cell_content = fr"{cell_content} \marginnote{{{NE(r"\newline ".join(margin_notes))}}}"
                        elif tbfield.node.arrowlinks:
                            if len(tbfield.node.arrowlinks) > 1:
                                raise InvalidRefException(fr"More than one arrowlinks found for field {tbfield.name} in table {dbtable.name}")
                            else:
                                fk_label = get_label(tbfield.node.arrowlinks[0].id)
                                cell_content = fr"\mbox{{\makecell[l]{{{cell_content} \\ \tiny{{(\faKey \xspace \hyperlink{{{fk_label}}}{{{EL(tbfield.node.arrowlinks[0].parent)}}}}})}}}}\hypertarget{{{get_label(tbfield.node.id)}}}"
                        row_text.append(NE(cell_content))
                    else:
                        val = getattr(tbfield, f)
                        row_text.append(val if val else " ")
                tab_mp1.add_row(row_text)

            tab_mp1.add_hline(color=self.regcol(self.theme.datatable.tab2_header_line_color))
            mp1.append(tab_mp1)

            mp2 = MiniPage(width=r"\linewidth", pos="t")
            mp2.append(NE(r"\vspace{0.08cm}"))
            mp2.append(NE(r"\tinytosmall"))

            if field_notes:
                itmz = DBItemize(options=("nolistsep", "noitemsep"))
                for field_name in field_notes.keys():
                    if len(field_notes[field_name]) > 1:
                        itmz.add_item(NE(verbatim(field_name+": ")))
                        inner_itmz = Itemize(options=("nolistsep", "noitemsep"))
                        for line in field_notes[field_name]:
                            inner_itmz.add_item(line)
                        itmz.append(inner_itmz)
                    else:
                        itmz.add_item(
                            NE(fr"""
{verbatim(field_name)}: {field_notes[field_name][0]}
"""))
                mp2.append(itmz)

            longtab.add_row(mp1, mp2)
            longtab.append(NE(r"\rowcolor{white}"))

            mp3 = MiniPage(width=r"\linewidth", pos="t")
            mp3.append(NE(r"\tinytosmall"))
            if dbtable.notes:
                itmz = Itemize(options=["nolistsep", "noitemsep"])
                for note in dbtable.notes:
                    itmz.add_item(note)
                mp3.append(itmz)
                mp3.append(NE(r"\vspace{.2cm}"))

            longtab.append(NE(r"\multicolumn{2}{l}{"))
            longtab.append(mp3)
            longtab.append(NE(r"}\\"))
#            longtab.add_hline(color=self.regcol(self.theme.datatable.tab1_header_line_color))
        ret.append(NE(r"\reversemarginpar"))
        ret.append(longtab)
        return ret

    def build_changeset_note_lines(self, node: Node):
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
        List[LatexObject]
            A list of LaTeX objects representing the note-lines of changeset nodes.
        """
        retblocks = list()
        if node.notes:
            for note in retrieve_note_lines(node.notes): # node.notes:
                retblocks.append(NE(r"\noindent"))
                segments = re.split(Doc.param_pat, note)
                if len(segments) > 1:  # Docinfo parameters are present
                    for segment in segments:
                        if not re.fullmatch(Doc.param_pat, f"{segment}"):
                            retblocks.append(segment)
                        else:
                            key = segment[1:-1]
                            if key in self.docinfo.docinfo_tpl:
                                retblocks.append(self.docinfo[self.docinfo.docinfo_tpl[key]])
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

    def build_changeset_table(self, cslist: List):
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
        tab = LongTable(r"l c p{0.75\linewidth}")
        tab.add_hline(color=self.regcol(self.theme.datatable.tab2_header_line_color))
        header_text = list()
        header_text.append(
            NE(
                fr"""\textcolor{{{self.regcol(self.theme.datatable.tab2_header_text_color)}}}%
                {{\tinytosmall{{{EL(italic("No."))}}}}}"""
            )
        )
        header_text.append(
            NE(
                fr"""\textcolor{{{self.regcol(self.theme.datatable.tab2_header_text_color)}}}%
                {{\tinytosmall{{{EL(italic("Type"))}}}}}"""
            )
        )
        header_text.append(
            NE(
                fr"""\textcolor{{{self.regcol(self.theme.datatable.tab2_header_text_color)}}}%
                {{\tinytosmall{{{EL(italic("Changes"))}}}}}"""
            )
        )
        tab.add_row(
            header_text,
            color=self.regcol(
                self.theme.datatable.tab2_header_row_color
            )
        )
        tab.add_hline(color=self.regcol(self.theme.datatable.tab2_header_line_color))
        tab.end_table_header()
        tab.add_hline(color=self.regcol(self.theme.datatable.tab2_header_line_color))
        tab.add_row((MultiColumn(3, align="r", data=NE(r"\faEllipsisH \xspace \faArrowRight")),))
        tab.add_hline(color=self.regcol(self.theme.datatable.tab2_header_line_color))
        tab.end_table_footer()
        tab.add_hline(color=self.regcol(self.theme.datatable.tab2_header_line_color))
        # tab.add_row(
        #     (MultiColumn(3, align="r", data="Changeset Finished"),)
        # )
        #tab.add_hline(color=self.regcol(self.theme.datatable.tab2_header_line_color))
        tab.end_table_last_footer()
        for idx, item in enumerate(cslist):
            sr_no = NE(fr"\tinytosmall{{\hyperlink{{{get_label(item[0].id)}}}{{{idx+1}}}}}")
            flag = None
            if item[1] == "D":
                flag = NE(
                    fr"""\textcolor{{{self.regcol(self.theme.colors.del_mark_color)}}}%
{{\tiny{{{self.theme.config.del_mark_flag}\xspace {self.theme.config.del_mark_text}}}}}""")
            elif item[1] == "A":
                flag = NE(
                    fr"""\textcolor{{{self.regcol(self.theme.colors.new_mark_color)}}}%
{{\tiny{{{self.theme.config.new_mark_flag}\xspace {self.theme.config.new_mark_text}}}}}""")
            else:
                raise InvalidTypeException(
                    "Invalid change-type found in changeset. Valid types are A and D only."
                )
            cs_text = NE(fr"\tinytosmall{{{EL(trunc80(str(item[0])))}}}")
            tab.append(NE(fr"\hypertarget{{CSREF:{idx}}}{{}}"))
            tab.add_row((sr_no, flag, cs_text))
        return tab

    def build_changeset_section(self, node: Node):
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
        List[LatexObject]
            A list of LaTeX objects representing the changeset table.
        """
        retblocks = list()
        if not len(self.changeset): # Nothing to be done
            return retblocks

        if node.notes:
            retblocks.extend(self.build_changeset_note_lines(node))
        retblocks.append(NE("\\begin{center}\\vspace{-0.5cm}"))
        retblocks.append(self.build_changeset_table(self.changeset))
        retblocks.append(NE("\\end{center}"))
        return retblocks

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
        - Handling changeset sections marked with 'inverted red triangle' icon

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
            # Do not process which are annotated with broken-line icon
            if node.icons and "broken-line" in node.icons:
                return list()

            # Get hypertarget before pertient flags are fetched (to fix a bug)
            hypertarget = self.get_hypertarget(node)

            flags = self.get_applicable_flags(node)
            flagdata = [
                (x, f"CSREF:{z}", z)
                    for x, y, z in flags if y == 'A' or y == 'D'
            ]
            flagtexts = [x for x, y, z in flagdata]

            if len(flagdata):
                node_text = fr'{" ".join(flagtexts)} {EL(str(node))}'
            else:
                node_text = EL(str(node))

            if level == 1:
                blocks.append(Section(NE(node_text), label=None))
            elif level == 2:
                blocks.append(Subsection(NE(node_text), label=None))
            elif level == 3:
                blocks.append(Subsubsection(NE(node_text), label=None))
            elif level == 4:
                blocks.append(Paragraph(NE(node_text), label=None))
            elif level == 5:
                blocks.append(
                    Subparagraph(NE(node_text), label=None)
                )
            else:
                # Any nodes beyond subparagraph (level=5) is not allowed.
                # One more level (Subsubparagraph) is possible but not being
                # used at present. Too many nested sections indicate problems
                # in organization of the document-structure.
                raise MaximumSectionDepthException(
                    f"Maximum depth ({level}) of sections reached for ndoe: "
                    f"'{node}'. Move this node to a lower level by "
                    "rearranging the structure/sections of your document in "
                    "the mindmap."
                )

            # Icon inverted red triangle along with trackchange section defined in docinfo
            if node.icons and "emoji-1F53B" in node.icons and self.docinfo["trackchange_section"]:
                if self.changeset_node:  # Ensure changeset node doesn't exist already
                    raise InvalidNodeException(
                        f'Node "{str(self.changeset_node)}(ID: {self.changeset_node.id})" is '
                        " already marked as changeset node. More than one changeset "
                        "nodes are not allowed to be maintained in a document. "
                        f'Remove either that node or the node "{str(node)}" (ID: {node.id}) '
                        "from the mindmap to continue."
                    )
                self.changeset_node = node
                self.changeset_section = blocks[-1]  # Add to changeset section
                return list()

            if hypertarget:
                blocks.append(hypertarget)

            if len(flagdata) and self.docinfo["trackchange_section"]:
                # Back references to changeset sections are required
                for x, y, z in flagdata:
                    blocks.append(
                        NE(fr"\margincomment{{\tiny{{$\Lsh$ \hyperlink{{{y}}}{{{self.docinfo["trackchange_section"]}: {z+1}}}}}}}")
                    )

            if node.arrowlinked:
                for referrer in node.arrowlinked:
                    blocks.append(
                        NE(
                            rf"""%
\margincomment{{\tiny{{$\Lsh$ %
\hyperlink{{{get_label(referrer.id)}}}{{{trunc18(str(referrer))}}}}}%
\newline}}"""
                        )
                )  # Add a margin comment

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
                elif node.icons and (
                    "links/libreoffice/file_doc_database" in node.icons):
                    blocks.extend(self.build_db_schema(node))
                    stop_traversing = True  # No more section processing needed

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
\renewcommand{{\headrule}}%
{{\color{{{self.regcol(self.theme.colors.header_line_color)}}}%
\hrule width \headwidth height \headrulewidth}}
\renewcommand{{\footrule}}%
{{\color{{{self.regcol(self.theme.colors.footer_line_color)}}}%
\hrule width \headwidth height \footrulewidth}}"""
            ),
        )

        lheader, cheader, rheader, lfooter, cfooter, rfooter = \
            (None for i in range(6))
        credits_marked = False

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
            if self.docinfo['l_footer_text'] != "%%":
                lfooter = NE(rf"{self.docinfo['l_footer_text']}")
        else:
            lfooter = NE(fr"\tiny{{{DocInfo.credits}}}")  # Credit-text
            credits_marked = True

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
            if self.docinfo['c_footer_text'] != "%%":
                cfooter = NE(rf"{self.docinfo['c_footer_text']}")
        elif not credits_marked:
            cfooter = NE(fr"\tiny{{{DocInfo.credits}}}")
            credits_marked = True

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
            if self.docinfo['r_footer_text'] != "%%":
                rfooter = NE(fr"\small{{{self.docinfo['r_footer_text']}}}")
        elif not credits_marked:
            rfooter = NE(fr"\tiny{{{DocInfo.credits}}}")
            credits_marked = True

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

        if self.docinfo.get("doc_version", None):
            doc_version = self.docinfo["doc_version"]
        else:
            doc_version = ""

        if self.docinfo.get("doc_title", None):
            doc_title = self.docinfo["doc_title"]
        else:
            doc_title = "<Missing Document Title>"

        if self.docinfo.get("doc_author", None):
            doc_author = self.docinfo["doc_author"]
        else:
            doc_author = "<Missing Document Author>"

        if self.docinfo.get("doc_date", None):
            doc_date = self.docinfo["doc_date"]
        else:
            doc_date = NE(r"\today")

        headfoot = self.build_headers_and_footers()
        doc.preamble.append(headfoot)

        doc.change_document_style("header")

        doc.append(
            NE(r"""
\begin{titlepage}
\centering
\vspace*{\fill}"""))

        if self.docinfo.get("tp_top_logo", None):
            doc.append(
                NE(fr"""
\includegraphics[%
height={self.theme.geometry.tp_top_logo_height}]%
{{{self.get_absolute_file_path(self.docinfo['tp_top_logo'])}}}\\
\vspace*{{{self.theme.geometry.tp_top_logo_vspace}}}"""))

        doc.append(
            NE(fr"""
\huge \bfseries {doc_title}\\
    \vspace*{{0.2cm}}
\small (Version: {doc_version})\\
    \vspace*{{0.2cm}}
\large {doc_author}\\
{doc_date}\\
\normalsize"""))

        if self.docinfo.get("tp_bottom_logo", None):
            doc.append(
                NE(fr"""
\vspace*{{{self.theme.geometry.tp_bottom_logo_vspace}}}
\includegraphics[%
height={self.theme.geometry.tp_bottom_logo_height}]%
{{{self.get_absolute_file_path(self.docinfo['tp_bottom_logo'])}}}\\"""))

        doc.append(
            NE(r"""
\vspace*{\fill}
\end{titlepage}
"""))

        #doc.append(NE(r"\maketitle"))
        doc.append(NE(r"\tableofcontents"))
        doc.append(NE(r"\newpage"))
        doc.append(NE(r"\justify"))

        # Create a list to hold the instances of LatexObject built using the
        # content of the mindmap.
        blocks = list()

        # Start traversing the child nodes one-by-one to build the content
        for child in self.mm.rootnode.children:
            self.traverse_children(child, 1, blocks)

        # If track changes are required to be collated into a section and if no
        # node is marked already to hold the changeset entries (by annotating
        # it with an icon of inverted red triangle), then append such a section
        # at the end of the document.
        if self.docinfo["trackchange_section"]:
            if self.changeset_node:
                cslist = self.build_changeset_section(self.changeset_node)
                for item in cslist:
                    self.changeset_section.append(item)
            else:
                cs_section = Section(self.docinfo["trackchange_section"])
                cs_section.append(NE("\\begin{center}\\vspace{-0.5cm}"))
                cs_section.append(self.build_changeset_table(self.changeset))
                cs_section.append(NE("\\end{center}"))
                blocks.append(cs_section)

        for color in self.colors:
            doc.add_color(color[0], color[1], color[2])

        for obj in blocks:
            doc.append(obj)

        with doc.create(Center()):
            doc.append(VerticalSpace(".5cm"))
            doc.append(HugeText(bold(r"* * * * *")))

            # docinfo based timezone is preferred
            if self.docinfo.get("timezone", None):
                tz = self.docinfo["timezone"]
            else:  # then comes option of confuguration based timezone
                tz = self.theme.config.timezone
            retrieaval_date = datetime.now(
                pytz.timezone(tz)).strftime("%d %B, %Y at %I:%M:%S %p %Z")
            doc.append(NE("\n"))
            doc.append((
                NE(fr"\tiny{{(Document prepared on {retrieaval_date})}}")))

        # Create folder to store images, if any
        file_path = Path(output_file_path)
        if file_path.suffix.lower() == ".pdf":
            file_path = file_path.with_suffix("")
        curr_dir = os.getcwd()
        os.chdir(self.working_dir)
        doc.generate_pdf(file_path, clean=clean, clean_tex=clean_tex)
        os.chdir(curr_dir)

def get_sample_config():
    """
    Return content of sample configuration file in YAML format.

    Returns
    -------
    str :
        Sample configuration in YAML format
    """

    theme = Theme()
    data = dict()


    def get_class_attributes(cls):
        return {
            key: value
            for key, value in cls.__class__.__dict__.items()
            if not key.startswith("__") and not callable(value)
        }

    for attr in [i for i in dir(theme) if not callable(i) and not i.startswith("__")]:
        data[attr] = get_class_attributes(getattr(theme, attr))

        #{k:v for k, v in getattr(theme, attr).__class__.__dict__.items() if not k.startswith("__")}
    return yaml.dump(data, default_flow_style=False)


def create_theme_from_config(conf_file):
    """
    Create a theme from the supplied fp-convert configuration file.

    Parameters
    ----------
    config_file : str
        The path to the fp-convert configuration file

    Returns
    -------
    Theme
        A theme created for FPDoc from the supplied configuration file.
    """
    config = Config()
    geometry = Geometry()
    table = Table()
    datatable = DataTable()
    colors = Colors()
    conf = yaml.safe_load(open(conf_file))
    if conf:
        for key in conf.keys():
            if key == "geometry":
                for k in conf[key].keys():
                    setattr(geometry, k, conf[key][k])
            elif key == "table":
                for k in conf[key].keys():
                    setattr(table, k, conf[key][k])
            elif key == "datatable":
                for k in conf[key].keys():
                    setattr(datatable, k, conf[key][k])
            elif key == "colors":
                for k in conf[key].keys():
                    setattr(colors, k, conf[key][k])
            elif key == "config":
                for k in conf[key].keys():
                    setattr(config, k, conf[key][k])
                if not config.new_mark_text:
                    config.new_mark_text = ""
                if not config.del_mark_text:
                    config.del_mark_text = ""
    else:
        raise UnsupportedFileException(f"Malformed configuration file {conf_file}.")

    return Theme(
        config=config, geometry=geometry, table=table,
        datatable=datatable, colors=colors)


class DBItemize(Itemize):
    pass