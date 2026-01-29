"""
Utilities for processing text files in fp-convert.
"""
import re
from typing import Dict
from pathlib import PosixPath

# replacements = {
#     r"ERROR.*": "ERROR REMOVED",
#     r"\btemp\b": "permanent"
# }

def create_file_with_replaced_texts(
        input_file: PosixPath,
        output_file: PosixPath,
        replacements: Dict[str, str]) -> None:
    """
    Replace certain text-blocks in the content obtained from the input file
    with their respective replacements (as supplied), and create a new output
    file with patched content.
    
    input_file
    """
    with open(input_file, "r", encoding="utf-8") as fin, \
        open(output_file, "w", encoding="utf-8") as fout:
        for line in fin:
            for pattern, repl in replacements.items():
                line = re.sub(pattern, repl, line)
            fout.write(line)
