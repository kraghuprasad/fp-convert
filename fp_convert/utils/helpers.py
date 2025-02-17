import re
from typing import List, Optional

from freeplane import Node

# from peek import peek  # noqa: F401
from pylatex import MdFramed
from pylatex.base_classes import LatexObject
from pylatex.utils import NoEscape

from ..errors import InvalidDocInfoKey

"""
Utility functions and containers used in mindmap to LaTeX conversion.
"""

field_type_pat = re.compile(r" *(varchar|char|int|decimal) *[\[\(]([\.\d]+)[\)\]] *")


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


def append_notes_if_exists(
    node: Node,
    segment: List[LatexObject],
    doc,
    prefix: Optional[LatexObject] = None,
    suffix: Optional[LatexObject] = None,
):
    """
    Append notes to the supplied LaTeX segment from the supplied node, with
    optional prefix and suffix elements, provided it exists in the node. Then
    return that segment.

    If the node has a stop-sign icon, the notes are placed in a specially styled
    frame. Otherwise, the notes are appended with optional prefix and suffix
    elements, provided they are supplied.

    Parameters
    ----------
    node : Node
        The Freeplane node whose notes should be appended to the supplied
        segment
    segment : List[LatexObject]
        The list of LaTeX objects to append the notes to
    doc :
        The document being built
    prefix : LatexObject, optional
        Content to insert before the notes
    suffix : LatexObject, optional
        Content to insert after the notes

    Returns
    -------
    List[LatexObject]
        The modified list of LatexObjects with with the notes appended to it
    """
    # if node.id in doc.processed_nodes:
    #    return segment  # Return without any further processing

    if node.notes:
        # If stop-sign is present, then just create a red box to put the warning text,
        # ignoring prefix and suffix parts.
        if node.icons and "stop-sign" in node.icons:
            # segment.append(MdFramed(em(str(node.notes), node), options="style=StopFrame"))
            mdf = MdFramed()
            mdf.options = "style=StopFrame"
            mdf.append(NoEscape(rf"\small{{{doc.emr(str(node.notes), node)}}}"))
            segment.append(mdf)
        else:
            if prefix:
                segment.append(prefix)
            # Commenting out the following as lack of NoEscape is preventing references to be built correctly.
            # But applying NoEscape here may cause problems, if notes contain characters applicable to LaTeX.
            # Need a neater way to create references!!!
            # segment.append(build_para_per_line(em(str(node.notes), node), doc))
            segment.append(
                NoEscape(retrieve_note_lines(doc.emr(str(node.notes), node)))
            )
            if suffix:
                segment.append(suffix)
    return segment


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
        r"Prepared by using \href{https://www.github.com/kraghuprasad/fp-convert}"
        "{fp-convert}"
    )
    docinfo_tpl = {  # Statically defined field converter template for docinfo
        "Version": "doc_version",
        "Title": "doc_title",
        "Date": "doc_date",
        "Author": "doc_author",
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
    compiled_pat = re.compile(regex_pat)

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
        self._data = {v: None for v in DocInfo.docinfo_tpl.values()}
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
        Get the value for a valid key from the DocInfo object. If not found,
        then return supplie default value.

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


class DBTableField:
    """
    Class to represent a field in a database table.
    """

    def __init__(
        self,
        mangled_info: Optional[str] = None,
        name: Optional[str] = None,
        field_type: Optional[str] = None,
        ai: Optional[str] = None,
        pk: Optional[str] = None,
        unique: Optional[str] = None,
        default: Optional[str] = None,
        null: Optional[str] = None,
        notes: Optional[List[str]] = None,
    ):
        """
        The constructor can take either exact attributes of the field, or it
        can try to derive individual details from the input parameter named
        mangled_info.

        Parameters
        ----------
        mangled_info : str, optional
            The full details of the field can be supplied in a single string
            following certain convention. For example, following is a valid
            mangled_info string:
                email: varchar(64), unique=yes, null=no, desc=Email address
                This string will be parsed to extract the name, filed_type,
                description, unique and default values, if supplied.
            name: str, optional
                The name of the field of the table.
            field_type: str, optional
                The data-type of the field of the table.
            ai: str, optional
                If yes, the field value is auto incrementing.
            pk: str, optional
                The field is primary key of that table.
            unique: str, optional
                If yes, the field's value must be unique in the table.
            default: str, optional
                The default value used, if it is not supplied for this field.
            null: str, optional
                If yes, this field allows null values. Default is True.
            notes: List[str], optional
                The list of notes associated with this field.
        """
        self.name = name
        self.field_type = field_type
        self.ai = ai
        self.pk = pk
        self.unique = unique
        self.default = default
        self.null = null
        if notes:
            self.notes = retrieve_note_lines(notes)
        else:
            self.notes = list()

        if mangled_info:
            self._retrieve_mangled_info(mangled_info)
        else:
            if not (name and field_type):
                raise ValueError(
                    "Either mangled_info, or name, field_type, and other"
                    "applicable details must be supplied while constructing"
                    "the table-field."
                )

    def append_notes(self, notes: str):
        """
        Method to append a note-string to the existing notes container.
        """
        self.notes.append(notes)

    def _retrieve_mangled_info(self, info: str):
        """
        Method to retrieve the field-specific details from a single string
        which was written following certain conventions. One such valid string
        is given below:
            email: varchar(64), unique=True, null=False, desc=Email address

        Parameters
        ----------
        info : str
            The string containing the field-specific details.

        returns: Nothing. It modifies the attributes of the object in-place.
        """
        f_name, f_rest = info.split(":", 1)
        if f_rest:
            self.name = str.strip(f_name)
            for item in f_rest.split(","):
                # part1, part2 = item.split("=", 1)
                part = str.strip(item)
                part_lower = part.lower()
                if part_lower in ["ai", "autoincrement", "autoincrementing"]:
                    self.ai = "yes"
                elif part_lower in ["primarykey", "pk", "primary-key"]:
                    self.pk = "yes"
                elif part_lower in ["unique", "uq"]:
                    self.unique = "yes"
                elif part_lower in [
                    "null",
                ]:
                    self.null = "yes"
                elif re.match("not +null", part_lower):
                    self.null = "no"
                elif part_lower.startswith("default"):
                    parts = re.split(" +", part, maxsplit=1)
                    if len(parts) == 1:
                        raise ValueError(
                            f"No default value supplied for field {self.name}."
                            "Please supply default value in the format"
                            "'default xxx' or remove the keyword default."
                        )
                    self.default = str.strip(parts[1])
                elif part_lower in {
                    "int",
                    "tinyint",
                    "int8",
                    "int16",
                    "int32",
                    "int64",
                    "float",
                    "text",
                    "date",
                    "datetime",
                    "char",
                    "boolean",
                    "bool",
                    "smallint",
                    "mediumint",
                    "bigint",
                    "double",
                    "decimal",
                    "real",
                    "json",
                    "enum",
                    "integer",
                    "time",
                    "timestamp",
                    "geocolumn",
                }:
                    self.field_type = part_lower
                else:
                    mpat = field_type_pat.match(part_lower)
                    if mpat:
                        db_type, size = mpat.group(1), mpat.group(2)
                        self.field_type = f"{db_type}[{size}]"
                    else:
                        raise ValueError(
                            "Invalid mangled_info value supplied. Please follow"
                            " proper convention while writing the field-specifications."
                            " A sample valid mangled_info string is:"
                            " email: varchar(64), null=False, ds=Email addresse,"
                        )


class DBTable:
    """
    Class to represent a table in a relational database.
    """

    def __init__(self, name: str, fields: List[DBTableField] = None, notes: str = None):
        """
        The constructor takes the name of the table and the list of fields
        that it contains.

        Parameters
        ----------
        name: str
            The name of the table.
        fields: List[DBTableField]
            A list of DBTableField objects representing the fields that the table
            contains.
        notes: str
            The notes associated with the database table.
        """
        self.name = name
        if fields:
            self.fields = [i for i in fields]
        else:
            self.fields = list()
        if notes:
            self.notes = notes
        else:
            self.notes = list()

    def append_field(self, field: DBTableField):
        """
        Method to append a DBTableField object to this table.
        """
        self.fields.append(field)

    def append_notes(self, notes: str):
        """
        Method to append a note-text to the existing notes container.
        """
        self.notes.append(notes)

    def __repr__(self):
        """
        Method to return the string representation of the table.
        """
        return f"DBTable(name={self.name}, fields={self.fields})"

    def __str__(self):
        """
        Method to return the string representation of the table.
        """
        return f"DBTable(name={self.name}, fields={self.fields})"

    def __eq__(self, other):
        """
        Method to check if two tables are equal.
        """
        return self.name == other.name and self.fields == other.fields

    def __hash__(self):
        """
        Method to return the hash of the table.
        """
        return hash((self.name, self.fields))

    def __iter__(self):
        """
        Method to iterate over all the fields of this table.
        """
        return MyIterator(self.fields)


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
