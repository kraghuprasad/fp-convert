class Config:
    """
    Following controls the usecase-specific configuration parameters.
    """
    uml_connector_line_type: str = "default"        # default, ortho or polyline
    uml_default_text_alignment: str = "left"        # left, center or right
    uml_plantuml_cmd: str = "/usr/bin/plantuml"     # command path for Linux/Unix systems only


class Geometry:
    """
    Following attributes define various geometry specific parameters used in rendering
    usecases.
    """
    uml_usecase_diagram_width: str = r"0.9\textwidth"


class Colors:
    """
    Following colors are defined for styling the usecase and their component blocks.
    """
    uml_actor_background_color: str = "#d8f0fd"     # light blue for background of actor
    uml_actor_border_color: str = "#4e98c4"         # blue for border of actor
    uml_actor_color: str = "#4e98c4"                # blue for actor
    uml_background_color: str = "#ffffff"           # white background
    uml_component_background_color: str = "#ffffff" # white background for component
    uml_component_border_color: str = "#000000"     # black border for component
    uml_component_color: str = "#d0d0d0"            # gray for component
    uml_note_background_color: str = "#f7f3de"      # light yellow background for note
    uml_note_border_color: str = "#867c1c"          # blackish yellow border for note
    uml_note_color: str = "#c0c0c0"                 # light gray for note
    uml_package_border_color: str = "#3a2f2f"       # brownish black for package border
    uml_package_color: str = "#ebf6fa"              # light blue for package
    uml_usecase_color: str = "#b1dafc"              # darker shade of blue for usecase
    uml_usecase_border_color: str = "#0542C5"       # dark blue for usecase border
