import pytest

from fp_convert.errors import InvalidDocInfoKey
from fp_convert.utils.helpers import DocInfo, get_label, retrieve_note_lines

# from peek import peek


def test_get_label():
    assert get_label("user_id") == "user:id"
    assert get_label("no_underscore") == "no:underscore"
    assert get_label("") == ""


def test_retrieve_note_lines():
    text = "  First paragraph  \n  Second paragraph  \n"
    result = retrieve_note_lines(text)
    assert result[0] == "First paragraph"
    assert result[1] == "Second paragraph"
    assert retrieve_note_lines("") == []


def test_docinfo_initialization():
    info_text = """
    Version: 1.0
    Title: Test Document
    Date: 2025-01-04
    """
    doc_info = DocInfo(info_text)

    assert doc_info["doc_version"] == "1.0"
    assert doc_info["doc_title"] == "Test Document"
    assert doc_info["doc_date"] == "2025-01-04"


def test_docinfo_invalid_key():
    doc_info = DocInfo("")

    with pytest.raises(InvalidDocInfoKey):
        doc_info["invalid_key"] = "test"

    with pytest.raises(KeyError):
        _ = doc_info["non_existent_key"]


def test_docinfo_dictionary_methods():
    info_text = """
    Version: 1.0
    Title: Test Document
    Date: 15 November, 2024
    Author: Whoopie Bard $<$whoopie@clueless.dev$>$\\Changu Bhai $<$changu.bhai@clueless.dev$>$
    Client: Blooper Corporation Inc.
    Vendor: Clueless Developers' Consortium
    Trackchange_Section: Track Changes
    TP_Top_Logo: images/blooper_logo.pdf
    TP_Bottom_Logo: images/clueless_devs_consortium.pdf
    C_Header_Text: Project Specifications of Blooper App
    R_Header_Text: Non-Confidential
    L_Header_Logo: images/blooper_logo.pdf
    C_Footer_Logo: images/clueless_devs_consortium.pdf
    R_Footer_Text: \small{Page \thepage\- of \pageref*{LastPage}}
    Timezone: Asia/Kolkata
    """
    doc_info = DocInfo(info_text)
    assert set(doc_info.keys()) == {
        "doc_version",
        "doc_title",
        "doc_date",
        "doc_author",
        "client",
        "vendor",
        "trackchange_section",
        "tp_top_logo",
        "tp_bottom_logo",
        "l_header_text",
        "l_header_image",
        "c_header_text",
        "c_header_image",
        "r_header_text",
        "r_header_image",
        "l_footer_text",
        "l_footer_image",
        "c_footer_text",
        "c_footer_image",
        "r_footer_text",
        "r_footer_image",
        "timezone",
    }
    assert doc_info.get("doc_version", "") == "1.0"
    assert doc_info.get("non_existent_key", "default") == "default"
