# from peek import peek
from pylatex import Document

# Version of the package
__version__ = "0.2.0"


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
