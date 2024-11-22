import re
from typing import Optional
from pylatex import NoEscape

from .. import FPDoc
from ..errors import InvalidRefException, IncorrectInitialization
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
    par_title_format = r"[hang]{\normalfont\normalsize\bfseries}{\theparagraph}{1em}{}"  # noqa
    par_title_spacing = r"{0pt}{3.25ex plus 1ex minus .2ex}{.75em}"
    subpar_title_format = r"[hang]{\normalfont\normalsize\bfseries}{\thesubparagraph}{1em}{}"  # noqa
    subpar_title_spacing = r"{0pt}{3.25ex plus 1ex minus .2ex}{.75em}"
    sf_outer_line_width = "1pt"    # Stop-Frame outer line-width size
    sf_round_corner_size = "3pt"   # Stop-Frame rounded corner's size
    sf_outer_left_margin = "5pt"   # Stop-Frame outer left margin width
    sf_inner_left_margin = "5pt"   # Stop-Frame inner left margin width
    sf_outer_right_margin = "5pt"  # Stop-Frame outer right margin width
    sf_inner_right_margin = "5pt"  # Stop-Frame inner right margin width


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


class Table:
    """
    Following colors are defined for the default tables laid out in PSD.
    """
    header_color = "Apricot",
    rowcolor_1 = "gray!25"
    rowcolor_2 = "white"
    line_color = "red"


class Color:
    """
    Following colours are defined for styling the PSD.
    """
    # link_color = "{rgb}{0.63, 0.79, 0.95}"
    link_color = "gray"
    file_color = "magenta"
    mc_color = "{rgb}{0,0.5,0}"  # Color of margin comments
    sf_line_color = "red"        # Stop-Frame line-color
    sf_background_color = "red!5!white"  # Stop-Frame background-color


class Theme:
    """
    A class to hold the overall theme of the document.
    """
    def __init__(self, config: Config = Config(),
                 geometry: Geometry = Geometry(),
                 table: Table = Table(), color: Color = Color()):
        self.config = config
        self.geometry = geometry
        self.table = table
        self.color = color


class PSDoc(FPDoc):
    """
    It defines the parameters required to generate a project specifications
    document.
    """

    # Reference patterns which match %ref%, and %refN% where N is a number.
    # These are used in the node as well as in their note-texts, whenever a
    # reference is needed to another node via an arrow-link.
    ref_pat = re.compile('%(ref[0-9]*)%')

    def __init__(self, mm_file: Optional[str] = None,
                 docinfo: Optional[DocInfo] = None,
                 theme: Theme = Theme(config=Config(),
                                      geometry=Geometry(),
                                      table=Table(),
                                      color=Color()),
                 lmodern: bool = False):
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
        if not mm_file and not docinfo:
            raise IncorrectInitialization(
                "Supply either path to a mindmap file (mm_file), or DocInfo"
                "object (docinfo) while initializing the PSDoc template.")

        self.theme = theme

        self.packages = (
            ('geometry', tuple()),
            ('amssymb', tuple()),
            ('xcolor', ("dvipsnames", "table")),
            ('tcolorbox', ("most", )),
            ('placeins', ("section", )),
            ('titlesec', tuple()),
            ('fontenc', ("T1", )),
            ('hyperref', tuple()),
            ('mdframed', ("framemethod=TikZ", )),
            ('ragged2e', ("raggedrightboxes", )),
        )

        self.preambletexts = (
            NoEscape(
                fr"\setcounter{{secnumdepth}}{{{theme.config.sec_depth}}}"),
            NoEscape(
                fr"\setcounter{{tocdepth}}{{{theme.config.toc_depth}}}"),
            NoEscape(
                fr"\setlength{{\parindent}}{{{theme.geometry.par_indent}}}"),
            NoEscape(
                fr"\titleformat{{\paragraph}}{theme.config.par_title_format}"),
            NoEscape(fr"\titlespacing*{{\paragraph}}{theme.config.par_title_spacing}"),  # noqa
            NoEscape(fr"\titleformat{{\subparagraph}}{theme.config.subpar_title_format}"),  # noqa
            NoEscape(fr"\titlespacing*{{\subparagraph}}{theme.config.subpar_title_spacing}"),  # noqa
            NoEscape(fr"\definecolor{{mccol}}{theme.color.mc_color}"),
            NoEscape(
                r"\newcommand\margincomment[1]{\RaggedRight{"
                r"\marginpar{\hsize1.7in\tiny\color{mccol}{#1}}}}"),
            NoEscape(
                r"\mdfdefinestyle{{StopFrame}}{{linecolor="
                fr"{theme.color.sf_line_color}, outerlinewidth="
                fr"{theme.config.sf_outer_line_width}, "
                fr"roundcorner={theme.config.sf_round_corner_size},"
                fr"rightmargin={theme.config.sf_outer_right_margin},"
                fr"innerrightmargin={theme.config.sf_inner_right_margin},"
                fr"leftmargin={theme.config.sf_outer_left_margin},"
                fr"innerleftmargin={theme.config.sf_inner_left_margin},"
                fr"backgroundcolor={theme.color.sf_background_color}}}"),
            NoEscape(fr"""
\hypersetup{{
%pdftitle={{Project Specifications Document}},
%pdfpagemode=FullScreen,
colorlinks=true,
linkcolor={theme.color.link_color},
filecolor={theme.color.file_color},
urlcolor={theme.color.url_color}
}}"""),
            # Setting headheight
            NoEscape(
                fr"\setlength\headheight{{{theme.geometry.head_height}}}"),

            # Styling the geometry of the document
            #
            NoEscape(fr"""
\geometry{{
a4paper,
%total={{170mm,257mm}},
left={theme.geometry.left_margin},
inner={theme.geometry.inner_margin},
right={theme.geometry.right_margin},
outer={theme.geometry.outer_margin},
top={theme.geometry.top_margin},
bottom={theme.geometry.bottom_margin},
}}"""),
        )  # End of tuple preambletexts

        super().__init__(lmodern=lmodern)

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
                        "outgoing arrow-link is using a node-reference.")

            if len(labels) == 1:
                text = text.replace('%ref%', fr'\autoref{{{labels[0]}}}')
            else:
                for idx, label in enumerate(labels):
                    text = text.replace(f"%ref{idx+1}%",
                                        fr'\autoref{{{label}}}')

            # Add a label to this node for back reference
            text = text + NoEscape(fr"\label{{{get_label(node.id)}}}")
        return text
