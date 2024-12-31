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

from fp_convert.errors import UnsupportedFileException
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
    "-t",
    "--template",
    help="template to be used for converting to TeX/LaTeX file",
    default="psdoc",
)
parser.add_argument(
    "-f",
    "--font-family",
    help="""font-family to be used while building the PDF file
    Correct LaTeX options are required to be passed-on while supplying this
    parameter. Incorrect options, if supplied, would result in TeX compilation
    failures. The option -k can be used to debug such issues by preserving the
    resultant TeX file for further inspection.
    Examples:
    roboto - The Roboto family of fonts to be used
    roboto:sfdefault - The Roboto family along with LaTeX option sfdefault
    roboto:sfdefault:scaled=1.1 - The Roboto family along with=LaTeX options
         sfdefault, and scaled=1.1 which are applicable on this font family.
         You need to ensure that invalid options for the chosen font-family
         do not get supplied here.
    roboto:scaled=1.1 - The Roboto family of fonts scaled to 1.1
    """,
    default="lmodern",
)
parser.add_argument(
    "-k",
    "--keep-tex",
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
mm_filepath = Path(mindmap_file_path)
output_pdf_path = args.output_file
pdf_filepath = Path(output_pdf_path)
tpl = args.template

temp_dir = tempfile.TemporaryDirectory(prefix="fp-convert-", delete=False)

psdoc_kwargs = {
    "working_dir": temp_dir.name,
}
if args.font_family:
    details = args.font_family.split(":")
    ff = list()
    ff_opts = list()
    ff.append(str.strip(details[0]))
    if len(details) > 1:
        for item in details[1:]:
            ff_opts.append(str.strip(item))
    ff.append(ff_opts)
    psdoc_kwargs["font_family"] = ff
else:
    psdoc_kwargs["font_family"] = ["lmodern", []]

if tpl == "psdoc":
    doc = PSDoc(mm_filepath, **psdoc_kwargs)
else:
    raise UnsupportedFileException("Invalid document template is supplied")

temp_output = Path(temp_dir.name, f"{pdf_filepath.name}")
doc.generate_pdf(temp_output, clean=args.debug, clean_tex=(not args.keep_tex))
shutil.copy2(temp_output, pdf_filepath)
if args.keep_tex:
    shutil.copy2(
        Path(temp_dir.name, (pdf_filepath.stem + ".tex")),
        Path(pdf_filepath.parent, (pdf_filepath.stem + ".tex")),
    )
    if not args.debug:
        temp_dir.cleanup()
