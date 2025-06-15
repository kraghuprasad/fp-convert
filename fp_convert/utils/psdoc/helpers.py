"""
Helper functions for generating documents of type project specifications.
"""

import re
from typing import List, Optional

from freeplane import Node
from pylatex import NoEscape as NE

from fp_convert.utils.helpers import (
    DocContext,
    Theme,
    field_type_pat,
    # is_ignore_type,
    # is_image_type,
    # is_ordered_list_type,
    # is_unordered_list_type,
    node_type_detector_factory,
    retrieve_note_lines,
)


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
        self.notes = list()
        self.node: Optional[Node] = None  # The node representing this field in the mindmap
        if notes:
            self.notes.extend(notes)

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

    def __init__(
            self, name: str, fields: List[DBTableField]|None = None,
            notes: str|None = None):
        """
        The constructor takes the name of the table and the list of fields
        that it contains.

        Parameters
        ----------
        name: str
            The name of the table.
        fields: List[DBTableField]
            A list of DBTableField objects representing the fields that the table
            contains. Default is None.
        notes: str
            The notes associated with the database table.
        """
        self.name = name
        if fields:
            self.fields = [i for i in fields]
        else:
            self.fields = list()
        self.notes = list()
        if notes:
            self.notes.extend(retrieve_note_lines(notes))
        self.label: str = ""
        self.node: Optional[Node] = None  # The node representing this table in the mindmap

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


node_type_codes = {
    "tc": {  # Track-Change
        "icons": {
            "emoji-1F53B",
        },
        "attr": "trackchange",
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
    "sf": {  # Stop-Frame
        "icons": {
            "stop-sign",
        },
        "attr": "stopframe",
    },
}

# Create detector functions for node-types
is_trackchange_type = node_type_detector_factory("tc", node_type_codes)
is_verbatim_type = node_type_detector_factory("vb", node_type_codes)
is_table_type = node_type_detector_factory("tb", node_type_codes)
is_dbschema_type = node_type_detector_factory("db", node_type_codes)
is_stopframe_type = node_type_detector_factory("sf", node_type_codes)
is_numbertable_type = node_type_detector_factory("nt", node_type_codes)


def get_applicable_flags(node: Node, ctx: DocContext, theme: Theme):
    """
    Check if supplied node has any applicable flags like for deletion or
    addition of text-blocks or graphical elements etc. and return a list
    with appropriate flags, icons or notes. If no flags are present, then
    return an empty list.

    Parameters:
        node: Node
            The node whose applicable flags are to be checked and evaluated.
        ctx: DocContext
            The document context object associated with document being built.
        theme: Theme
            The theme object which contains various configuration parameters
            required to build the document.

    Returns:
        list[tuple(str, str, int)]
            A list of tuples of the following form:
            (flag-text, flag-type, index-position in the list)
            The last argument indicates the position of the entry in list like
            change-set so that a back reference to it can be included in the document
            at the pertinent location.
    """
    ret = list()

    # Check for deletion flag first and if not found then check for addition
    # as these two cases are mutually exclusive.
    if node.icons:
        if "button_cancel" in node.icons:
            flag = NE(
                rf"""\textcolor{{{ctx.regcol(theme.colors.del_mark_color)}}}{{%
{{\rotatebox{{10}}{{\tiny{{\textbf{{{theme.config.del_mark_text}}}}}}}}}%
{{{theme.config.del_mark_flag}}}}}"""
            )

            # Register the node for deletion
            ctx.changeset.append((node, "D"))
            ret.append((flag, "D", len(ctx.changeset) - 1))

        elif "addition" in node.icons:
            flag = NE(
                rf"""\textcolor{{{ctx.regcol(theme.colors.new_mark_color)}}}{{%
{{\rotatebox{{10}}{{\tiny{{\textbf{{{theme.config.new_mark_text}}}}}}}}}%
{{{theme.config.new_mark_flag}}}}}"""
            )

            # Register the node for addition
            ctx.changeset.append((node, "A"))
            ret.append((flag, "A", len(ctx.changeset) - 1))

    # If required, more flags can be handled here before returning
    return ret
