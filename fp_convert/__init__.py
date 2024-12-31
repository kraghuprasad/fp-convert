from freeplane import Node
from pathlib import Path
from pylatex import Document, Itemize
from pylatex.utils import NoEscape as NE

from .utils.decorators import register_color, track_processed_nodes
from .errors import MissingFileException
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
                f"A required file ({file_path}) is missing. Either use an"
                "absolute file path, or a path relative to the mindmap"
                "itself. Also the file must exist already."
            )
        return abs_path

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
