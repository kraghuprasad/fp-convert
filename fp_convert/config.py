"""
Configuration module of fp-convert
Author: K. Raghu Prasad
License: GPL(v3)
"""
import yaml
from typing import Any, Dict, Union

from fp_convert.errors import InvalidTypeException, MissingFileException, MissingPermissionException, UnsupportedFileException


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
    
    def dump(self) -> dict[str, dict[str, Any]]:
        """
        Dump the content of this container as a dictionary, ensuring that duplicate
        parameters are not included in the result.
        """
        ret: dict[str, dict[str, str]] = dict()
        for item in self._objects:
            section = item.__class__.__name__.lower()
            if section not in ret:
                ret[section] = dict()
            for key in dir(item):
                if not key.startswith("_") and key not in ret[section]:
                    value = getattr(item, key)
                    if not callable(value):
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


class Main:
    """
    The main configuration parameters for building the document
    """
    timezone: str = "UTC"  # Timezone for all timestamps used in the document
    max_sec_depth: int = 5  # Maximum nested sections allowed (capped to 6)
    toc_depth: int = 3  # Maximum section-depths in the table of contents
    figure_width: str = r"0.6\textwidth"  # Width of the figure, in LaTeX
    del_mark_color: str = "red!80!gray"  # Color of markers for nodes marked for deletion
    del_mark_flag: str = r"\faCut"  # FontAwesome icon for del-markings
    del_mark_text: str = "CUT"  # Text marking nodes for removal
    new_mark_color: str = "cobalt"    # Color of markers for newly created nodes
    new_mark_flag: str = r"\faPlus"   # FontAwesome icon for new-markings
    new_mark_text: str = "NEW"    # Text marking newly added nodes
    file_color: str = "magenta"        # Color of file names in the document
    header_line_color: str = "airforceblue"  # Color of header line
    header_thickness: Union[float, int] = 0.4  # Header line thickness
    footer_line_color: str = "airforceblue"  # Color of footer line
    footer_thickness: Union[float, int] = 0.4  # Footer line thickness
    head_height: str = "25pt"
    inner_margin: str = "1.25in"  # Applicable only in twosided mode
    outer_margin: str = "1.25in"  # Applicable only in twosided mode
    link_color: str = "celestialblue" # Color of hyperlinks in the document
    mc_color: str = "{rgb}{0,0.5,0}"  # Color of margin comments in the document
    par_indent: str = "0pt"
    left_margin: str = "1.25in"
    right_margin: str = "1.25in"
    top_margin: str = "1.5in"
    bottom_margin: str = "1.5in"
    url_color: str = "ceruleanblue"       # Color of URLs in the document

    # Paramaters for top and bottom logos of title-page
    tp_bottom_logo_height: str = "1.5cm"  # Height of bottom logo on title page
    tp_bottom_logo_vspace: str = "7cm"
    tp_top_logo_height: str = "3cm"       # Height of top logo on title page
    tp_top_logo_vspace: str = "5cm"

    # Height of various images used in headers and footers of all pages
    c_footer_image_height: str = "0.5cm"
    c_header_image_height: str = "0.5cm"
    l_footer_image_height: str = "0.5cm"
    l_header_image_height: str = "0.7cm"
    r_footer_image_height: str = "0.5cm"
    r_header_image_height: str = "0.5cm"

    # Various parameters for paragraphs and subparagraphs
    par_title_format: str = r"[hang]{\normalfont\normalsize\bfseries}{\theparagraph}{1em}{}"
    par_title_spacing: str = r"{0pt}{3.25ex plus 1ex minus .2ex}{.75em}"
    subpar_title_format: str =  r"[hang]{\normalfont\normalsize\bfseries}{\thesubparagraph}{1em}{}"
    subpar_title_spacing: str = r"{0pt}{3.25ex plus 1ex minus .2ex}{.75em}"


class StopFrame:
    """
    The configuration parameters for building stopframe-blocks
    """
    background_color: str = "red!5!white"    # Stop-Frame background-color
    inner_left_margin: str = "10pt"  # Stop-Frame inner left margin width
    inner_right_margin: str = "30pt"  # Stop-Frame inner right margin width
    line_color: str = "cadmiumred"           # Stop-Frame line-color
    outer_left_margin: str = "5pt"  # Stop-Frame outer left margin width
    outer_line_width: str = "1pt"  # Stop-Frame outer line-width size
    outer_right_margin: str = "5pt"  # Stop-Frame outer right margin width
    round_corner_size: str = "3pt"  # Stop-Frame rounded corner's size

class Table:
    """
    The configuration parameters for building table-blocks
    """
    footer_row_color: str = "babyblueeyes!10"
    header_row_color: str = "babyblueeyes!80"
    header_text_color: str = "darkblue"
    line_color: str = "cornflowerblue"
    rowcolor_1: str = "babyblueeyes!35" # Row colors 1 and 2 belowng to rendering of rows in default table
    rowcolor_2: str = "babyblueeyes!20" # Row colors 1 and 2 belowng to rendering of rows in default table
    rowcolor_3: str = 'lightapricot!30' # Row colors 3 and 4 belong to rendering of rows in deliverable-table
    rowcolor_4: str = 'lightapricot!10' # Row colors 3 and 4 belong to rendering of rows in deliverable-table
    rowcolor_5: str = 'lightapricot!50' # Row color 5 is for rendering the row containing deliverable-name


class DBSchema:
    """
    The configuration parameters bilding DB schema-blocks
    """
    tbl1_body_line_color: str = "gray!30"
    tbl1_header_line_color: str = "fpcblue2"
    tbl1_header_row_color: str = "spirodiscoball!20!white"
    tbl1_header_text_color: str = "darkblue"
    tbl2_header_line_color: str = "fpcblue2"
    tbl2_header_row_color: str = "fpcblue1"
    tbl2_header_text_color: str = "darkblue"
    tbl2_rowcolor_1: str = "white"
    tbl2_rowcolor_2: str = "tealblue!7!white"

class UML:
    """
    The configuration parameters for building UML diagram-blocks
    """
    actor_background_color: str = "#d8f0fd"     # light blue for background of actor
    actor_border_color: str = "#4e98c4"         # blue for border of actor
    actor_color: str = "#4e98c4"                # blue for actor
    background_color: str = "#ffffff"           # white background
    component_background_color: str = "#ffffff" # white background for component
    component_border_color: str = "#000000"     # black border for component
    component_color: str = "#d0d0d0"            # gray for component
    connector_line_type: str = "default"          # default, ortho or polyline
    default_text_alignment: str = "left"          # left, center or right
    note_background_color: str = "#f7f3de"      # light yellow background for note
    note_border_color: str = "#867c1c"          # blackish yellow border for note
    note_color: str = "#c0c0c0"                 # light gray for note
    package_border_color: str = "#3a2f2f"       # brownish black for package border
    plantuml_cmd: str = "plantuml"       # command name (relies on PATH environment) or OS dependent full path
    usecase_border_color: str = "#0542C5"       # dark blue for usecase border
    usecase_color: str = "#b1dafc"              # darker shade of blue for usecase
    usecase_diagram_width: str = r"0.9\textwidth" # width of usecase diagram

class ColorBox:
    """
    The configuration parameters for building colorbox-blocks
    """
    background_color: str = "blue!10!white"
    frame_color: str = "blue!80!black"
    title_color: str = "black"
    box_rule_width: str = "0.8pt"
    box_arc_size: str = "2.5mm"
    left: str = "5mm"
    right: str = "5mm"
    top: str = "2mm"
    bottom: str = "2mm"

class FancyBox:
    """
    The configuration parameters for building colorbox-blocks
    """
    title_color: str = "black"
    title_font: str = r"\bfseries\large"
    title_background_color: str = "red!20!white"
    title_frame_color: str = "red!80!white"
    title_attributes: str = "sharp corners"
    # title_attributes: str = "rounded corners"
    title_position: str = "top left"
    title_xshift: str = "1.5mm"
    title_yshift: str = "-1mm"
    title_drop_shadow: str = "false"
    title_bullet: str = r"\faChevronCircleRight"
    frame_bg_color: str = "red!5!white"
    frame_color: str = "red!80!white"
    frame_arc_size: str = "1mm"
    frame_rule_width: str = "0.8pt"
    frame_width: str = r"0.9\textwidth"
    frame_left_margin: str = "6pt"
    frame_right_margin: str = "6pt"
    frame_top_margin: str = "6pt"
    frame_bottom_margin: str = "6pt"
    frame_alignment: str = "center"  # left, center or right
    frame_drop_shadow: str = "false"

class FancyBox2:
    """
    The configuration parameters for building colorbox-blocks
    """
    title_color: str = "white"
    title_font: str = r"\bfseries\large"
    title_background_color: str = "purple!70!black"
    title_frame_color: str = "purple!70!black"
    title_attributes: str = "sharp corners"
    # title_attributes: str = "rounded corners"
    title_position: str = "top left"
    title_xshift: str = "1.5mm"
    title_yshift: str = "-1mm"
    title_drop_shadow: str = "false"
    title_bullet: str = r"\faChevronCircleRight"
    frame_bg_color: str = "white"
    frame_color: str = "purple!70!black"
    frame_arc_size: str = "1mm"
    frame_rule_width: str = "0.8pt"
    frame_width: str = r"0.85\textwidth"
    frame_left_margin: str = "6pt"
    frame_right_margin: str = "6pt"
    frame_top_margin: str = "6pt"
    frame_bottom_margin: str = "6pt"
    frame_alignment: str = "center"  # left, center or right
    frame_drop_shadow: str = "false"
    table_rowcolor_1: str = "lightapricot!50"
    table_rowcolor_2: str = "lightapricot!30"
    table_rowcolor_3: str = "lightapricot!10"
    table1_width: str = r"\textwidth" # width for tabled-content
    table2_width: str = r"0.8\textwidth" # width for child-node-content
    hrule_width: str = "0.4pt"  # width of horizontal rule in the fancy box

class Translations:
    """
    The translation-texts for automatically generated text segments
    """
    deliverable: str = "Deliverable"
    deliverable_id: str = "Deliverable-ID"
    accountable: str = "Accountability"
    delivery_date: str = "Date of Delivery"
    risk_types: str = "Risk-Types"
    risk_id: str = "Risk-ID"

config_classes = [
    Main, StopFrame, Table, DBSchema, UML, ColorBox, FancyBox,
    FancyBox2, Translations
]

class Config:
    """
    A class to hold the overall configuration of the document which may
    contain various objects of different types holding respective parameters.
    For example, for the project specifications, it may contain attributes
    like main, stopframe, table, dbschema, etc. These attributes can be passed
    on to the constructor of this class. For example:
        config = Config(Main(), Stopframe(), Table(), DBSchema())

    One or more components can be added to this class. These components are
    required in building the complete Config object. It is dependent on the
    document being constructed, and hence, it should be able to incorporate
    those parameters too which would be required in future.
    For that purpose, all attributes of this class are instances of class
    ObjectMix. The attribute-names are derived by converting the
    class-names of supplied config-components into their respective lower
    case names.  Attributes of formerly added components will override the
    same of the ones added later.

    All components with customized parameter-value pairs should be supplied
    at the time of confstruction of this object. As soon as the config-object
    is constructed, the default values of the attributes for all the
    components listed in config_classes are supplied to fill-in the missing
    attributes - if any - of those components.
    
    If you are adding some entirely new components for your customized
    builder functions, then they can be added after the object is constructed.
    By default, only the components listed in config_classes are initialized
    in the constructor, after using user-supplied values.

    In the configuration file used to initialize the config, all of these
    attributes would be treated as respective sections, like [main],
    [stopframe], [table], [uml], [dbschema], etc. The config components can
    be any object which has attributes defined in the respective sections of
    the configuration file. For example, section [main] can have attributes
    like `toc_depth`, `sec_depth`, etc.
    """
    main: ObjectMix
    stopframe: ObjectMix
    dbschema: ObjectMix
    table: ObjectMix
    uml: ObjectMix
    colorbox: ObjectMix
    fancybox: ObjectMix
    fancybox2: ObjectMix
    translations: ObjectMix

    def __init__(self, *components):
        """
        Initialize the Config object with one or more component-objects.

        Parameters
        ----------
        components : object
            One or more component-objects holding various parameters required
            in building the Config object. It is mostly dependent on the
            document being constructed.
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
        for cc in config_classes:
            self.add_component(cc())

    def add_component(self, component: object) -> None:
        """
        Method to add a component to this instance of the Config. They are
        usually added at runtime, as and when required. It allows extending
        the configuration for newer modules which get loaded at runtime based
        on the mindmap being parsed and converted.

        Parameters
        ----------
        component : object
            The component of the config getting added. It is usually supplied
            from an externally defined module, like uml.
        """
        try:
            attr = getattr(self, component.__class__.__name__.lower())
        except AttributeError:
            attr = ObjectMix()
            setattr(self, component.__class__.__name__.lower(), attr)
        attr.add_object(component)
    
    def dump(self) -> dict[str, dict[str, Any]]:
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
    
    def dump_yml(self, default_flow_style=False):
        return yaml.dump(self.dump(), default_flow_style=default_flow_style)

def create_config_from_file(conf_file):
    """
    Create a Config object from the supplied YAML based fp-convert
    configuration file.

    Parameters
    ----------
    config_file : str
        The path to the fp-convert configuration file

    Returns
    -------
    Config
        A Config object created for rendering GeneralDoc from the supplied
        configuration file.
    """
    components: Dict[str, object] = dict()
    for cc in config_classes:  # Populate default components
        components[cc.__name__.lower()] = cc()
    try:
        with open(conf_file) as f:
            conf = yaml.safe_load(f)
    except FileNotFoundError:
        raise MissingFileException(f"Configuration file not found: {conf_file}")
    except PermissionError:
        raise MissingPermissionException(f"Permission denied reading configuration file: {conf_file}")
    except yaml.YAMLError as e:
        raise UnsupportedFileException(f"Invalid YAML in configuration file {conf_file}: {e}")

    if conf and isinstance(conf, dict):
        for key in conf.keys():
            if key not in components:
                components[key] = type(
                    str.capitalize(key),
                    (object,),
                    conf[key]
                )
                continue
            else:
                for k in conf[key].keys():
                    # setattr(components[key], k, conf[key][k])
                    value = conf[key][k]

                    # Get the expected type from the class definition if it exists
                    if hasattr(components[key].__class__, k):
                        expected_type = type(getattr(components[key].__class__, k))
                        if not isinstance(value, expected_type):
                            # Allow str to in/float conversion for common cases
                            if expected_type in (int, float) and isinstance(value, str):
                                try:
                                    value = expected_type(value)
                                except ValueError:
                                    raise InvalidTypeException(
                                        f"Invalid value for {key}.{k}: expected {expected_type.__name__}, got {type(value).__name__}"
                                    )
                    setattr(components[key], k, value)
    else:
        raise UnsupportedFileException(f"Malformed configuration file {conf_file}.")

    return Config(*components.values())

