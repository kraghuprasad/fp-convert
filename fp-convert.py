#!/usr/bin/env python3
#
"""
A program to convert Freeplane based mindmaps to corresponding PDF documents.
If mindmap is constructed, following certain conventions, you can produce
print-quality PDF documents using fp-convert. It uses pytablewriter, pylatex,
and freeplane-io packages for its heavy-lifting.

Author: K Raghu Prasad <raghuprasad AT duck.com>
Copyright: ©2024-25 K. Raghu Prasad <raghuprasad AT duck.com>
ALL RIGHTS RESERVED.
"""
import sys, os, re
from pathlib import Path
from datetime import date
try:
    import freeplane
    from pylatex import (
        Alignat, Axis, Command, Description, Document, Figure, FlushLeft,
        Foot, Head, Itemize, Label, LargeText, LineBreak, Math, Matrix,
        MediumText, MiniPage, NewLine, NoEscape, Package, PageStyle, Plot,
        Ref, Section, Subsection, Subsubsection, Tabular, TikZ,
        simple_page_number,
        )
    from pylatex.section import Paragraph, Subparagraph
    from pylatex.position import VerticalSpace
    from pylatex.frames import MdFramed
    from pylatex.utils import bold, italic, verbatim
    #from pytablewriter import LatexTableWriter
except ModuleNotFoundError:
    print("""
    Besides standard Python modules, following packages are required to
    execute this program:
        freeplane_io (>=0.10.0)
        pylatex (>=1.4.2)
        pytablewriter (>=1.2.0)
    Please install all of them (usually by running "pip install <package-name>)"
    """)
    sys.exit(1)


class TableTheme:
    header_color = "Apricot",
    rowcolor_1 = "gray!25"
    rowcolor_2 = "white"
    line_color = "red"

class ColorTheme:
    link_color = "{rgb}{0.63, 0.79, 0.95}"
 
class Theme:
    table = TableTheme()
    color = ColorTheme()


class HeaderConfig:
    headline = True
    headline_color = "red"
    header_left = ""
    header_center = ""
    header_right = ""
    
 
class FooterConfig:
    footline = True
    footline_color = "red"
    footer_left = ""
    footer_center = ""
    footer_right = ""


class Config:
    header = HeaderConfig()
    footer = FooterConfig()
    
    
theme = Theme()
config = Config()

geometry={"top": "3in", "left": "1.5in", "right": "1.5in", "bottom": "2in"}


class InvalidRefException(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class InvalidRefTypeException(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class MissingFileException(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class FPDocument(Document):
    """
    Document class to build a Freeplane Document (from a Freeplane Mindmap).
    """
    # The compiled pattern to detect references in text found in Freeplane
    # Mindmap
    ref_pat = re.compile('%(ref[0-9]*)%')
    
    def __init__(
            self, docinfo=None, geometry=geometry, theme=None, config=None):
        super().__init__(lmodern=False)
            
        # Maintain a container with ids of the nodes which are already processed
        self.processed_nodes = set()

        if not docinfo:
            docinfo = dict()
            
        self.docinfo = docinfo

        # Add required packages
        self.packages.append(Package('geometry'))
        self.packages.append(Package('amssymb'))
        self.packages.append(Package('xcolor', options=("dvipsnames", "table")))
        self.packages.append(Package('tcolorbox', options="most"))
        self.packages.append(Package('placeins', options=("section",)))
        self.packages.append(Package('titlesec'))
        self.packages.append(Package('fontenc', options="T1"))
        self.packages.append(Package('hyperref'))
        self.packages.append(Package('mdframed', options="framemethod=TikZ"))
        self.packages.append(Package('ragged2e', options="raggedrightboxes"))

        ## For reference to include subsubparagraph, if needed
        #
        #\setcounter{secnumdepth}{5}%
        #\setcounter{tocdepth}{6}
        #\setlength{\parindent}{0pt}%
        #\titlespacing*{\paragraph}{4pt}{3.25ex plus 1ex minus .2ex}{.75em}%
        #\titleformat{\paragraph}[hang]{\normalfont\normalsize\bfseries}{\theparagraph}{1em}{}%
        #\titlespacing*{\subparagraph}{4pt}{3.25ex plus 1ex minus .2ex}{.75em}%
        #\titleformat{\subparagraph}[hang]{\normalfont\normalsize\bfseries}{\theparagraph}{1em}{}%
        #\titleclass{\subsubparagraph}{straight}[\subparagraph]
        #\newcounter{subsubparagraph}
        #\renewcommand{\thesubsubparagraph}{\Alph{subsubparagraph}}
        #\titleformat{\subsubparagraph}[runin]{\normalfont\normalsize\bfseries}{\thesubsubparagraph}{1em}{}
        #\titlespacing*{\subsubparagraph} {\parindent}{3.25ex plus 1ex minus .2ex}{1em}
        #\makeatletter
        #\def\toclevel@subsubparagraph{6}
        #\makeatother

        self.preamble.append(NoEscape(r"\setcounter{secnumdepth}{5}"))
        self.preamble.append(NoEscape(r"\setcounter{tocdepth}{3}"))
        self.preamble.append(NoEscape(r"\setlength{\parindent}{0pt}"))
        self.preamble.append(NoEscape(r"\titleformat{\paragraph}[hang]{\normalfont\normalsize\bfseries}{\theparagraph}{1em}{}"))
        self.preamble.append(NoEscape(r"\titlespacing*{\paragraph}{0pt}{3.25ex plus 1ex minus .2ex}{.75em}"))
        self.preamble.append(NoEscape(r"\titleformat{\subparagraph}[hang]{\normalfont\normalsize\bfseries}{\thesubparagraph}{1em}{}"))
        self.preamble.append(NoEscape(r"\titlespacing*{\subparagraph}{0pt}{3.25ex plus 1ex minus .2ex}{.75em}"))
        self.preamble.append(NoEscape(r"\definecolor{mtcol}{rgb}{0,0.5,0}"))
        self.preamble.append(NoEscape(r"\newcommand\margincomment[1]{\RaggedRight{\marginpar{\hsize1.7in\tiny\color{mtcol}{#1}}}}"))
        
        # Styling for MdFramed content pertaining to stop-sign.
        self.preamble.append(NoEscape(r"\mdfdefinestyle{StopFrame}{linecolor=red, outerlinewidth=1pt, roundcorner=3pt, rightmargin=5pt, innerrightmargin=5pt, leftmargin=5pt, innerleftmargin=5pt, backgroundcolor=red!5!white}"))

        
        # URL/Link styling
        #
    #    self.preamble.append(NoEscape(r"""
    #\hypersetup{colorlinks,linkcolor={red!50!black},
    #citecolor={blue!50!black},
    #urlcolor={blue!80!black}}"""))
        
        self.preamble.append(NoEscape(r"""
    \hypersetup{
    %pdftitle={Sample Document},
    %pdfpagemode=FullScreen,
    colorlinks=true,
    linkcolor=gray,
    filecolor=magenta,      
    urlcolor=cyan
    }"""))

        # Setting headheight                                  
        self.preamble.append(NoEscape(r"\setlength\headheight{20pt}"))
        
        # Styling the geometry of the document
        #
        self.preamble.append(NoEscape(f"""
\\geometry{{
a4paper,
%total={{170mm,257mm}},
left={geometry["left"]},
right={geometry["right"]},
top={geometry["top"]},
bottom={geometry["bottom"]},
}}"""))
        
        # Apply theme
        if theme:
            self.apply_theme(theme)
 
        # Apply custom text in headers and footers
        self.generate_headers()
        #        docinfo.get('c_header_text', str(node)),
        #        docinfo.get('doc_author', "<Author details missing>"),
        #        docinfo.get('organization', "<Organization details missing>"),
        #        lheader = NoEscape(r"\includegraphics[height=0.5cm]{images/blooper_logo.pdf}"),
        #        lfooter = "",
        #        cheader = docinfo.get('c_header_text', str(node)),
        #        cfooter = NoEscape(r"\includegraphics[height=0.7cm]{images/blooper_corporation_logo.pdf}"))
        #
        # --- End of Constructor of FPDoc ---
       
        
    def generate_headers(self):
    #                    title="<Missing Title>",
    #                    author="<Missing Doc Author>",
    #                    company="<Missing Organization>",
    #                    date=NoEscape(r"\today"),
    #                    lheader="<LH Block>",  # Block to be applied on left side of header
    #                    cheader="<Document Name>",         # Block to be applied as central header
    #                    lfooter=NoEscape(r'\tiny{Generated by \href{https://www.python.org}{fp-convert}.}'),
    #                    rfooter="Right Footer",
    #                    cfooter="<CF Logo>"    # Blck to be applied on center of footer
    #                   ):  
        self.preamble.append(
            Command("title",
                    self.docinfo.get("doc_title", "<Missing document title>")))
        self.preamble.append(
            Command("author",
                    self.docinfo.get("doc_author", "<Missing author name>")))
        self.preamble.append(
            Command("date",
                    self.docinfo.get("doc_date", "<Missing doument date>")))
        header = PageStyle(
            "header",
            header_thickness=self.docinfo.get("header_thickness", "0.4pt"),
            footer_thickness=self.docinfo.get("footer_thickness", "0.4pt"),
            data=NoEscape(r'''
\renewcommand{\headrule}{\color{red}\hrule width \headwidth height \headrulewidth}% Red line
\renewcommand{\footrule}{\color{red}\hrule width \headwidth height \footrulewidth}% Red line
'''))
        
        # Create left header
        with header.create(Head("L")):
            if self.docinfo["l_header_text"]:
                header.append(self.docinfo.get["l_header_text"])
            elif self.docinfo["l_header_image"]:
                header.append(NoEscape(
                    rf"\includegraphics[height=0.5cm]{{{self.docinfo['l_header_image']}}}"))
            else:
                header.append("<Missing left header>")
            
        # Create center header
        with header.create(Head("C", data=NoEscape(r"\normalcolor"))):
            if self.docinfo["c_header_text"]:
                header.append(self.docinfo["c_header_text"])
            elif self.docinfo["c_header_image"]:
                header.append(NoEscape(
                    rf"\includegraphics[height=0.5cm]{{{self.docinfo['c_header_image']}}}"))
            else:
                header.append("<Missing center header>")
            
        # Create right header
        with header.create(Head("R", data=NoEscape(r"\normalcolor"))):
            if self.docinfo["r_header_text"]:
                header.append(
                    NoEscape(rf"\small{{{self.docinfo['r_header_text']}}}"))
            elif self.docinfo["r_header_image"]:
                header.append(NoEscape(
                    rf"\includegraphics[height=0.5cm]{{{self.docinfo['r_header_image']}}}"))
            else:
                header.append("<Missing right header>")
            
        # Create left footer
        with header.create(Foot("L", data=NoEscape(r"\normalcolor"))):
            if self.docinfo["l_footer_text"]:
                header.append(
                    NoEscape(rf"\small{{{self.docinfo['l_footer_text']}}}"))
            elif self.docinfo["l_footer_image"]:
                header.append(NoEscape(
                    rf"\includegraphics[height=0.5cm]{{{self.docinfo['c_header_image']}}}"))
            else:
                header.append("<Missing left footer>")
            
        # Create center footer
        with header.create(Foot("C", data=NoEscape(r"\normalcolor"))):
            if self.docinfo["c_footer_text"]:
                header.append(
                    NoEscape(rf"\small{{{self.docinfo['c_footer_text']}}}"))
            elif self.docinfo["c_footer_image"]:
                header.append(NoEscape(
                    rf"\includegraphics[height=0.5cm]{{{self.docinfo['c_footer_image']}}}"))
            else:
                header.append("<Missing center footer>")
            
        # Create right footer
        with header.create(Foot("R", data=NoEscape(r"\normalcolor"))):
            if self.docinfo["r_footer_text"]:
                header.append(
                    NoEscape(rf"\small{{{self.docinfo['r_footer_text']}}}"))
            elif self.docinfo["r_footer_image"]:
                header.append(NoEscape(
                    rf"\includegraphics[height=0.5cm]{{{self.docinfo['r_footer_image']}}}"))
            else:
                #header.append(simple_page_number())
                header.append(NoEscape(r"\small{Page \thepage\- of \pageref*{LastPage}}"))

        self.preamble.append(header)
        self.change_document_style("header")

        self.append(NoEscape(r"\maketitle"))
        self.append(NoEscape(r"\tableofcontents"))
        self.append(NoEscape(r"\newpage"))
        self.append(NoEscape(r"\justify"))
        
    def apply_theme(self, theme):
        self.theme = theme
        self.append(NoEscape(r'\rowcolors{2}{'+theme.table.rowcolor_1+r'}{'+theme.table.rowcolor_2+r'}'))
    

#
# Utility functions
#
def get_label(id):
    """
    Replace _ with : in the ID of the nodes created by FP.
    """
    return id.replace("_", ":")


def em(content, node):
    """
    Function to expand macros. It is usually used to retrieve the reference-links from supplied node,
    and patch it in the returned content.
    """
    mpats = FPDocument.ref_pat.findall(content)
    if mpats:
        
        labels = list()
        if node.arrowlinks:
            for node_to in node.arrowlinks:
                labels.append(get_label(node_to.id))
        else:
            raise InvalidRefException(
                    f"Node [{str(node)}(ID: {node.id})] without any outgoing arrow-link is using a node-reference.")

        if len(labels) == 1:
            content = content.replace('%ref%', fr'\autoref{{{labels[0]}}}')
        else:
            for idx, label in enumerate(labels):
                #content = content.replace('%ref%', fr'\autoref{{{refs[key]}}}')
                content = content.replace(f"%ref{idx+1}%", fr'\autoref{{{label}}}')
                
        # Add a label to this node for back reference
        content = content + NoEscape("\\label"+f"{{{get_label(node.id)}}}")
    return content


def build_figure(node, doc):
    """
    Build and return a LaTeX figure element using the supplied node.
    """
    ret = list()

    if node.imagepath:
        img_path =  node.imagepath
        
        if Path(img_path).is_file():
            if Path(img_path).suffix.lower() == '.svg':
                # SVG files need corresponding PDF files as they are not
                # treated well by pdflatex. This program doesn't autoconvert
                # SVG to PDF at the present. It has to be done manually.
                fsegs = os.path.splitext(img_path)
                if Path(f"{fsegs[0]}.pdf").is_file():
                    img_path = f"{fsegs[0]}.pdf"
                elif Path(f"{fsegs[0]}.PDF").is_file():
                    img_path = f"{fsegs[0]}.PDF"
        else:
            raise MissingFileException(f"A required file {node.imagepath} missing.")

        fig = Figure(position='!htb')
        fig.append(NoEscape(r'\begin{center}\tcbox{\includegraphics[width=0.5\textwidth]{'
                            + img_path + r'}}\end{center}'))  # Build a boxed figure
        fig.add_caption(node)
        fig.append(NoEscape(r'\label{' + get_label(node.id + '}')))
        ret.append(fig)
    
    # Add back references, if this node is being pointed to by other nodes
    # i.e. sinks for arrows.
    for referrer in node.arrowlinked:
        ret.append(NoEscape(r"\margincomment{\tiny{$\Lsh$ \autoref{" + get_label(referrer.id) + r"}}\newline}"))
        
    if ret:
        return ret
    return ""
        

def build_verbatim_list(node, doc):
    """
    Build a list of parts with the contents of the children printed in
    verbatim mode.
    """
    if node.children:
        itmz = Itemize()
        for child in node.children:
            p = ""
            # If no notes are present, then item-element should start with []
            # to avoid bullets.
            if child.notes:
                p = f"""{p}%\n{em(str(child.notes), child)}"""
                p += "\n\\begin{verbatim}" + em(str(child), child) + '\\end{verbatim}'
            else:
                p += '[]\\begin{verbatim}' + str(child) + '\\end{verbatim}'
             
            # Add back references, if this node is being pointed to by other
            # nodes (sinks for arrows)
            for referrer in node.arrowlinked:
                p = p + NoEscape(r"\margincomment{\tiny{$\Lsh$ \autoref{" + get_label(referrer.id) + "}}}")
                
            itmz.add_item(NoEscape(p))
        return itmz
    return ""

    
def build_para_per_line(content, doc):
    """
    If the supplied content is newline separated, then each line is treated
    as a standalone paragraph.
    """
    #lines = [str.strip(l) for l in str.strip(content).split("\n") if str.strip(l)]
    #print(f"lines: {lines}")
    lines = build_note_lines(content)
    if len(lines) == 1:
        return lines[0]
    lst = "\\par ".join(lines)
    return NoEscape(f"\\par {lst}")

    
def append_notes_if_exists(node, segment, doc, prefix=None, suffix=None):
    """
    Append a note-segment (conditionally prefixed or suffixed with certain
    elements) to the supplied LaTeX segment, provided notes exist in given node.
    """
    if node.id in doc.processed_nodes:
        return segment  # Return without any further processing
    
    if node.notes:
        # If stop-sign is present, then just create a red box to put the warning text,
        # ignoring prefix and suffix parts.
        if node.icons and "stop-sign" in node.icons:
            #segment.append(MdFramed(em(str(node.notes), node), options="style=StopFrame"))
            mdf = MdFramed()
            mdf.options = "style=StopFrame"
            mdf.append(NoEscape(fr"\small{{{em(str(node.notes), node)}}}"))
            segment.append(mdf)
        
        else:
            if prefix:
                segment.append(prefix)
            # Commenting out the following as lack of NoEscape is preventing
            # references to be built correctly. But applying NoEscape here may
            # cause problems, if notes contain characters applicable to LaTeX.
            # Need a neater way to create references!!!
            #segment.append(build_para_per_line(em(str(node.notes), node), doc))
            segment.append(NoEscape(build_para_per_line(em(str(node.notes), node), doc)))
            if suffix:
                segment.append(suffix)
    return segment

    
def build_recursive_list(node, doc, level):
    """
    Build and return a recursive list of lists as long as child nodes are
    present.
    """
    if node.id in  doc.processed_nodes:
        return ""
    
    if node.children:
        itmz =  Itemize()
        for child in node.children:
            # For the purpose of debugging only
            #print("  "*level, f"[{child.id}]", child)
            #print("  "*level, f"[imagepath]", child.imagepath)
            #print("  "*level, f"[icons]", child.icons)
            p = ""
            content = str(child).split(":", 1)
            if len(content) == 2:
                #p = f"{bold(content[0])}: {content[1]}"
                p = f"{bold(content[0])}: {em(content[1], child)}"
                if child.notes:
                    if child.icons and "stop-sign" in child.icons:
                        mdf = MdFramed()
                        mdf.options = "style=StopFrame"
                        #mdf.append(em(str(child.notes), child))
                        note_lines = build_note_lines(child.notes)
                        #mdf.append(em(str(note_lines[0]), child))
                        mdf.append(NoEscape(fr"\small{{{em(str(note_lines[0]), child)}}}"))
                        for line in note_lines[1:]:
                            mdf.append("\n")
                            #mdf.append(em(str(line), child))
                            mdf.append(NoEscape(fr"\small{{{em(str(line), child)}}}"))
                        notes = mdf.dumps()
                    else: 
                        notes = build_para_per_line(em(child.notes, child), doc)
                    p = f"""{p}\\par {notes}"""
            elif child.children or child.notes:
                #if child.icons and "stop-sign" in child.icons:
                #    p = str(child)
                #else:
                #    p = f"{bold(child)}"
                    
                p = em(str(child), child)
                if child.notes:
                    if child.icons and "stop-sign" in child.icons:
                        mdf = MdFramed()
                        mdf.options = "style=StopFrame"
                        note_lines = build_note_lines(em(child.notes, child))  # double check it
                        #mdf.append(em(str(note_lines[0]), child))
                        mdf.append(NoEscape(fr"\small{{{em(str(note_lines[0]), child)}}}"))
                        for line in note_lines[1:]:
                            mdf.append("\n")
                            #mdf.append(em(str(line), child))
                            mdf.append(NoEscape(fr"\small{{{em(str(line), child)}}}"))
                        notes = mdf.dumps()
                    else:
                        notes = build_para_per_line(em(child.notes, child), doc)
                    p = f"""{p}\\par {notes}"""
            else:
                #p = str(child)
                p = em(str(child), child)

            # Add a label so that other nodes can refer to it.
            p = p + NoEscape(r"\label{" + get_label(child.id) + "}")
            
            # Add back references, if this node is being pointed to by other nodes (sinks for arrows)
            for referrer in child.arrowlinked:
                p = p + NoEscape(r"\margincomment{\tiny{$\Lsh$ \autoref{" + get_label(referrer.id) + "}}}")
                
            if child.children:
                if child.icons and 'links/file/generic' in child.icons:  # Table is to be built
                    tab_notes = build_table_and_notelist(child, doc)
                    itmz.add_item(NoEscape(p))
                    if len(tab_notes) >= 1:
                        #itmz.append(NoEscape("\\begin{center}"))
                        itmz.append(NoEscape(r"\newline \raggedright"))
                        itmz.append(tab_notes[0])
                        #itmz.append(NoEscape("\\end{center}"))
                    if len(tab_notes) > 1:
                        itemz = Itemize()
                        #print(tab_notes[1:])
                        for h, c in tab_notes[1]:
                            #print(f"Header: {h}")
                            #print(f"Content: {c}")
                            item = bold(h)
                            lst = "\\par ".join(c)
                            #print(f"{NoEscape(hdr)}:{NoEscape(lst)}")
                            #p = f"""{p}\\par {notes}"""
                            item = f"""{item}\\par {lst}"""
                            itemz.add_item(NoEscape(item))
                        itmz.append(itemz)
                # Else check if children should be formatted verbatim
                elif 'links/file/json' in child.icons or \
                   'links/file/xml' in child.icons or \
                   'links/file/html' in child.icons:
                    itmz.add_item(NoEscape(p))
                    itmz.append(build_verbatim_list(child, doc))
                    #itmz.append(f"{NoEscape(p)}\\newline {build_verbatim_list(child, doc)}")
                    #p += build_verbatim_list(child, doc)
                else:  # Expecting a plain list, or list of list, or list of lists ...
                    itmz.add_item(NoEscape(p))
                    itmz.append(build_recursive_list(child, doc, level+1))
                    #itmz.append(f"{NoEscape(p)}\\newline {build_recursive_list(child, doc, level+1)}")
                    #p += build_recursive_list(child, doc, level+1)
            else:
                itmz.add_item(NoEscape(p))
            doc.processed_nodes.add(child.id)
        doc.processed_nodes.add(node.id)
        return itmz
    
    doc.processed_nodes.add(node.id)
    return ""

    
def build_note_lines(notes):
    """
    Build and return a list of sentences found per line of notes.
    """
    ret = list()
    if notes:
        [ret.append(str.strip(i)) for i in notes.split("\n") if str.strip(i)]
    return ret

    
def build_table_and_notelist(node, doc):
    """
    Build a tabular layout using the tree of information obtained from the
    supplied of node.
    """
    doc.processed_nodes.add(node.id)
    
    if node.children:
        col1 = dict()  # Collection of table-data
        notes = list() # Collection of notes (if they exist)

        for field in node.children:
            if field:
                #print(f"Field is {field}")
                doc.processed_nodes.add(field.id)
                col1[str(field)] = {str.strip(str(d).split(":")[0]): str.strip(str(d).split(":")[1]) for d in field.children}
                if field.notes:
                    notes.append((field, build_note_lines(em(field.notes, field))))
                
        col_hdrs = sorted(list({e for d in col1.values() for e in d.keys()}))

        # Build table-content first
        tab = Tabular("l" * (1+len(col_hdrs)), pos="c")
        #tab.add_caption(node, label=get_label("TAB:", node.id))
        tab.add_hline(color=doc.theme.table.line_color)
        row = list(" ")
        row.extend([bold(hdr) for hdr in col_hdrs])
        tab.add_row(*row, color=doc.theme.table.header_color, strict=True)
        tab.add_hline(color=doc.theme.table.line_color)
        for field in sorted(col1.keys()):
            row = [field,]
            for col in col_hdrs:
                row.append(col1[field].get(col, ""))
            tab.add_row(row)
        tab.add_hline(color=doc.theme.table.line_color)
        
        # Then check if notes are to be collected for the same node
        if notes:
            return (tab, notes)
        return (tab, )
    return tuple()


def add_to_blocks(block, item_list):
    """
    Append items from item_list into the block.
    """
    for item in item_list:
        block.append(item)
        

def retrieve_docinfo(node):
    """
    Parses the notes section of the supplied node and retrieves the
    document-information from it, if it is available. Usually only the
    root node should be supplied to this function to fetch the document's
    information.
    """
    docinfo_tpl = {
        "Title": "doc_title",
        "Version": "doc_version",
        "Date": "doc_date",
        "Author": "doc_author",
        "Client": "client",
        "Vendor": "vendor",
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
        "Header_Thickness": "header_thickness",
        "Footer_Thickness": "footer_thickness",
        "Intro_Text": "intro_text",
    }
    docinfo = {v: None for v in docinfo_tpl.values()}
    regex_pat = "^(" + "|".join([k for k in docinfo_tpl.keys()]) + ") *:(.+)$"
    compiled_pat = re.compile(regex_pat)

    if node.notes:
        for line in build_note_lines(node.notes):
            mpats = compiled_pat.search(line)
            if mpats:
                docinfo[docinfo_tpl[str.strip(mpats[1])]] = str.strip(mpats[2])
    #print(docinfo)
    return docinfo
        
def traverse_children(node, indent, doc):
    """
    Traverse the node-tree and build sections, subsections, and further sections and
    tables based on the depth of the node under process.
    """
    stop_traversing = False
    if node:
        #For the purpose of debugging only
        #print("  "*indent, f"[{node.id}]", node)
        #if node.imagepath:
        #    print("  "*indent, f"[{node.id}]", node.imagepath)
        #if node.icons:
        #    print("  "*indent, f"[{node.id}]", node.icons)
         
        if node.id in doc.processed_nodes:
            # This node is processed already via some look-ahead helper
            # functions.
            #print(f"Received node '{node}' with id {node.id} for reprocessing.")
            return
        
        if indent == 1:
            blocks = [Section(f"{node}", label=Label(get_label(node.id))),]
        elif indent == 2:
            blocks = [Subsection(f"{node}", label=Label(get_label(node.id))),]
        elif indent == 3:
            blocks = [Subsubsection(f"{node}", label=Label(get_label(node.id))),]
        elif indent == 4:
            blocks = [Paragraph(NoEscape(f"{node}"), label=Label(get_label(node.id))),]
        elif indent == 5:
            blocks = [Subparagraph(NoEscape(f"{node}"), label=Label(get_label(node.id))),]
        else:
            return  # Not going to process beyond \subparagraph of LaTeX at the moment.

        #append_notes_if_exists(node, blocks, doc, prefix=NoEscape(r"\raggedright"))
        append_notes_if_exists(node, blocks, doc)
        
        if node.icons and 'image' in node.icons:  # Render image, if required
            add_to_blocks(blocks, build_figure(node, doc))
            
        if node.children:  # Non-section specific things are handled here
            if node.icons and 'links/file/generic' in node.icons:  # Table is to be built
                #append_notes_if_exists(node, blocks, doc, suffix=NewLine())
                tab_notes = build_table_and_notelist(node, doc)
                if len(tab_notes) >= 1:
                    blocks.append(NoEscape("\\begin{center}"))
                    blocks.append(tab_notes[0])
                    blocks.append(NoEscape("\\end{center}"))
                    if len(tab_notes) > 1:
                        itmz = Itemize()
                        #print(tab_notes[1:])
                        for h, c in tab_notes[1]:
                            #print(f"Header: {h}")
                            #print(f"Content: {c}")
                            item = bold(h)
                            lst = "\\par ".join(c)
                            #print(f"{NoEscape(hdr)}:{NoEscape(lst)}")
                            #p = f"""{p}\\par {notes}"""
                            item = f"""{item}\\par {lst}"""
                            itmz.add_item(NoEscape(item))
                        blocks.append(itmz)
                        #[blocks.append(NoEscape(i)) for i in tab_notes[1:]]
                        #blocks.extend([i for i in tab_notes[1:]])
                stop_traversing = True  # After list processing, no section level processing required
            elif node.icons and 'list' in node.icons:  # List is to be built
                #append_notes_if_exists(node, blocks, doc)
                blocks.append(build_recursive_list(node, doc, indent))
                stop_traversing = True  # After list processing, no section level processing required
            elif node.icons and  (
                'links/file/json' in node.icons or \
                'links/file/xml' in node.icons or \
                'links/file/html' in node.icons):
                itmz.append(build_verbatim_list(node, doc))
        with doc.create(blocks[0]):
            if len(blocks) > 1:
                for element in blocks[1:]:
                    doc.append(element)
        doc.processed_nodes.add(node.id)  # Register this node as already processed
        
        if stop_traversing:  # If section-level processing is not expected further, just return
            return
        
        for child in node.children:
            traverse_children(child, indent+1, doc)


if __name__ == '__main__':
    import argparse
    from os import path

    parser = argparse.ArgumentParser(
        description="Program to convert a Freeplane mindmap's content into \
                a print-quality PDF document. If only relative file-paths \
                are used to define the resources (like images) used in the \
                mindmap, then run this program from the folder in which the \
                mindmap file is situated. In case absolute paths are used in \
                the resource-paths within the mindmap, then this program can \
                be executed from anywhere, as long as appropriate input and \
                output file-paths are provided to it.")
    parser.add_argument("mindmap_file", help="input freeplane mindmap file-path")
    parser.add_argument("output_file", help="output PDF file-path")
    parser.add_argument("-k", "--keep_latex", help="keep intermediate \
            LaTeX file", action="store_true")
    #parser.add_argument("-d", "--debug", help="preserve all intermediate \
    #        files for debugging purpose", action="store_true")
    args = parser.parse_args()

    mindmap_file_path = args.mindmap_file

    mm = freeplane.Mindmap(mindmap_file_path)
    node = mm.rootnode
    docinfo = retrieve_docinfo(node)
    #print(docinfo)

    theme = Theme()
    config = Config()
    
    geometry = {"left": "1.3in", "right": "1.5in", "top": "1.5in", "bottom": "1.5in"}
    doc = FPDocument(docinfo=docinfo, geometry=geometry, theme=theme)
    #doc.packages.append(Package('nimbussans'))
    #doc.packages.append(Package('nunito', options="lining"))
    #doc.packages.append(Package('noto', options="sfdefault"))
    doc.packages.append(Package('roboto', options="sfdefault"))
    
    for child in node.children:
        traverse_children(child, 1, doc)
    #for i in doc:
    #    print(i)
    doc.generate_pdf(os.path.splitext(args.output_file)[0], clean_tex=(not args.keep_latex))

