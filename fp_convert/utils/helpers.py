"""
Module to provide common utility classes and methods.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set

from freeplane import Node

from pylatex import Figure, MdFramed
from pylatex.base_classes import LatexObject
from pylatex.utils import NoEscape as NE

from ..errors import InvalidDocInfoKey, InvalidFPCBlockTypeException
from ..utils.decorators import register_color

"""
Utility functions and containers used in mindmap to LaTeX conversion.
"""

field_type_pat = re.compile(r" *(varchar|char|int|decimal) *[\[\(]([\.\d]+)[\)\]] *")

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


def node_type_detector_factory(type_code: str, type_code_repo: dict):
    """
    A special factory method which creates a type-detector function based on
    the input type specified.

    Parameters
    ----------
    type_code: str
        One of the pedefined type-codes for which there is a special way to
        render its text in the PDF document.
    type_code_repo: dict
        The dictionary containing all type-codes applicable for respective
        module's node-types.

    Returns
    -------
    function
        The type-detector function.

    Notes
    -----
    The node can be annotated with either using a predefined set of icons or
    via attribute named fpcBlockType. It values are case insensitive and should
    be one defined in node_type_codes container: orderedlist, unorderedlist,
    verbatim, table, dbschema.
    """

    def detector(node: Node):
        try:  # Check for attributes first
            if (
                node.attributes["fpcBlockType"].lower()
                == type_code_repo[type_code]["attr"]
            ):
                return True
        except KeyError:
            pass

        # If required attribute not found, then check node-icons
        if node.icons and set(node.icons).intersection(
            type_code_repo[type_code]["icons"]
        ):
            return True

        # Node-type indicators are either missing or it is different than
        # the supplied one
        return False

    if type_code in type_code_repo:
        return detector

    raise InvalidFPCBlockTypeException(  # Supplied type_code is not supported.
        f"Code {type_code} is not found in given type-code-repo dictionary."
    )


node_type_codes = {
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
}
is_ordered_list_type = node_type_detector_factory("ol", node_type_codes)
is_unordered_list_type = node_type_detector_factory("ul", node_type_codes)
is_ignore_type = node_type_detector_factory("ig", node_type_codes)
is_image_type = node_type_detector_factory("im", node_type_codes)


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
    segment: List[LatexObject|NE],
    doc,
    prefix: Optional[LatexObject|NE] = None,
    suffix: Optional[LatexObject|NE] = None,
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
            mdf.append(NE(rf"\small{{{doc.emr(str(node.notes), node)}}}"))
            segment.append(mdf)
        else:
            if prefix:
                segment.append(prefix)
            # Commenting out the following as lack of NoEscape is preventing references to be built correctly.
            # But applying NoEscape here may cause problems, if notes contain characters applicable to LaTeX.
            # Need a neater way to create references!!!
            # segment.append(build_para_per_line(em(str(node.notes), node), doc))
            segment.append(NE(retrieve_note_lines(doc.emr(str(node.notes), node))))
            if suffix:
                segment.append(suffix)
    return segment


class ObjectMix:
    """
    Mix one or more objects together - still maintaining their separate
    existence - and fetch any attributes from them (based on priority) using
    standard object and attribute notations. The existence of attributes are
    tested in the same order, in which the objects are supplied to the its
    constructor. The higher priority objects must precede the lower priority
    ones while constructing this object. For example if attribute x exists in
    objects a and b both, and ObjectMix o is created as o = ObjectMix(a, b);
    then o.x will return the value of a.x, not that of b.x.

    Object of this class allows only retrieval of attribute-values, provided
    they are present in the object-mix. No attributes can be set using it. In
    short, it is a read-only object.
    """

    def __init__(self, *objects):
        """
        Initialize the ObjectMix with one or more objects. It ignores duplicates
        and maintains a set of unique objects. The order of objects is preserved
        in the list of objects, but the duplicates are ignored.
        Parameters
        ----------
        objects : objects
            One or more objects to be mixed.
        """
        self._repo = set()
        self._objects = []  # List to maintain the order of objects
        for obj in objects:  # ignore duplicates
            if obj not in self._repo:
                self._repo.add(obj)
                self._objects.append(obj)

    def add_object(self, obj):
        """
        Add an object to the ObjectMix. If the object is already present, it is
        ignored. This allows extending the ObjectMix with new objects at runtime
        with default values for those attributes which are missing in the objects
        added earlier.

        Parameters
        ----------
        obj : object
            The object to be added to the ObjectMix. It can be any configuration
            object which has predefined attributes in it. For example, an instance
            of Config class can have attributes like `toc_depth`, `sec_depth`, etc.
        """
        if obj not in self._repo:  # ignore duplicates
            self._repo.add(obj)
            self._objects.append(obj)
    
    def dump(self) -> dict[str, dict[str, str]]:
        """
        Dump the content of this container as a dictionary, ensuring that duplicate
        parameters are not included in the result.
        """
        ret: dict[str, dict[str, str]] = dict()
        for item in self._objects:
            section = item.__class__.__name__.lower()
            if section not in ret:
                ret[section] = dict()
            for key, value in item.__class__.__dict__.items():
                if not key.startswith("__") and not callable(value) and \
                            key not in ret[section]:
                    ret[section][key] = value
        return ret

    def __str__(self):
        """
        Returns a string representation of the content of this object-mix in
        its current state.
        """
        ret = list()
        for obj in self._objects:
            ret.append(str(obj))
        return "\n".join(ret)

    def __getattr__(self, name):
        for obj in self._objects:
            if hasattr(obj, name):
                return getattr(obj, name)
        raise AttributeError(
            f"ObjectMix {self.__class__.__name__} has no attribute {name}. "
            f"Probably a required object is not added into this mix."
        )


class Theme:
    """
    A class to hold the overall theme of the document which may contain various
    objects of different types holding respective parameters. For example, for
    the template psdoc, it may contain attributes like config, geometry, table,
    dbschematable etc. These attributes can be passed on to the constructor of this
    class in its constructor. For example:
        theme = Theme(Config(), Geometry())

    One or more theme-component-objects holding various parameters
    required in building the complete theme object. It is dependent on the
    document being constructed, and hence, it should be able to incorporate
    those parameters too which would be required in future. 
    For that purpose, all attributes of this class are instances of class
    ObjectMix. The attribute-names are derived by converting the
    class-names of supplied theme-components into their respective lower
    case names.  Attributes of formerly added components will override the
    same of the ones added later.

    The components added later may supply default values for the attributes
    which were not supplied by the components added earlier. Depending on
    the template being used, all of these attributes may or may not be
    present in the theme-object. If required, then they are expected to be
    present in the configuration file used to initialize the theme-object
    for whichever module gets used in the conversion of the mindmap to PDF
    document.       

    In the configuration file used to initialize the theme, all of these
    attributes would be treated as respective sections, like [config],
    [geometry], [table], [dbschematable], [colors] etc. The theme
    components can be any object which has attributes defined in the
    respective sections of the configuration file. For example, Config
    object can have attributes like `toc_depth`, `sec_depth`, etc.
    The Geometry object can have attributes like `inner_margin`,
    `top_margin`, `head_height`, `figure_width` etc. The Table object can
    have attributes like `header_row_color`, `header_text_color`, etc.
    The DBSchemaTable object can have attributes like `dbschematable_font_size`,
    `dbschematable_font_family`, `dbschematable_width` etc. The Colors object can
    have attributes like `primary_color`, `background_color`,
    `secondary_color`, etc. The list of these theme components are not
    exhaustive, and can be extended in future to include more components
    as required by the document template used for conversion.
    """
    config: ObjectMix
    geometry: ObjectMix
    table: ObjectMix
    dbschematable: ObjectMix
    colors: ObjectMix

    def __init__(self, *components):
        """
        Initialize the Theme object with one or more theme-component-objects.

        Parameters
        ----------
        components : object
            One or more theme-component-objects holding various parameters
            required in building the complete theme object. It is mostly
            dependent on the document being constructed.
        """

        # Use default values of respective paramaters, if supplied ones
        # are None.
        for component in components:
            if component:
                name = component.__class__.__name__.lower()
                try:
                    attribute = getattr(self, name)
                    attribute.add_object(component)
                except AttributeError:
                    attribute = ObjectMix(component)
                    setattr(self, name, attribute)

    def add_component(self, component: object) -> None:
        """
        Method to add a component to the theme. They are usually added at runtime,
        as and when required. It allows extending the theme for newer modules which get
        loaded at runtime based on the mindmap being parsed and converted.

        Parameters
        ----------
        component : object
            The component of the theme getting added. It is usually supplied from an
            externally defined module, like usecase.
        """
        try:
            attr = getattr(self, component.__class__.__name__.lower())
        except AttributeError:
            attr = ObjectMix()
            setattr(self, component.__class__.__name__.lower(), attr)
        attr.add_object(component)
    
    def dump(self) -> dict[str, dict[str, str]]:
        """
        Dump all the parameters of theme, categorized by their respective sections.
        """
        ret = dict()
        # for name, value in self.__class__.__dict__.items():
        #     if not name.startswith("__") and not callable(value):
        for name, value in self.__dict__.items():
            if not name.startswith("__") and not callable(value):
                ret.update(value.dump())
        return ret


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
    image_path: Path,
    image_width: str,
    image_caption: str | None = None,
    image_position: str = "!htb",
):
    """
    Return a LaTeX Figure object containing supplied figure, and
    layouts based on the supplied configuration.

    Parameters
    ----------
    image_path: Path
        A Path opbject pointing to the image file.
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
    colors: List = field(default_factory=list)
    hypertargets: Set = field(default_factory=set)
    changeset: List = field(default_factory=list)
    changeset_section: str | None = field(default=None)
    changeset_node: Node | None = field(default=None)
    working_dir: Path | None = field(default=None)
    images_dir: Path | None = field(default=None)

    @register_color
    def regcol(self, color):
        """
        Register supplied color to the document-context before proceeding
        """
        return color
