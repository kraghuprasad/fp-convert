#!/usr/bin/env python3
#
"""
A program to invoke Freeplane mindmap to PDF conversion utility.
If the mindmap is constructed, following certain conventions, one can
produce print-quality PDF documents using this program.
It uses freeplane-io and pylatex packages for the heavy-lifting.

Author: K Raghu Prasad <raghuprasad AT duck.com>
Copyright: ©2024-25 K. Raghu Prasad <raghuprasad AT duck.com>
ALL RIGHTS RESERVED.
"""
import argparse
import shutil
import tempfile
from pathlib import Path

from peek import peek

from fp_convert.templates.psdoc import PSDoc

parser = argparse.ArgumentParser(
    description="""
Program to convert a Freeplane mindmap's content into a print-quality PDF
document. If only relative file-paths are used to define the resources
(like images) used in the mindmap, then run this program from the folder in
which the mindmap file is situated. In case absolute paths are used in the
resource-paths within the mindmap, then this program can be executed from
anywhere, as long as appropriate input and output file-paths are provided to
it.
"""
)
parser.add_argument("mindmap_file", help="input freeplane mindmap file-path")
parser.add_argument("output_file", help="output PDF file-path")
parser.add_argument(
    "-k",
    "--keep_tex",
    help="keep intermediate TeX/LaTeX file",
    action="store_true",
)
parser.add_argument(
    "-d",
    "--debug",
    help="preserve all intermediate files for debugging purpose",
    action="store_true",
)
args = parser.parse_args()

mindmap_file_path = args.mindmap_file
#peek(mindmap_file_path)
mm_filepath = Path(mindmap_file_path)
#peek(mm_filepath)
output_pdf_path = args.output_file
#peek(output_pdf_path)
pdf_filepath = Path(output_pdf_path)
#peek(pdf_filepath)

# with tempfile.TemporaryDirectory(prefix="fp-convert-") as temp_dir:
#    doc = PSDoc(mindmap_file_path, working_dir=temp_dir)
#    temp_output = Path(temp_dir, f"{pdf_filepath.name}.tex")
#    doc.generate_pdf(temp_output, clean_tex=(not args.keep_tex))
#    shutil.copy2(temp_output, output_pdf_path)
#    if args.keep_tex:
#        shutil.copy2(f"{temp_output}.tex", Path(
#            pdf_filepath.parent, f"{pdf_filepath.stem}.tex"))

temp_dir = tempfile.TemporaryDirectory(prefix="fp-convert-", delete=False)
doc = PSDoc(mm_filepath, working_dir=temp_dir.name, lmodern=True)
temp_output = Path(temp_dir.name, f"{pdf_filepath.name}")
peek(temp_output)
doc.generate_pdf(temp_output, clean=args.debug, clean_tex=(not args.keep_tex))
shutil.copy2(temp_output, pdf_filepath)
if not args.debug:
    temp_dir.cleanup()
