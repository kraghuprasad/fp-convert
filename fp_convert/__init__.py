from pathlib import Path

from freeplane import Node
from pylatex import Document, Itemize
from pylatex.utils import NoEscape as NE

from .errors import MissingFileException
from .utils.decorators import register_color, track_processed_nodes
from .utils.helpers import get_label


class FPDoc(Document):
    """
    Base class for all document templates.

    Parameters
    ----------
    name: str
        The name of the document.
    documentclass: str
        The LaTeX document-type to be used to construct this document. The
        default is "article" type.
    lmodern: bool
        Whether or not to use latin modern font family in the LaTeX document
        getting generated. If it is ``True`` then
        `lmodern package <https://ctan.org/pkg/lm>` is loaded, and it is used
        in the document.
    """

    def __init__(self, name: str, documentclass: str = "article", lmodern=True):
        super().__init__(name, documentclass=documentclass, lmodern=False)

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
                f"A required file ({file_path}) is missing. Either use an "
                "absolute file path, or a path relative to the mindmap "
                "itself. Also the file must exist already."
            )
        return abs_path

    # Used mostly in cases where raw text is being exchanged, instead of
    # PyLaTeX based objects to build the document. For example, while building
    # verbatim lists.
    def mark_flags(self, text: str, node: Node):
        """
        Check if node has any applicable flags like for deletion or addition
        etc. and add pertient notes or icons to the supplied text. If no flags
        are present, then the supplied text is returned as it is.

        Parameters:
            text: str
                The text to which the flags are to be added.

            node: Node
                The node whose applicable flags are to be checked.
        """
        # Check for deletion flag first
        if node.icons and "button_cancel" in node.icons:
            frame_top = fr"""
\textcolor{{red}}%
{{\faTimes \rule[0.33em]{{0.2\textwidth}}{{0.2pt}}%
\small following is marked for removal%
\normalsize \rule[0.33em]{{0.2\textwidth}}{{0.2pt}}%
\faTimes}}\newline%"""
            frame_bot = fr"""
\textcolor{{red}}{{\faTimes \rule[0.33em]{{0.725\textwidth}}{{0.2pt}}%
\faTimes}}"""
            text = f"{NE(frame_top)}{text}{NE(frame_bot)}"
        elif node.icons and "addition" in node.icons:  # Check for addition
            prefix = fr"\textcolor{{cobalt}}{{\rotatebox{{30}}{{\tiny{{\textbf{{New}}}}}}\faFlagCheckered }}"
            text = f"{prefix}{text}"
        return text

    def get_applicable_flags(self, node: Node):
        """
        Check if node has any applicable flags like for deletion or addition of
        text-blocks or graphical elements etc. and return a list with appropriate
        flags, icons or notes. If no flags are present, then return an empty list.

        Parameters:
            node: Node
                The node whose applicable flags are to be checked and evaluated.
        """
        ret = list()

        # Check for deletion flag first and if not found then check for addition
        # as these two cases are mutually exclusive.
        if node.icons and "button_cancel" in node.icons:
            flag = NE(
                fr"""
\textcolor{{{self.regcol(self.theme.colors.del_mark_color)}}}{{%
{{\rotatebox{{30}}{{\tiny{{\textbf{{{self.docinfo["del_mark_text"]}}}}}}}}}%
{{{self.docinfo["del_mark_flag"]}}}}}""")
            ret.append(flag)
        elif node.icons and "addition" in node.icons:
            flag = NE(
                fr"""
\textcolor{{{self.regcol(self.theme.colors.new_mark_color)}}}{{%
{{\rotatebox{{30}}{{\tiny{{\textbf{{{self.docinfo["new_mark_text"]}}}}}}}}}
{{{self.docinfo["new_mark_flag"]}}}}}""")
            ret.append(flag)

        # If required, more flags can be handled here before returning
        return ret

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
                else:
                    # To avoid bullet, starting the item with []
                    p = f"{p}%\n[]\\begin{{verbatim}}\n{str(child)}\\end{{verbatim}}"

                # Search and add any applicable flag related texts
                p = self.mark_flags(p, child)

                # Add back references, if this node is being pointed to by other
                # nodes (sinks for arrows)
                for referrer in node.arrowlinked:
                    p += NE(
                        fr"\margincomment{{\tiny{{$\Lsh$ \autoref{{{get_label(
                            referrer.id)}}}}}}}")

                itmz.add_item(NE(p))
            return [itmz,]
        return list()

    @register_color
    def regcol(self, color):
        """
        Register supplied color to the document before proceeding
        """
        return color