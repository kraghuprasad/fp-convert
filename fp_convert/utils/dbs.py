"""
Module to provide common utility classes and methods for building DB Schema
blocks in the document.
Author: K. Raghu Prasad
License: GPL(v3)
"""

import re
from typing import List, Optional
from freeplane import Node
from pylatex import Itemize
from pylatex import escape_latex as EL

from fp_convert.utils.helpers import (
    MyIterator,    
    retrieve_note_lines
)

field_type_pat = re.compile(r"^\s*(varchar|char|int|decimal)\s*[\[\(]\s*([\d,\s]+)\s*[\)\]]\s*$")


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
                    "Either mangled_info, or name and field_type (and other applicable details) "
                    "must be supplied while constructing the table-field."
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

        # Revised version for rigourous testing
        try:
            f_name, f_rest = info.split(":", 1)
        except ValueError as e:
            raise ValueError("mangled_info must contain a ':' separating name and specifications.") from e

        self.name = str.strip(f_name)
        f_rest = f_rest.strip()

        def split_top_level_commas(s: str) -> List[str]:
            items, cur, depth = [], [], 0
            for ch in s:
                if ch in "([":
                    depth += 1
                elif ch in "])" and depth > 0:
                    depth -= 1
                if ch == "," and depth == 0:
                    items.append("".join(cur))
                    cur = []
                else:
                    cur.append(ch)
            if cur:
                items.append("".join(cur))
            return items

        KNOWN_TYPES = {
            "int", "tinyint", "int8", "int16", "int32", "int64", "float", "text", "date",
            "datetime", "char", "boolean", "bool", "smallint", "mediumint", "bigint",
            "double", "decimal", "real", "json", "jsonb", "enum", "integer", "time",
            "timestamp", "geocolumn", "varchar",
        }

        def as_yes_no(val: str) -> str:
            return "yes" if val.strip().lower() in {"1","true","t","yes","y"} else "no"

        tokens = split_top_level_commas(f_rest) if f_rest else []
        for raw in tokens:
            part = raw.strip()
            if not part:
                continue
            lower = part.lower()

            # NOT NULL (phrase) handling
            if re.search(r"\bnot\s+null\b", lower):
                self.null = "no"
                continue

            # key[:=]value pairs
            m = re.match(r"^\s*([a-z_-]+)\s*[:=]\s*(.+)\s*$", part, flags=re.IGNORECASE)
            if m:
                key = m.group(1).lower()
                val = m.group(2).strip()
                if key in {"ai","auto","autoincrement","autoincrementing"}:
                    self.ai = as_yes_no(val)
                elif key in {"pk","primarykey","primary-key","primary"}:
                    self.pk = as_yes_no(val)
                elif key in {"unique","uq"}:
                    self.unique = as_yes_no(val)
                elif key in {"null"}:
                    self.null = as_yes_no(val)
                elif key in {"default","def"}:  # default with = or : operator
                    self.default = EL(val)
                elif key in {"desc","description","note","notes"}:
                    self.notes.append(EL(val))
                else:
                    # Could be a type alias accidentally written as key=value; fall through validation below.
                    pass
                continue

            # Bare flags (ai, pk, unique, null)
            if lower in {"ai","autoincrement","autoincrementing"}:
                self.ai = "yes"; continue
            if lower in {"primarykey","pk","primary-key","primary"}:
                self.pk = "yes"; continue
            if lower in {"unique","uq"}:
                self.unique = "yes"; continue
            if lower == "null":
                self.null = "yes"; continue

            # default without = operator
            if lower.startswith("default "):
                _, val = lower.split(" ", 1)
                self.default = EL(val.strip())
                continue

            # Type with optional size/precision: varchar(64), int[11], decimal(10,2)
            mpat = field_type_pat.fullmatch(lower)
            if mpat:
                db_type, size = mpat.group(1), mpat.group(2)
                self.field_type = f"{db_type}[{size}]"
                continue

            # Plain type token
            if lower in KNOWN_TYPES:
                self.field_type = lower
                continue

            raise ValueError(
                f"Invalid mangled_info token '{raw}' encountered while parsing field-specifications. "
                "Example of a valid info: 'email: varchar(64), unique=True, null=False, desc=Email address'."
            )

        if not self.field_type:
            raise ValueError(f"Type not specified for field '{self.name}'.")


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
        self.notes.extend(retrieve_note_lines(notes))


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
        if not isinstance(other, DBTable):
            return NotImplemented
        return self.name == other.name and self.fields == other.fields

    def __hash__(self):
        """
        Method to return the hash of the table.
        """
        return hash((self.name, tuple(self.fields)))
    def __iter__(self):
        """
        Method to iterate over all the fields of this table.
        """
        return MyIterator(self.fields)

class DBItemize(Itemize):
    pass