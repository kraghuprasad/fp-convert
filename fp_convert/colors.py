"""
Module to retrieve color specs of named standard colors.
"""

import json
import os
from pathlib import Path

colordefs_file_path = Path(
    Path(os.path.abspath(__file__)).parent, "resources", "colordefs.json"
)

try:
    with open(colordefs_file_path, encoding="utf-8") as colordefs_file:
        colordefs = json.load(colordefs_file)
except FileNotFoundError as e:
    raise RuntimeError(f"Missing color definitions file: {colordefs_file_path}") from e
except json.JSONDecodeError as e:
    raise RuntimeError(f"Invalid JSON in {colordefs_file_path}: {e}") from e

class Color:
    """
    Class to retrieve color specs of named standard colors.
    """

    def __init__(self, name: str, colordefs: dict=colordefs):
        """
        Initialize the color from the content colordefs.json.

        Parameters:
        -----------
        name: str
            The name of the color. It should be the standard name of the color,
            all in lower case English alphabets.

        colordefs: dict
            The dictionary containing the color definitions.
        """
        if name not in colordefs["colors"]:
            raise ValueError(f"Color {name} not found in system's color "
                             f"definition-file {colordefs_file_path} or "
                             "the one supplied at runtime.")

        self.name = name
        self.rgbval = colordefs["colors"][name][1]
        self.htmlval = colordefs["colors"][name][3]
        self.description = colordefs["colors"][name][4]

    def get_rgbval(self):
        """
        Get the RGB color values.
        """
        return self.rgbval

    def get_htmlval(self):
        """
        Get the HTML color values.
        """
        return self.htmlval

    def get_description(self):
        """
        Get the descriptive name of the color.
        """
        return self.description

    def get_hexval(self):
        """
        Get the color value string formatted in hexadecimal.
        """
        return f"0x{self.htmlval[1:]}"
