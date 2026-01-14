"""
Module to provide common utility classes and methods.
"""
from decimal import Decimal
import inspect
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
import subprocess
from types import ModuleType
from typing import Any, List, Dict, Callable, Optional, Set, Literal

from freeplane import Node

from pylatex import (
    Command,
    Figure,
    LongTable,
    MdFramed,
    MultiColumn,
    MultiRow,
)
from pylatex.base_classes import LatexObject
from pylatex.table import Tabular
from pylatex.utils import (
    bold,
    NoEscape as NE,
    escape_latex as EL,
)


from ..errors import (
    InvalidAttributeException, InvalidNodeException, InvalidRefException, InvalidDocInfoKey, InvalidFPCBlockTypeException, MissingHeaderException, MissingNodeException, MissingValueException
)
from ..utils.decorators import _get_local_flagged_nodes, register_color, track_flagged_nodes
from fp_convert.config import Config

"""
Utility functions and containers used in mindmap to LaTeX conversion.
"""

ref_pat = re.compile("(%ref[0-9]*%)")  # Regex pattern to match references
param_pat = re.compile("(%[^ %]+%)")

valid_ra_column_types = {  # Valid right-aligned column-types (numbers)
    "decimal", "number", "float", "integer", "percentage", "currency",
    "numeral", "int",
}
valid_la_column_types = {  # Valid left-aligned column-types (text)
    "text", "phone", "phonenumber", "contact", "contactnumber"
}

valid_node_type_codes = {
    "ol": {  # Ordered List
        "icons": {
            "emoji-1F522",
        },
        "attr": "orderedlist",
    },
    "ul": {  # Unordered List
        "icons": {
            "list",
        },
        "attr": "unorderedlist",
    },
    "ig": {  # Ignore-Block
        "icons": {
            "broken-line",
        },
        "attr": "ignore",
    },
    "im": {  # Image
        "icons": {
            "image",
        },
        "attr": "image",
    },
    "sf": {  # Stop-Frame
        "icons": {
            "stop-sign",
        },
        "attr": "stopframe",
    },
    "tc": {  # Track-Change
        "icons": {
            "emoji-1F53B",
        },
        "attr": "trackchanges",
    },
    "vb": {  # Verbatim
        "icons": {"links/file/xml", "links/file/json", "links/file/html"},
        "attr": "verbatim",
    },
    "tb": {  # Table
        "icons": {
            "links/file/generic",
        },
        "attr": "table",
    },
    "nt": {  # Number Table
        "icons": {
            "emoji-1F9EE",
        },
        "attr": "numbertable",
    },
    "db": {  # DB Schema
        "icons": {
            "links/libreoffice/file_doc_database",
        },
        "attr": "dbschema",
    },
    "up": {  # Usecase-System
        "icons": set(),
        "attr": "ucpackage",
    },
    "ur": {  # Usecase-Actors
        "icons": set(),
        "attr": "ucactors",
    },
    "ua": {  # Usecase-Action
        "icons": set(),
        "attr": "ucaction",
    },
    "ch": {  # Column-Headers
        "icons": set(),
        "attr": "columnheaders",
    },
    "td": {  # Table-Data
        "icons": set(),
        "attr": "tabledata",
    },
}

def node_type_detector_factory(
        type_code: str, node_type_codes: dict = valid_node_type_codes):
    """
    A special factory method which creates a type-detector function based on
    the input type specified.

    Parameters
    ----------
    type_code: str
        One of the pedefined type-codes for which there is a special way to
        render its text in the PDF document.
    node_type_codes: dict
        A container of type-codes and their associated data.

    Returns
    -------
    function
        The type-detector function.

    Notes
    -----
    The node can be annotated with either using a predefined set of icons or
    via attribute named fpcBlockType. It values are case insensitive and should
    be one defined in node_type_codes container: orderedlist, unorderedlist,
    verbatim, table, dbschema, unorderedlist, orderedlist, project, and similar
    types of nodes.
    """

    def detector(node: Node):
        try:  # Check for attributes first
            if (
                node.attributes["fpcBlockType"].lower()
                == node_type_codes[type_code]["attr"]
            ):
                return True
        except KeyError:
            pass

        # If required attribute not found, then check node-icons
        if node.icons and set(node.icons).intersection(
            node_type_codes[type_code]["icons"]
        ):
            return True

        # Node-type indicators are either missing or it is different than
        # the supplied one
        return False

    if type_code in node_type_codes:
        return detector

    raise InvalidFPCBlockTypeException(  # Supplied type_code is not supported.
        f"Code {type_code} is not found in the node-type-codes dictionary."
    )

# Create detector functions for various fpcBlockType values
is_ordered_list_type = node_type_detector_factory("ol")
is_unordered_list_type = node_type_detector_factory("ul")
is_ignore_type = node_type_detector_factory("ig")
is_image_type = node_type_detector_factory("im")
is_stopframe_type = node_type_detector_factory("sf")
is_trackchanges_type = node_type_detector_factory("tc")
is_verbatim_type = node_type_detector_factory("vb")
is_table_type = node_type_detector_factory("tb")
is_dbschema_type = node_type_detector_factory("db")
is_numbertable_type = node_type_detector_factory("nt")
is_ucpackage_type = node_type_detector_factory("up")
is_ucactors_type = node_type_detector_factory("ur")
is_ucaction_type = node_type_detector_factory("ua")
is_columnheaders_type = node_type_detector_factory("ch")
is_tabledata_type = node_type_detector_factory("td")


# Valid attributes for mindmap-nodes
valid_node_attr_names = {
    "Accountables",
    "BlockType",
    "DeliveryDate",
    "Id",
    "IsActive",
    "NotesPosition",
    "RequirementType",
    "RiskTypes",
    "ShowCaption",
    "UCPDirection",
    "ColumnType",
    "SumIt",
}

def fpc_attr_fetcher_factory(
        attr_name: str,
        lower_case: bool = True) -> Callable[[Node, str], str]:
    """
    A special factory method which creates a fetcher function based on the
    attribute-name supplied to it. The fetcher function converts the values
    of concerned attribute to lowercase, and returns it.

    Parameters
    ----------
    attr_name: str
        One of the predefined attribute-names like "BlockType", "NotesPosition",
        "IsActive", etc. for which corresponding attributes like fpcBlockType,
        fpcNotesPosition, fpcIsActive, etc. are expected in the nodes of the
        mindmap.
    lower_case: bool
        Whether to convert the attribute-value to lowercase or not.

    Returns
    -------
    function
        The value-fetcher function for supplied attribute-name.
    """
    global valid_node_attr_names
    if attr_name not in valid_node_attr_names:
        raise InvalidAttributeException(
            f"Supplied attribute-name '{attr_name}' is not a valid one. "
            "Please ensure that it is one of the following:\n"
            f"{valid_node_attr_names}")

    def fetcher(node: Node, default: str = None):
        """
        Fetch value of the supplied attribute in lower case, or return the
        supplied default value in lower case.
        
        Parameters
        ----------
        node: Node
            The node whose attribute is to be fetched.
        default: str
            The default value to be returned if the node-attribute is not found.
        Returns
        -------
        str
            The value of the node-attribute (in applicable case) or default.
        """
        if lower_case:
            try:
                return str.lower(node.attributes[f"fpc{attr_name}"])
            except KeyError:
                # return str(default)
                return str.lower(default) if default is not None else None
        return node.attributes.get(f"fpc{attr_name}", default)

    return fetcher

# Functions to fetch value of given attribute from a node. The second argument
# of the RHS function indicates if the attribue(value) should be converted to
# lower case before returning it.
get_fpc_accountables = fpc_attr_fetcher_factory("Accountables", False)
get_fpc_block_type = fpc_attr_fetcher_factory("BlockType")
get_fpc_delivery_date = fpc_attr_fetcher_factory("DeliveryDate", False)
get_fpc_id = fpc_attr_fetcher_factory("Id", False)
get_fpc_is_active = fpc_attr_fetcher_factory("IsActive")
get_fpc_notes_position = fpc_attr_fetcher_factory("NotesPosition")
get_fpc_requirement_type = fpc_attr_fetcher_factory("RequirementType", False)
get_fpc_risk_types = fpc_attr_fetcher_factory("RiskTypes", False)
get_fpc_show_caption = fpc_attr_fetcher_factory("ShowCaption")
get_fpc_ucp_direction = fpc_attr_fetcher_factory("UCPDirection")
get_fpc_column_type = fpc_attr_fetcher_factory("ColumnType")
get_fpc_sum_it = fpc_attr_fetcher_factory("SumIt")

def get_direction(direction: str) -> Literal["n", "s", "e", "w"]:
    """
    Interpret the input string as a direction (compass point).

    Parameters
    ----------
    direction : str
        The input string to interpret.

    Returns
    -------
    str
        One of the values "n", "s", "e", "w".

    Raises
    ------
    ValueError
        If the input cannot be interpreted as a direction.
    """
    direction_lower = direction.strip().lower()
    if direction_lower in {"s", "south"}:
        return "s"
    elif direction_lower in {"n", "north"}:
        return "n"
    elif direction_lower in {"e", "east"}:
        return "e"
    elif direction_lower in {"w", "west"}:
        return "w"
    raise ValueError(f"Cannot interpret '{direction}' as a valid direction.")

def to_bool(value: str) -> bool:
    """
    Interpret the input value as a boolean.

    Parameters
    ----------
    value : str
        The input value to interpret.

    Returns
    -------
    bool
        True if the input matches any true-like values, False if it matches any false-like values.

    Raises
    ------
    ValueError
        If the input cannot be interpreted as true or false.
    """
    true_values = {"y", "yes", "1", "t", "true"}
    false_values = {"n", "no", "0", "f", "false"}
    
    value_lower = value.strip().lower()
    if value_lower in true_values:
        return True
    elif value_lower in false_values:
        return False
    raise ValueError(f"Cannot interpret '{value}' as boolean.")


def compact_string(string: str) -> str:
    """
    Compact the string by removing leading and trailing whitespaces, and
    replacing multiple spaces with a single space.

    Parameters
    ----------
    string : str
        The string to be compacted.

    Returns
    -------
    str
        The compacted string.
    """
    return re.sub(r"\s+", " ", str.strip(string)) if string else ""


def ensure_directory_exists(dir_path: Path|str) -> None:
    """
    Ensure that the directory exists, creating it if necessary.

    Parameters
    ----------
    dir_path : Path | str
        The path to the directory to ensure existence of.
    """
    dir_path = Path(dir_path)
    if dir_path.exists():
        if dir_path.is_dir():
            return
        else:
            raise FileExistsError(
                f"Path {dir_path} exists but is not a directory."
            )
    else: 
        dir_path.mkdir(parents=True, exist_ok=True)


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
    return [str.strip(i) for i in text.split("\n") if str.strip(i)]

# TODO: Fix function-naming to avoid the following. Make name more generic
# like retrieve_lines() or retrieve_text_lines() or get_lines().
retrieve_node_lines = retrieve_note_lines

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
    building the document. It mimics a standard dictionary, with keys as
    ``doc_version``, ``doc_date`` and ``doc_author`` etc.

    The storage, deletion, and contains-check of a is done via proxy keys which
    are not actually present in the storage container. But the values are
    retrieved via actual keys against which they are stored. The proxy and
    actual keys are mapped via class variable ``docinfo_tpl``. The retrievals
    are done only via document template classes, and hence actual keys are used
    from within its code only, while the storage keys are obtained from mindmap
    and hence, they are passed through stricter checks.

    Parameters
    ----------
    docinfo_tpl : dict
        Template dictionary mapping document info field names to internal storage keys.
        Used to convert between external field names (e.g. "Version") and internal keys
        (e.g. "doc_version").
    regex_pat : str
        Regular expression pattern used to match document info fields in the input text.
        Pattern matches field name followed by colon and value.
    compiled_pat : re.Pattern
        Compiled regular expression pattern for matching document info fields.
        Pre-compiled for efficiency when processing multiple lines.
    _data : dict
        Internal storage dictionary containing the document info values.
        Keys are the internal storage keys, values are the field values.
    """

    credits = (
        r"Generated by \href{https://www.github.com/kraghuprasad/fp-convert}"
        "{fp-convert}"
    )
    docinfo_tpl = {  # Statically defined field converter template for docinfo
        "Version": "doc_version",
        "Title": "doc_title",
        "Template": "template",
        "Date": "doc_date",
        "Author": "doc_author",
        "Organization": "organization",
        "Client": "client",
        "Vendor": "vendor",
        "Trackchange_Section": "trackchange_section",
        "TP_Top_Logo": "tp_top_logo",
        "TP_Bottom_Logo": "tp_bottom_logo",
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
        "Timezone": "timezone",  # The timezone used for all auto-generated dates
    }
    regex_pat = "^(" + "|".join([k for k in docinfo_tpl.keys()]) + ") *:(.+)$"
    compiled_pat = re.compile(regex_pat)  # Regular expression pattern to match docinfo fields

    def __init__(self, info_text: str):
        """
        Initialize a DocInfo object to store document metadata. It mimics the interface of a
        standard Python dictionary.

        The DocInfo class manages document metadata like version, date, author, headers,
        footers etc. It provides a mapping between user-friendly field names (e.g. "Version")
        and internal storage keys (e.g. "doc_version").

        Document info is parsed from a text string containing fields in the format:
        Field_Name: value

        Parameters
        ----------
        info_text : str
            Text containing document metadata fields in Field_Name: value format.
            Can be empty/None in which case all fields are initialized to None.
        """
        self._data = {v: "" for v in DocInfo.docinfo_tpl.values()}
        self._data["timezone"] = "UTC"

        if info_text:
            for line in retrieve_note_lines(info_text):
                mpats = DocInfo.compiled_pat.search(line)
                if mpats:
                    self._data[DocInfo.docinfo_tpl[str.strip(mpats[1])]] = str.strip(
                        mpats[2]
                    )

    def get(self, key, default):
        """
        Get the value for a valid key from the DocInfo object. If %% is found to be
        the returned value, then return an empty string. If no values were found,
        then return supplied default value.

        Parameters
        ----------
        key : str
            The key for which the value is to be retrieved.

        default : object
            The object to be returned, if matching key not found.

        Returns
        -------
        object:
            The value-object associated with supplied key, or if it doesn't
            exit, then supplied default.
        """
        try:
            if self._data[key] == "%%":
                return ""
            return self._data[key]
        except KeyError:
            return default

    def __getitem__(self, key: str):
        """
        Get the value for a valid key from the DocInfo object.

        Parameters
        ----------
        key : str
            The key for which the value is to be retrieved.

        Returns
        -------
        str
            The value associated with the key.

        Raises
        ------
        KeyError
            If supplied key is not found in the DocInfo object.
        """

        return self._data[key]

    def __setitem__(self, key: str, value: str):
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
            self._data[DocInfo.docinfo_tpl[key]] = value
        else:
            raise InvalidDocInfoKey(f"Invalid DocInfo key: {key}")

    def __delitem__(self, key: str):
        """
        Delete the value associated with a valid key from the DocInfo object.

        Parameters
        ----------
        key : str
            The key for which the value is to be deleted.

        Raises
        ------
        KeyError
            If supplied key is not found in the DocInfo object.
        """

        del self._data[DocInfo.docinfo_tpl[key]]

    def __contains__(self, key: str):
        if DocInfo.docinfo_tpl.get(key, None):
            return DocInfo.docinfo_tpl[key] in self._data
        return False

    def __len__(self):
        """
        Return the number of items in the DocInfo object.

        Returns
        -------
        int
            The number of items in the DocInfo object.
        """

        return len(self._data)

    def __str__(self):
        """
        Return the string representation of the DocInfo object.

        Returns
        -------
        str
            The string representation of the DocInfo object.
        """

        return str(self._data)

    def __repr__(self):
        """
        Return the string representation of the DocInfo object.

        Returns
        -------
        str
            The string representation of the DocInfo object.
        """

        return str(self._data)

    def keys(self):
        """
        Return the actual keys as maintained in the DocInfo object.

        Returns
        -------
        list[str]
            The list of actual keys of the DocInfo object.
        """

        return self._data.keys()

    def values(self):
        """
        Return the values as maintained in the DocInfo object.

        Returns
        -------
        list[str]
            The list of values stored in the DocInfo object.
        """

        return self._data.values()

    def items(self):
        """
        Return the items as maintained in the DocInfo object.

        Returns
        -------
        list[tuple[str, str]]
            The list of actual key-value pairs stored in the DocInfo object.
        """

        return self._data.items()


def truncate_string(string: str, max_length: int) -> str:
    """
    Function to create a truncated string from a given string.

    Parameters
    ----------
    string: str
        The string to be truncated.
    max_length: int
        The maximum length of the truncated string.

    Returns
    -------
    str
        The truncated string.
    """
    if len(string) > max_length:
        # return string[: max_length - 3] + "\u2026"
        return string[: max_length - 3] + "..."
    else:
        return string


def special_truncator_factory(max_length: int):
    """
    Special factory method to create a truncator function which also removes
    the colon, if it exists at the end of the string.

    Parameters
    ----------
    max_length: int
        The maximum length of the truncated string.

    Returns
    -------
    function
        The truncator function.
    """

    def truncator(string: str):
        return re.sub(":$", "", truncate_string(string, max_length))

    return truncator


# Create truncator functions for strings with limited size
trunc80 = special_truncator_factory(80)
trunc32 = special_truncator_factory(32)
trunc18 = special_truncator_factory(18)


def build_latex_figure_object(
    image_path: PurePosixPath,
    image_width: str,
    image_caption: str | None = None,
    image_position: str = "!htb",
):
    """
    Return a LaTeX Figure object containing supplied figure, and
    layouts based on the supplied configuration.

    Parameters
    ----------
    image_path: PurePosixPath
        A PurePosixPath object pointing to the image file. The pdflatex wants
        pure posix paths only.
    image_width: str
        The width of the image expected in output.
    image_caption: str
        The caption of the image (optional).
    image_position: str
        Preferred position for image to be defined in LaTeX.

    Returns
    -------
    A LaTeX Figure object.
    """
    fig = Figure(position=image_position)
    fig.append(
        NE(
            rf"""
\begin{{center}}%
\tcbox{{\includegraphics[%
width={image_width}]{{{image_path}}}}}%
\end{{center}}%"""
        )
    )  # Build a boxed figure
    if image_caption is not None:
        fig.add_caption(image_caption)
    return fig


@dataclass
class DocContext:
    """
    It holds the context specific details which can be used by modules rendering
    various types of document-elements.
    """

    docinfo: DocInfo
    hypertargets: Set = field(default_factory=set)
    changeset: List = field(default_factory=list)
    colors: list[tuple[str, str, str]] = field(default_factory=list)
    changeset_section: str | None = field(default=None)
    changeset_node: Node | None = field(default=None)
    working_dir: Path | None = field(default=None)
    images_dir: Path | None = field(default=None)
    list_type_stack: List[str] = field(default_factory=list)

    # A container is required to store the margin comments when they are
    # generated inside LaTeX floats. They would be flushed outside the floats.
    in_floating_environment: List[int] = field(default_factory=list)
    margin_comments: Dict[str,str] = field(default_factory=dict)

    @register_color
    def regcol(self, color):
        """
        Register supplied color to the document-context before proceeding
        """
        return color
    
    def flush_margin_comments(
        self,
        comments: List[tuple[str, str]],
        ret: List[str|LatexObject|NE]) -> None:
        """
        Function to flush-out margin-comments to the document being built.

        Parameters
        ----------
        self: DocContext
            The document-context.
        comments: List[tuple[str, str]]
            A list of tuple of two strings containing the margin-comments to
            be flushed, along with applicable identifiers of node and
            change-set-types, if any.
        ret: List[str|LatexObject|NE]
            A list of strings, LaTeX objects, or NE objects representing the
            content of the document being built at the moment, which could be
            used to flush out the margin-comments, provided that currently no
            floating environment is being constructed.

        returns
        -------
        None
        """
        if comments:  # Proceed only if comment-list is non-empty
            if self.in_floating_environment:
                for c in comments:
                    self.margin_comments[c[1]] = c[0]
            else:
                ret.extend([c[0] for c in comments])
        
def retrieve_number_table_data(node: Node, ctx: DocContext) -> Dict[str, Any]:
    """
    Fetch the data required to build a number-table from the supplied node.

    Parameters
    ----------
    node: Node
        The node from which and its children, the data required to build the
        number-table is to be retrieved.
    ctx: DocContext
        The document-context object used to build the document.

    Returns
    -------
    dict: Dict[str, Any]
        A dictionary containing the data required to build a number-table.
        Following keys are maintained in it:
            alingnments: List[str]
            headers: List[str]
            rows: List[List[str]]
            totals: Dict[str, Decimal]
            notes: List[str]
            tblprops: Dict[str, str]
    """
    ret = dict()

    if node.children:
        ret["alignments"] = alignments = ["l", ]  # Alignment specifications for column-values
        ret["headers"] = headers = list()  # List of table-headers
        ret["rows"] = rows = list()  # List of rows with column-values
        ret["totals"] = totals = dict()  # Dict for storing sum of column-values
        ret["notes"] = notes = list()  # List of notes (if they exist)
        ret["tblprops"] = tblprops = {  # Valid table-properties (only one now)
            "column1": "",  # Header for first column
        }
        for child in node.children:
            if is_ignore_type(child):
                continue

            if is_columnheaders_type(child):  # Process column-headers
                note_lines = retrieve_note_lines(child.notes)
                for line in note_lines:
                    try:
                        key, val = [
                            str.strip(x) for x in line.split(":", 1)
                        ]
                        key = str.lower(key)
                        if key in tblprops:
                            tblprops[key] = val
                    except ValueError:
                        pass

                # Build a list of column-headers
                if child.children:
                    for item in child.children:
                        headers.append(str(item))
                        col_type = get_fpc_column_type(item)
                        if col_type in valid_ra_column_types:
                            alignments.append("r") # Right align the values
                            # if to_bool(get_fpc_sum_it(item)):
                            sum_it_val = get_fpc_sum_it(item, "false")
                            if sum_it_val and to_bool(sum_it_val):
                                totals[str(item)] = 0
                        elif col_type in valid_la_column_types:
                            alignments.append("l") # Left align the values
                        else:
                            raise ValueError(
                                f"Invalid column-type '{col_type}' found for "
                                "column-header '{item}'. Valid column-types "
                                f"are either one of {valid_la_column_types} "
                                "which would be aligned left to the column or "
                                f"one of number-types {valid_ra_column_types} "
                                "which would be aligned right and could be "
                                "summed-up too."
                            )
                else:
                    raise MissingHeaderException(
                        f"No child-nodes defined for the node '{child}' "
                        f"(ID: {child.id}) which is of type ColumnHeaders. "
                        "A number table can not be built without column-headers "
                        "getting defined in those child-nodes."
                    )
            elif is_tabledata_type(child):  # Process table-data
                if not child.children:
                    raise InvalidNodeException(
                        f"No child-nodes defined for the node '{child}' "
                        f"(ID: {child.id}) which is of type TableData. "
                        "A number table can not be built without table-data "
                        "getting defined in those child-nodes."
                    )
                note_lines = get_processed_note_lines(child, ctx)
                for field in child.children:
                    row = [NE(fr"\small{{{EL(field)}}}"), ]
                    if field.children:
                        for aln, hdr, val in zip(
                            alignments[1:], headers, field.children
                        ):
                            row.append(NE(fr"\small{{{EL(val)}}}"))
                            if aln == "r":
                                if hdr in totals:
                                    totals[hdr] += Decimal(str(val))
                        if len(row) != len(headers) + 1:
                            raise MissingValueException(
                                'Field-count mismatch in number-table '
                                f'"{str(node)}" for its row "{str(field)}". '
                                'According to its header-node, there should '
                                f'have been {len(headers)} children for this '
                                f'node, but found only {len(row)-1} instead.')
                    else:  # No fields for this node, and hence empty row
                        for item in headers:
                            row.append(NE(""))
                    rows.append(row)

                    if field.notes:
                        note_lines = retrieve_note_lines(field.notes)
                        field_notes = list()
                        for line in note_lines:
                            line_blocks = list()
                            for item in expand_macros(line, field, ctx):
                                line_blocks.append(item)
                            field_notes.append(line_blocks)
                        notes.append((field, field_notes))
    else:
        raise MissingNodeException(
            f"No child-nodes defined for the node '{node}'"
            f"(ID: {node.id}) which is of type NumberTable. A number-table "
            "can not be built for a node of type NumberTable, unless it has "
            "nodes of type ColumnHeaders and TableData as its child-nodes."
        )
    return ret


def retrieve_table_and_notelist(node: Node, config: Config, ctx: DocContext):
    """
    Retrieve table-data and associated field-notes from a Freeplane node, and
    return in a list.

    Parameters
    ----------
    node : Node
        The Freeplane node from which table-data and notes are to be retrieved
    config : Config
        The configuration object used to build the the document
    ctx : DocContext
        The context of the document being built

    Returns
    -------
    list[Tabular, list[tuple[Node, list[str]]]]
        A list of two elements: a LaTeX Taublar object and a list of tuples
        associated with the table-fields in it.
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
                    field_notes = list()
                    for line in retrieve_note_lines(str(field.notes)):
                        field_notes.append(expand_macros(line, field, ctx))
                    notes.append((field, field_notes))

        col_hdrs = sorted(list({e for d in col1.values() for e in d.keys()}))

        # Build table-content first
        tab = Tabular("l" * (1 + len(col_hdrs)), pos="c")
        tab.add_hline(color=ctx.regcol(config.table.line_color))
        tab.add_hline(color=ctx.regcol(config.table.line_color))
        col1_hdr = re.sub(r":$", "", str(node))
        row = [
            NE(
                fr"""
\small{{\color{{{ctx.regcol(config.table.header_text_color)}}}%
\textsf{{{col1_hdr}}}}}"""
            ),
        ]
        row.extend(
            [
                NE(fr"""
\small{{\color{{{ctx.regcol(config.table.header_text_color)}}}%
\textsf{{{hdr}}}}}"""
                ) for hdr in col_hdrs
            ]
        )
        tab.add_row(
            *row,
            color=ctx.regcol(config.table.header_row_color),
            strict=True)
        tab.add_hline(color=ctx.regcol(config.table.line_color))
        for field in sorted(col1.keys()):
            row = [field, ]
            for col in col_hdrs:
                row.append(col1[field].get(col, ""))
            tab.add_row(row)
        tab.add_hline(color=ctx.regcol(config.table.line_color))

        # Then check if notes are to be collected for the same node
        if notes:
            return [tab, notes]
        return [tab, ]

    # Empty list is returned by default, if no children are present for that
    # node.
    return list()

# TODO: Refactor psdoc.py to remove get_hypertarget from it, and use this
# function there instead.
def get_hypertarget(node: Node, ctx: DocContext) -> NE|None:
    """
    Generate the hypertarget for the supplied node.

    Parameters:
        node: Node
            The node for which the hypertarget is to be generated.
        ctx: DocContext
            The document-context object to append to its hypertarget-list.

    Returns:
        NE|None
            The hypertarget command wrapped in NE or None
    """
    if node not in ctx.hypertargets:
        ctx.hypertargets.add(node)
        return Command("hypertarget", arguments=(get_label(node.id), ""))
    return None

def get_stopframe_block(node: Node, ctx: DocContext):
    """
    Generate the stopframe-block for the supplied node.

    Parameters:
        node: Node
            The node whose note-text would be used to create the content of
            stopframe-block
        ctx: DocContext
            The document-context object

    Returns:
        list[str|LatexObject|NE]
            A list of strings, LaTeX objects, or NE objects representing the
            content of stop-frame.
    """
    ret = list()
    note_lines = retrieve_note_lines(
        str(node.notes)) if str(node.notes) else None

    mdf = None
    if note_lines:
        mdf = MdFramed()
        mdf.options = "style=StopFrame"

        # Process first note-line
        for item in expand_macros(note_lines[0], node, ctx):
            mdf.append(Command("small", item))

        for line in note_lines[1:]:  # Process remaining note-lines, if any
            mdf.append("\n")
            for item in expand_macros(line, node, ctx):
                mdf.append(Command("small", item))

    if mdf:
        ret.append(mdf)
    
    if brefs := get_references(node, back_ref=True):
        ret.append(brefs)

    return ret

# TODO: Refactor psdoc.py to remove expand_macros from it, and use this
# function there instead.
def expand_macros(text: str, node: Node, ctx: DocContext):
    """
    Function to expand macros to get applicable reference-details. It is
    usually used to retrieve the reference-links from supplied node, and
    patch it in the returned content-list.

    Parameters
    ----------
    text : str
        The text from which the macros are to be extracted as well as expanded.
    node : Node
        The current node which would be searched to identify other nodes to
        which it refers to.
    ctx : DocContext
        The document-context of the document being processed.

    Returns
    -------
    list[LatexObject]
        A list of LaTeX objects representing the content after expanding the
        macros.
    """
    ret = list()
    segments = re.split(ref_pat, text)

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
                if not re.fullmatch(ref_pat, fr"{segment}"):
                    ret.append(EL(segment))
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
                if not re.fullmatch(ref_pat, segment):
                    ret.append(EL(segment))
                else:
                    try:
                        ret.append(refs[segment])
                        ret.append(Command("xspace"))
                    except KeyError:
                        raise InvalidRefException(
                            f"Node [{str(node)}(ID: {node.id})] with "
                            "multiple outgoing arrow-links is using an "
                            f"invalid node-reference ({segment}) in its "
                            "text or notes."
                        ) from None

        # Add a label to this node for back reference
        if ht := get_hypertarget(node, ctx):
            ret.append(NE(ht))

    else:  # No references are present in the supplied text
        #ret.append(segments[0])
        ret.append(EL(segments[0]))
    return ret
def get_applicable_flags(
    node: Node,
    ctx: DocContext,
    config: Config) -> list[tuple[NE, str, int, str]]:
    """
    Check if node has any applicable flags like for deletion or addition of
    text-blocks or graphical elements etc. and return a list with appropriate
    flags, icons or notes. If no flags are present, then return an empty list.

    Parameters:
        node: Node
            The node whose applicable flags are to be checked and evaluated
        ctx: DocContext
            The document context object associated with document being built
        config: Config
            The Config object from which flag-text sepecific configuration
            parameters are to be retrieved

    Returns:
        list[Optional[tuple[NE, str, int, str]]]
            A list of tuples of the following form:
            (flag-text, flag-type, index-position in the list, and node-id)
            The last but one argument indicates the position of the entry in
            list like change-set so that a back reference to it can be included
            in the document at the pertinent location. The last argument is the
            id of the node, which would be useful to remove duplicates getting
            printed while rendering the document.
    """
    ret = list()

    # Check for deletion flag first and if not found then check for addition
    # as these two cases are mutually exclusive.
    if node.icons:
        if "button_cancel" in node.icons:
            flag = NE(
                fr"""\textcolor{{{ctx.regcol(config.main.del_mark_color)}}}{{%
{{\rotatebox{{10}}{{\tiny{{\textbf{{{config.main.del_mark_text}}}}}}}}}%
{{{config.main.del_mark_flag}}}}}""")

            if node.id not in _get_local_flagged_nodes():
                # Register the node for deletion if not done already
                ctx.changeset.append((node, "D"))
            ret.append((flag, "D", len(ctx.changeset)-1, node.id))

        elif "addition" in node.icons:
            flag = NE(
                fr"""\textcolor{{{ctx.regcol(config.main.new_mark_color)}}}{{%
{{\rotatebox{{10}}{{\tiny{{\textbf{{{config.main.new_mark_text}}}}}}}}}%
{{{config.main.new_mark_flag}}}}}""")

            if node.id not in _get_local_flagged_nodes():
                # Register the node for addition
                ctx.changeset.append((node, "A"))
            ret.append((flag, "A", len(ctx.changeset)-1, node.id))

    # If required, more flags can be handled here before returning
    return ret


def get_flag_blocks(
        node: Node, config: Config,
        ctx: DocContext) -> List[Optional[Command|str]]:
    """
    Check if node has any applicable flags like for deletion or addition of
    text-blocks or graphical elements etc. If found, return it; else None.

    Parameters:
        node: Node
            The node whose applicable flags are to be checked and evaluated.
        config: Config
            The Config object which contains various configuration parameters
            required to build the document.
        ctx: DocContext
            The document context object associated with document being built.

    Returns: List[Optional[Command|str]]
            A list containing hypertarget(Command), if any, and flag-text
    """
    # Search and add any applicable flag related texts
    flags = get_applicable_flags(node, ctx, config)
    flagdata = [
        (x, f"CSREF:{z}", z)
            for x, y, z, node_id in flags if y == 'A' or y == 'D'
    ]
    fblocks = list()
    if len(flags):
        flagtexts = [x for x, y, z in flagdata]
        if ht := get_hypertarget(node, ctx):
            fblocks.append(ht)
        for x in flagtexts:
            fblocks.append(x)
    return fblocks

@track_flagged_nodes
def get_flag_refs(
        node: Node, config: Config, ctx: DocContext) -> list[NE]:
    """
    Return a list of non-escaped LaTeX blocks of strings containing the
    backreferences to records of track-change sections for the supplied node.

    Parameters:
        node: Node
            The node for which the back-reference is to be generated.
        config: Config
            The Config object to be used to render flag-text.
        ctx: DocContext
            The document context object associated with document being built.

    Returns:
        list[tuple(NE, str)]
            A list of tuples containing two values: non-escaped LaTeX block
            of strings containing the back-references to records found in the
            track-change table, and a string of flag-type and the applicable
            node-id separated by a hyphen.
    """
    # Search and add any applicable flag related texts
    flags = get_applicable_flags(node, ctx, config)
    flagdata = [
        (x, f"CSREF:{z}", z, node_id)
            for x, y, z, node_id in flags if y == 'A' or y == 'D'
    ]
    frefs = list()
    if len(flagdata) and ctx.docinfo["trackchange_section"]:
        for x, y, z, node_id in flagdata:
            frefs.append((NE(fr"\margincomment{{\tiny{{$\Lsh$ \hyperlink{{{y}}}"
                            fr"{{{ctx.docinfo["trackchange_section"]}"
                            fr": {z+1}}}}}}}"), f"{y}-{node_id}"))
    return frefs

def get_references(node: Node, back_ref: bool = False) -> list[tuple[NE, str]]:
    """
    Return a non-escaped LaTeX block of strings containing the reference of
    specified type for the supplied node. Else return None. Default is forward
    reference.
    
    Parameters:
        node: Node
            The node for which the back-reference is to be generated.
        back_ref: bool = False
            The type of reference to be generated. Based on this the
            arrow-indicator changes.

    Returns:
        list[tuple[NE, str]]
            A list of tuples, each containing a non-escaped LaTeX block with
            the reference and the referrer's node ID.
    """
    ret = list()
    arrows = node.arrowlinked if back_ref else node.arrowlinks
    for referrer in arrows:
        icon = "$\Lsh$" if back_ref else "$\Rsh$"
        ret.append(
            (
                NE(fr"\margincomment{{\tiny{{{icon} \hyperlink{{{get_label(
                referrer.id)}}}{{{trunc32(str(referrer))}}}}}}}"),
                referrer.id
            )
        )
    return ret


def get_processed_note_lines(
        node: Node, ctx: DocContext
    ) -> List[str|LatexObject|NE|List]:
    """
    Get the list of LaTeX objects, NE, string, or another similar list
    representing each of the lines of note-text with all macros expanded
    for the supplied node.

    Parameters
    ----------
    node : Node
        The node from which the note-text is to be retrieved. It must be
        from the same mindmap from which the document is being built.
    ctx: DocContext
        The document context object associated with document being built.

    Returns
    -------
    list[List[str|LatexObject|NE]]
        A list of list of strings, LaTeX objects, or NoEscape objects
        representing the lines of note-text.
    """
    ret = list()

    # If one or more note-lines exist, then process them
    if node.notes:
        for line in retrieve_note_lines(str(node.notes)):
            ret.append(expand_macros(line, node, ctx))
    return ret


def get_node_text_blocks(
        node: Node,
        config: Config,
        ctx: DocContext
    ) -> List[LatexObject | str | NE]:
    """
    Retrieve node-content in the form of a list of blocks of LaTeX objects
    from the supplied node while ensuring that flag-texts are duly included
    in them. It is used to build the text-blocks of non-section kinds of
    nodes.

    Parameters:
        node: Node
            The node from which the content is to be fetched
        config: Config
            The Config object which contains configuration parameters
        ctx: DocContext
            The document context object

    Returns:
        List[LatexObject | str | NE | EL]
            The content of the node along with flag-texts in a list of LaTeX
            objects or other forms suitable to get included in the document.
    """
    # Collect flag-specific text and back-references
    fblocks = get_flag_blocks(node, config, ctx)
    frefs = get_flag_refs(node, config, ctx)

    ret = list()

    # Prepare current node-specific content
    content = str(node).split(":", 1)
    if len(content) == 2:
        if fblocks:
            ret.extend(fblocks)
            ret.extend(
                [
                    Command("xspace"),
                    NE(bold(EL(content[0]))),
                ]
            )
        else:
            ret.append(NE(bold(EL(content[0]))))
        
        # Add a colon after first part, but only if there exists some text
        # in the second part of the content.
        node_content = str.strip(content[1])
        ret.append(": ") if node_content else None
    else:
        if fblocks:
            ret.extend(fblocks)
            ret.append(Command("xspace"))
        node_content = str.strip(content[0])

    ret.extend(expand_macros(node_content, node, ctx))
    # ret.append("\n")
    ctx.flush_margin_comments(frefs, ret)
    return ret


def get_note_text_blocks(
    node: Node,
    config: Config,
    ctx: DocContext
) -> List[Optional[Command|str]]:
    """
    Retrieve note-content from the supplied node while ensuring that all
    styles, including stop-frames are duly rendered in the returned string.

    Parameters:
        node: Node
            The node from which the content is to be fetched
        config: Config
            The Config object which contains configuration parameters
        ctx: DocContext
            The document context object

    Returns:
        List[Optional[Command|str]]
            A list containing one paragraph each for each line of notes
            duly formatted for stop-frames too, if any.
    """
    # Collect note-content after expanding macros, if any
    note_lines = get_processed_note_lines(node, ctx)
    note_list = list()
    if len(note_lines):
        # If stop-sign is present in that node, then style a framed box
        # accordingly.
        if is_stopframe_type(node):
            note_list.append(Command("savecurrentfontsize"))
            mdf = MdFramed()
            mdf.options = "style=StopFrame"
            for element in note_lines[0]:  # Process first note-line
                mdf.append(element)

            for line in note_lines[1:]:  # Process remaining note-lines, if any
                mdf.append("\n")
                for element in line:
                    mdf.append(element)

            note_list.append(mdf)
            note_list.append(Command("savedlastfontsize"))
        else:
            for element in note_lines[0]:  # Process first note-line
                note_list.append(element)

            for line in note_lines[1:]:  # Process remaining note-lines, if any
                note_list.append(Command("par"))
                for element in line:
                    note_list.append(element)

    return note_list

class MyIterator:
    """
    Class to implement a simple external iterator.
    An iterable object is required to construct the instance of this class.
    """

    def __init__(self, data):
        self.data = data
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.data):
            raise StopIteration
        item = self.data[self.index]
        self.index += 1
        return item


class KeyValuePairTable(Tabular):
    """A Tabular helper to render rows of (label, value) pairs as:
    l@{}cl per pair."""

    # Ensure the emitted environment is \begin{tabular}...\end{tabular}
    _latex_name = 'tabular'

    def __init__(self, num_pairs: int | None, **kwargs):
        """
        num_pairs: number of (label, value) pairs per row.
                   If None, it will be inferred from the first add_row(..) call.
        """
        self.num_pairs = num_pairs
        self._frozen = num_pairs is not None

        # Provide a placeholder spec if we don't yet know the number of pairs.
        # We'll overwrite self.table_spec as soon as the first row arrives.
        placeholder_spec = 'l' if num_pairs is None else ''.join(['l@{}cl'] * num_pairs)
        super().__init__(placeholder_spec, **kwargs)

    def _ensure_spec(self, pairs_count: int):
        if not self._frozen:
            self.num_pairs = pairs_count
            # Build the real spec: each (key, ":", value) → l@{}cl
            self.table_spec = ''.join(['l@{}cl'] * self.num_pairs)
            self.width = 3 * pairs_count
            self._frozen = True

    def add_row(self, *pairs):
        """
        Add a row of key–value pairs.
        Usage:
            table.add_row(("Mobile", "+12..."), ("Email", "x@y.com"))
        Also accepts a single dict:
            table.add_row({"Mobile": "+12...", "Email": "x@y.com"})
        """
        # Allow a single dict argument
        if len(pairs) == 1 and isinstance(pairs[0], dict):
            # Preserve insertion order (Py3.7+ dicts keep order)
            pairs = tuple(pairs[0].items())

        self._ensure_spec(len(pairs))

        if len(pairs) != self.num_pairs:
            raise ValueError(f"Expected {self.num_pairs} pairs, got {len(pairs)}")

        row_cells = []
        for key, value in pairs:
            row_cells.extend([key, NE(':'), value])
        return super().add_row(row_cells)

def is_actor_node(node: Node) -> bool:
    """
    Check if the supplied node is a usecase-actor node.

    Parameters:
        node: Node
            The node to be checked.

    Returns:
        bool: True if the node is a usecase-actor node, False otherwise.
    """
    if node:
        # Check if its parent is a usecase-actors node
        if node.parent and is_ucactors_type(node.parent):
            return True
    return False

def puml2svg(puml_cmd: str, puml_file: Path, output_dir: Path) -> None:
    """
    Convert a PlantUML file to SVG format.

    Parameters:
    puml_cmd: str
        The command to invoke PlantUML.
    puml_file: Path
        The path to the PlantUML file.
    output_dir: Path
        The directory where the SVG file will be saved.

    Raises:
    subprocess.CalledProcessError
        If the PlantUML conversion fails.
    FileNotFoundError
        If the PlantUML command is not found.
    """
    try:
        # Convert PUML to SVG using plantuml command line tool
        subprocess.run(
            [puml_cmd, '-tsvg', str(puml_file), '-o', str(output_dir)],
            check=True,
            capture_output=True,
            text=True
        )
    except FileNotFoundError:
        raise FileNotFoundError(f"PlantUML command '{puml_cmd}' not found")
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(
            e.returncode,
            e.cmd,
            output=e.stdout,
            stderr=f"PlantUML conversion failed: {e.stderr}"
        )

def build_ucaction_tabular_segments(action_nodes: List[Node]) -> List[LongTable] | None:
    """
    Build and return a tabular segment for the usecase actions.

    Parameters:
    action_nodes: List[Node]
        List of action nodes to be included in the tabular segment.
    """
    ret: List[LongTable] = []
    for action_node in action_nodes:
        if is_ignore_type(action_node) or not action_node.children:
            continue  # Skip if ignored or no conditions are present

        conditions: dict[Node, list[Node]] = {}
        for condition in action_node.children:
            if is_ignore_type(condition):
                continue  # skip if ignored

            flows: List[Node] = list()
            for flow in condition.children:
                if is_ignore_type(flow):
                    continue  # skip if ignored or no flows are present
                flows.append(flow)
            if flows:
                conditions[condition] = flows

        if not conditions:
            continue  # Nothing to do if relevant nodes are absent

        tbl_required = False  # Flag to check if tabular segment is required

        tbl = LongTable(
            r"|p{0.15\textwidth} p{0.78\textwidth}|"
            # "ll"
        )
        tbl.add_hline()
        tbl.add_row((MultiColumn(2, align='|c|', data=str(action_node)),))
        tbl.end_table_header()
        tbl.add_hline()

        # Build tabular conent having conditions and flow details
        for condition, flows in conditions.items():
            row_required = len(flows) >= 1
            for idx, item in enumerate(flows[:-1]):
                if row_required:
                    tbl.add_row("", f"{str(item)}")
                    tbl_required = True

            if row_required:
                # Add the multirow section at the end to ensure that row-text
                # always renders on top layer. Otherwise it may get hidden.
                tbl.add_row((MultiRow(NE(-abs(len(flows))), data=f"{str(condition)}"), f"{str(flows[-1])}"))
                tbl.add_hline()

        if tbl_required:
            ret.append(tbl) 
    return ret if len(ret) else None

def fetch_builders(mod: ModuleType) -> Dict[str, Callable]:
    """
    Fetch the list of builder-functions by matching certain patterns of
    function-names existing in supplied module.

    Parameters:
    mod: ModuleType
        The module to be scanned for builder-functions.
    
    Returns:
    Dict[str, Callable]
        A dictionary mapping pattern-matched names to their builder functions.
    """
    return {
            m.group(1): func for name, func in inspect.getmembers(
                mod, inspect.isfunction) if (
                    m := mod.builder_func_pat.match(name))
    }

def dump(x: LatexObject|NE|str):
    """
    Function to return the string representation of the supplied object.
    """
    if isinstance(x,LatexObject):
        return x.dumps()
    else:
        return str(x)

def list_exists_in_parent_path(
        node: Node, builders: Dict[str, Callable]) -> bool:
    """
    Check if the supplied node's parent or grand parents were ever of a
    list type.
    Parameters:
    node: Node
        The node whose parent-path is to be checked.
    builders: Dict[str, Callable]
        The dictionary of builder-functions to check if the supplied node
        is of a list-type, which would require one of the list builder
        function to build it.
    Returns:
    bool
        True if the supplied node's parent or grand parents were ever of
        a list type, False otherwise.
    """
    # func_name = builders[
    #     node.attributes.get("fpcBlockType", "default")].__name__
    func_name = builders[get_fpc_block_type(node, "default")].__name__
    if func_name in {
            "build_orderedlist_block", "build_unorderedlist_block"}:
        return True

    if node.parent:
        return list_exists_in_parent_path(node.parent, builders)

    # This is root-node. So no list existed in the path traversed so far
    return False
