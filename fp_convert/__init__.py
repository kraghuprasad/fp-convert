from pylatex import Document


class FPDoc(Document):
    """
    Base class for all document templates.

    Parameters
    ----------
    lmodern: bool
        Whether or not to use latin modern font family in the LaTeX document
        getting generated. If it is ``True`` then
        `lmodern package <https://ctan.org/pkg/lm>` is loaded, and it is used
        in the document.
    """

    def __init__(self, lmodern=True):
        super().__init__(lmodern=lmodern)
