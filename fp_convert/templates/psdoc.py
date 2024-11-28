import re
from typing import Optional

from pylatex import Command, Foot, Head, NoEscape, PageStyle

from .. import FPDoc
from ..errors import IncorrectInitialization, InvalidRefException
from ..helpers import DocInfo, get_label

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
    header_thickness = "0.4pt"  # Header line thickness
    footer_thickness = "0.4pt"  # Footer line thickness


class Geometry:
    """
    Following attributes define various geometry specific parameters of the
    page.
    """

    left_margin = "1.3in"
    inner_margin = "1.3in"  # Applicable only in twosided mode
    right_margin = "1.5in"
    outer_margin = "1.5in"  # Applicable only in twosided mode
    top_margin = "1.5in"
    bottom_margin = "1.5in"
    head_height = "20pt"
    par_indent = "0pt"
    l_header_image_height = "0.5cm"


class Table:
    """
    Following colors are defined for the default tables laid out in PSD.
    """

    header_color = ("Apricot",)
    rowcolor_1 = "gray!25"
    rowcolor_2 = "white"
    line_color = "red"


class Color:
    """
    Following colours are defined for styling the PSD.
    """

    header_line_color = "red"
    footer_line_color = "red"
    # link_color = "{rgb}{0.63, 0.79, 0.95}"
    link_color = "gray"
    file_color = "magenta"
    mc_color = "{rgb}{0,0.5,0}"  # Color of margin comments
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
        color: Optional[Color] = None,
    ):
        # Use default values of respective paramaters, if supplied ones
        # are None.
        self.config = Config() if not config else config
        self.geometry = Geometry() if not geometry else geometry
        self.table = Table() if not table else table
        self.color = Color() if not color else color


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
        mm_file: Optional[str] = None,
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
            file. A DocInfo object would be constructed automatically from the
            information obtained from the root node of this mindmap.
        :param docinfo: A DocInfo object, containing the document related
            information.
        :param theme: An instance of Theme class which would be used for
            constructing the document. The styles, geometry of the page,
            colors etc. are defined in this class.
        :param lmodern: A boolean indicating whether to use Latin Modern
            fonts in the resultant LaTeX document. Default value of it is
            False.
        """
        super().__init__(lmodern=lmodern)
        if theme is None:  # If user-supplied theme is absent, use default
            theme = Theme()

        self.theme = theme
        if not docinfo and not mm_file:  # At least one of them is required
            raise IncorrectInitialization(
                "Either mindmap file path or DocInfo object should be supplied"
            )

        if docinfo and mm_file:
            pass

        self.packages = (
            ("geometry", tuple()),
            ("amssymb", tuple()),
            ("xcolor", ("dvipsnames", "table")),
            ("tcolorbox", ("most",)),
            ("placeins", ("section",)),
            ("titlesec", tuple()),
            ("fontenc", ("T1",)),
            ("hyperref", tuple()),
            ("mdframed", ("framemethod=TikZ",)),
            ("ragged2e", ("raggedrightboxes",)),
        )

        self.preambletexts = (
            NoEscape(rf"\setcounter{{secnumdepth}}{{{theme.config.sec_depth}}}"),
            NoEscape(rf"\setcounter{{tocdepth}}{{{theme.config.toc_depth}}}"),
            NoEscape(rf"\setlength{{\parindent}}{{{theme.geometry.par_indent}}}"),
            NoEscape(rf"\titleformat{{\paragraph}}{theme.config.par_title_format}"),
            NoEscape(
                rf"\titlespacing*{{\paragraph}}{theme.config.par_title_spacing}"
            ),  # noqa
            NoEscape(
                rf"\titleformat{{\subparagraph}}{theme.config.subpar_title_format}"
            ),  # noqa
            NoEscape(
                rf"\titlespacing*{{\subparagraph}}{theme.config.subpar_title_spacing}"
            ),  # noqa
            NoEscape(rf"\definecolor{{mccol}}{theme.color.mc_color}"),
            NoEscape(
                r"\newcommand\margincomment[1]{\RaggedRight{"
                r"\marginpar{\hsize1.7in\tiny\color{mccol}{#1}}}}"
            ),
            NoEscape(
                r"\mdfdefinestyle{{StopFrame}}{{linecolor="
                rf"{theme.color.sf_line_color}, outerlinewidth="
                rf"{theme.config.sf_outer_line_width}, "
                rf"roundcorner={theme.config.sf_round_corner_size},"
                rf"rightmargin={theme.config.sf_outer_right_margin},"
                rf"innerrightmargin={theme.config.sf_inner_right_margin},"
                rf"leftmargin={theme.config.sf_outer_left_margin},"
                rf"innerleftmargin={theme.config.sf_inner_left_margin},"
                rf"backgroundcolor={theme.color.sf_background_color}}}"
            ),
            NoEscape(
                rf"""
\hypersetup{{
%pdftitle={{Project Specifications Document}},
%pdfpagemode=FullScreen,
colorlinks=true,
linkcolor={theme.color.link_color},
filecolor={theme.color.file_color},
urlcolor={theme.color.url_color}
}}"""
            ),
            # Setting headheight
            NoEscape(rf"\setlength\headheight{{{theme.geometry.head_height}}}"),
            # Styling the geometry of the document
            #
            NoEscape(
                rf"""
\geometry{{
a4paper,
%total={{170mm,257mm}},
left={theme.geometry.left_margin},
inner={theme.geometry.inner_margin},
right={theme.geometry.right_margin},
outer={theme.geometry.outer_margin},
top={theme.geometry.top_margin},
bottom={theme.geometry.bottom_margin},
}}"""
            ),
        )  # End of tuple preambletexts

    def _emr(self, text, node):
        """
        Private function to expand macros to get applicable reference-details.
        It is usually used to retrieve the reference-links from supplied node,
        and patch it in the returned content.

        Parameters
        ----------
        text : str
            The text from which the macros are to be extracted as well as
            expanded.
        node : freeplane.MindmapNode
            The current node which would be searched to identify other nodes
            to which it refers to.
        """
        mpats = PSDoc.ref_pat.findall(text)
        if mpats:
            labels = list()
            if node.arrowlinks:
                for node_to in node.arrowlinks:
                    labels.append(get_label(node_to.id))
            else:
                raise InvalidRefException(
                    f"Node [{str(node)}(ID: {node.id})] without any"
                    "outgoing arrow-link is using a node-reference."
                )

            if len(labels) == 1:
                text = text.replace("%ref%", rf"\autoref{{{labels[0]}}}")
            else:
                for idx, label in enumerate(labels):
                    text = text.replace(f"%ref{idx+1}%", rf"\autoref{{{label}}}")

            # Add a label to this node for back reference
            text = text + NoEscape(rf"\label{{{get_label(node.id)}}}")
        return text

    def generate_pdf(self, output_file: str):
        """
        Generate PDF document from the supplied content of the mindmap.

        Parameters
        ----------
        output_file : str
            The file name (with path if required) to which the generated PDF
            is to be saved.
        """

        # Start buidling the LaTeX document
        self.preamble.append(Command("title", self.docinfo.title))
        self.preamble.append(Command("author", self.docinfo.author))
        self.preamble.append(Command("date", self.docinfo.date))
        header = PageStyle(
            "header",
            header_thickness=self.theme.config.header_thickness,
            footer_thickness=self.theme.config.footer_thickness,
            data=NoEscape(
                rf"""
\renewcommand{{\headrule}}{{\color{{{self.theme.color.header_line_color }}}\hrule width \headwidth height \headrulewidth}}%
\renewcommand{{\footrule}}{{\color{{{self.theme.color.footer_line_color}}}\hrule width \headwidth height \footrulewidth}}%
                """
            ),
        )
        if self.docinfo.get("l_header_image", None):
            lheader = NoEscape(
                rf"\includegraphics[height={self.theme.geometry.l_header_image_height}]{{{self.docinfo['l_header_image']}}}"
            )
        elif self.docinfo.get("l_header_text", None):
            lheader = NoEscape(rf"{self.docinfo['l_header_text']}")
        if lheader:
            with header.create(Head("L")):
                header.append(lheader)
xxxxx
        super().generate_pdf(output_file)
