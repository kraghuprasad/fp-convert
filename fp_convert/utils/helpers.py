import re

"""
Utility functions used for FreePlane mindmap to PDF conversion.
"""
from freeplane import Node

from ..errors import InvalidDocinfoKey


def get_label(id: str):
    """
    Replace _ with : in the ID of the nodes created by FP.

    Parameters
    ----------
    id : str
        ID of the node in the mindmap which needs to be transformed to replace
        underscore(_) with colon(:).

    Returns
    -------
    str :
        Transformed ID.
    """
    return id.replace("_", ":")


def retrieve_note_lines(text: str):
    """
    Build and return a list of paragraphs found per line of note-texts.
    It ensures that no whitespaces surrounds the paragraph of texts returned
    in a list.

    Parameters
    ----------
    text : str
        The note-text from which paragraphs are to be retrieved, assuming that
        one line of text contains one paragraph.

    Returns
    -------
    list[str] :
        A list of paragraphs found in the note-text.
    """
    ret = list()
    if text:
        [ret.append(str.strip(i)) for i in text.split("\n") if str.strip(i)]
    return ret


def get_notes(node: Node):
    """
    Extract note-text from a Freeplane node, and return a list of paragraphs
    found in it.

    Parameters
    ----------
    node : Node
        The Freeplane node from which notes are to be retrieved.

    Returns
    -------
    list[str] :
        A list of paragraphs found in the note-text associated with supplied
        node.
    """
    if node.notes:
        return retrieve_note_lines(node.notes)
    return None


class DocInfo:
    """
    The DocInfo class collects the document related information from the text
    content supplied while initializing it. Usually this text is stored in the
    root node of the Freeplane mindmap. It is used by document templates while
    building the document.

    Parameters
    ----------
    info_text : str
        The text using which the document related information is to be
        retrieved.
    preserve_latex : bool
        A boolean indicating whether to preserve the LaTeX file generated as
        part of building the PDF document. It is set to ``True`` by default.
    """
    docinfo_tpl = {  # Statically defined field converter template for docinfo
        "Version": "doc_version",
        "Date": "doc_date",
        "Author": "doc_author",
        "Client": "client",
        "Vendor": "vendor",
        "L_Header_Text": "l_header_text",
        "L_Header_Logo": "l_header_image",
        "C_Header_Text": "c_header_text",
        "C_Header_Logo": "c_header_image",
        "R_Header_Text": "r_header_text",
        "R_Header_Logo": "r_header_image",
        "L_Footer_Text": "l_footer_text",
        "L_Footer_Logo": "l_footer_image",
        "C_Footer_Text": "c_footer_text",
        "C_Footer_Logo": "c_footer_image",
        "R_Footer_Text": "r_footer_text",
        "R_Footer_Logo": "r_footer_image",
        "Intro_Text": "intro_text",
    }
    regex_pat = "^(" + "|".join([k for k in docinfo_tpl.keys()]) + ") *:(.+)$"
    compiled_pat = re.compile(regex_pat)

    def __init__(self, info_text: str, preserve_latex: bool = True):
        self.preserve_latex = preserve_latex
        self.docinfo = {v: None for v in DocInfo.docinfo_tpl.values()}
        if info_text:
            for line in retrieve_note_lines(info_text):
                mpats = DocInfo.compiled_pat.search(line)
                if mpats:
                    self.docinfo[DocInfo.docinfo_tpl[str.strip(mpats[1])]] = \
                        str.strip(mpats[2])

    def set_info(self, key: str, value: str):
        """
        Set the value for a valid key in the DocInfo object.

        Parameters
        ----------
        key : str
            The key for which the value is to be set.
        value : str
            The value to be set for the key.

        Raises
        ------
        InvalidDocinfoKey
            If supplied key is not found to be a valid one.
        """
        if DocInfo.docinfo_tpl.get(key, None):
            self.docinfo[DocInfo.docinfo_tpl[key]] = value
        else:
            raise InvalidDocinfoKey(f"Invalid DocInfo key: {key}")

