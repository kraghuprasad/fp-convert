"""
Various builders for the components of the LaTeX document.
"""
from decimal import Decimal
import re
from dateutil import parser as dateparser
from typing import Dict, List, Set, Optional, Callable
from pathlib import Path, PurePosixPath
from collections import OrderedDict
from freeplane import Node
from pylatex import (
    Command,
    Itemize,
    LongTable,
    MiniPage,
    Tabularx,
)
from pylatex.base_classes import LatexObject
from pylatex.table import Tabular
from pylatex.utils import (
    bold,
    NoEscape as NE,
    escape_latex as EL,
    italic,
    verbatim,
)

from cairosvg import svg2pdf

from fp_convert.utils.decorators import (
    track_processed_nodes,
    limit_depth,
)
from fp_convert.docs import GeneralDoc
from fp_convert.config import Config
from fp_convert.errors import (
    FileConversionException, InvalidNodeException, InvalidRefException, UnsupportedFileException
)
from fp_convert.utils.helpers import (
    build_latex_figure_object,
    build_ucaction_tabular_segments,
    get_references,
    get_direction,
    get_flag_refs,
    get_flag_blocks,
    get_hypertarget,
    get_label,
    get_node_text_blocks,
    get_note_text_blocks,
    get_processed_note_lines,
    get_stopframe_block,
    is_actor_node,
    puml2svg,
    retrieve_note_lines,
    retrieve_table_and_notelist,
    to_bool,
    dump,
    list_exists_in_parent_path,
    retrieve_number_table_data,
    is_ignore_type,
    is_ucaction_type,
    is_ucpackage_type,
    is_stopframe_type,
    get_fpc_accountables,
    get_fpc_block_type,
    get_fpc_delivery_date,
    get_fpc_id,
    get_fpc_is_active,
    get_fpc_notes_position,
    get_fpc_risk_types,
    get_fpc_show_caption,
)

from fp_convert.utils.dbs import (
    DBItemize,
    DBTable,
    DBTableField,
)
from fp_convert.utils.uml.plantuml import (
    Actor,
    ActorFactory,
    Package,
    Relationship,
    UseCaseDiagram,
    Usecase,
)

# All builder-functions publicly exposed to build a document segment
# from a mindmap node must have names matching with following pattern.
# Such function-names must contain only two underscores(_) in it, which
# should enclose the value of respective fpcBlokType attribute used in
# the node.
builder_func_pat = re.compile(r'^build_([^_]+)_block$')  

def enter_floating_environment(doc: GeneralDoc) -> None:
    """
    It is executed when a floating environment is going to be encountered.
    It maintains the call-count which gets decreased only when the method
    # exiting_floating_environment is called.

    Parameters
    ----------
    doc: GeneralDoc
        The document being built

    returns
    -------
    None
    """
    doc.ctx.in_floating_environment.append(1)
    
def exit_floating_environment(
        doc: GeneralDoc,
        ret: List[str|LatexObject|NE]) -> None:
    """
    It is executed when a floating environment is going to be exited.
    It maintains the call-count which gets decreased only when the method
    # exiting_floating_environment is called.

    Parameters
    ----------
    doc: GeneralDoc
        The document being built
    ret: List[str|LatexObject|NE]
        A list of strings, LaTeX objects, or NE objects representing the
        content of the document being built.

    returns
    -------
    None
    """
    if not doc.ctx.in_floating_environment:
        raise Exception("Method exit_floating_environment() invoked "
                        "without a previous matching call to the method "
                        "enter_floating_environment().")
    else:
        doc.ctx.in_floating_environment.pop()
        if not doc.ctx.in_floating_environment and doc.ctx.margin_comments:
            ret.extend(doc.ctx.margin_comments.values())
            doc.ctx.margin_comments.clear()


def create_box(
        title: List[LatexObject | str],
        body: List[LatexObject | str],
        doc: GeneralDoc,
        config: Config,
        title_bullet: str=r"\small \faChevronCircleRight \normalsize \xspace",
        box_type: str="fancybox"):
    """
    It creates boxes of various types and styles in which supplied textual
    content is rendered.

    Parameters
    ----------
    title : List[LatexObject | str]
        List of blocks of text or LaTeX objects which are part of the title
    body :  List[LatexObject | str]
        List of blocks of text or LaTeX objects which are part of the body
    doc : GeneralDoc
        The document in which this box is getting rendered
    config : Config
        The configuration object in which the style-definitions of this box
        defined
    title_bullet : str
        Bullet-character to be used in the title of the box, like any icon
        from the fontawesome library
    box_type : str
        Type of the box to be created. It can be any name which once used,
        its style can not be changed for the next invocation of this function.
        Hence, if different styles or types of boxes are required to be
        rendered, then use different names for this parameter. Please note
        that there is no restrictions on calling this function multiple times
        with same box-type-name. But, after first invocation, all parameters
        in supplied configuration object (config) would be ignored completely.
    """
    if box_type not in doc.preambles:
        doc.preambles[box_type] = [NE(fr"""
\newtcolorbox{{{box_type}}}[2][]{{%
    enhanced,
    breakable,
    colback={getattr(config, box_type).frame_bg_color},
    colframe={getattr(config, box_type).frame_color},
    coltitle={getattr(config, box_type).title_color},
    fonttitle={getattr(config, box_type).title_font},
    title=#2,
    arc={getattr(config, box_type).frame_arc_size},
    top={getattr(config, box_type).frame_top_margin},
    bottom={getattr(config, box_type).frame_bottom_margin},
    left={getattr(config, box_type).frame_left_margin},
    right={getattr(config, box_type).frame_right_margin},
    width={getattr(config, box_type).frame_width},
    boxrule={getattr(config, box_type).frame_rule_width},
    attach boxed title to {getattr(config, box_type).title_position}={{yshift={getattr(config, box_type).title_yshift},xshift={getattr(config, box_type).title_xshift}}},
    boxed title style={{
        enhanced,
        colback={getattr(config, box_type).title_background_color},
        colframe={getattr(config, box_type).title_frame_color},
        {"drop shadow" if to_bool(getattr(config, box_type).title_drop_shadow) else ""},
        {getattr(config, box_type).title_attributes}
    }},
    {"drop shadow" if to_bool(getattr(config, box_type).frame_drop_shadow) else ""},
    #1
}}
""")]
    ret = list()
    ret.append(NE(fr"\begin{{{box_type}}}{{{title_bullet} "))
    ret.extend(title)
    ret.append(NE("}"))
    ret.extend(body)
    ret.append(NE(fr"\end{{{box_type}}}"))
    return ret

@track_processed_nodes
@limit_depth
def build_risk_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[str|LatexObject|NE]:
    """
    Build a block of text in LaTeX for the risk type using the content
    of supplied node and its notes.

    Parameters
    ----------
    node : Node
        The node containing the information of risk
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap
    builders: Dict[str, Callable]
        A dictionary of builders to be used for building the document
        components. The keys are the node types and values are the
        corresponding builder functions
    Returns
    -------
    list[str|LatexObject|NE]
        A list of strings, LaTeX objects, or NE objects representing the
        content of risk-node and its children.
    """
    ret = list()
    if is_ignore_type(node):
        return ret
    if ht := get_hypertarget(node, doc.ctx):
        ret.append(ht)
    
    # Show risk-id in title-box
    title = [
        Command("tinytosmall"),
        NE(bold(doc.config.translations.risk_id)),
        ": ", NE(r"\xspace"),
        EL(get_fpc_id(
            node, NE(r"\faChevronLeft not specified\faChevronRight"))),
        Command("normalsize"),
    ]

    risk_types = [
            str.strip(item) for item in get_fpc_risk_types(
                node,
                NE(r"\faChevronLeft not specified\faChevronRight")
            ).split(";")
    ]

    body = [
        Command("tinytosmall"),
        NE(bold(doc.config.translations.risk_types)),
        r": ", NE(r"\xspace"),
        EL(", ".join(risk_types)),
        Command("normalsize"),
    ]

    note_lines = get_processed_note_lines(node, doc.ctx)
    if note_lines:
        itmz = Itemize()
        for lst in note_lines:
            itmz.add_item(lst[0])
            for element in lst[1:]:  # append rest of the list (line)
                itmz.append(element)
        body.append(itmz)

    fblocks = get_flag_blocks(node, doc.config, doc.ctx)
    ftext = " ".join([dump(b) for b in fblocks]) if fblocks else ""

    # Find out if parent of this node comes under a list type or
    # section/subsection/... type of node. or under some kind of list. Based on that the content of its
    # block of test would change.
    if list_exists_in_parent_path(node.parent, builders):
        if ftext:
            ret.append(NE(fr"{ftext}\xspace {EL(str(node))}"))
        else:
            ret.append(EL(str(node)))
    else:
        if ftext:
            ret.append(
                doc.sections[depth](
                    NE(fr"{ftext}\xspace {EL(str(node))}"), label=False))
        else:
            ret.append(doc.sections[depth](NE(EL(str(node))), label=False))

    ret.extend(
        create_box(
            title, body, doc, doc.config, box_type="fancybox"
        )
    )

    doc.ctx.flush_margin_comments(get_references(node, back_ref=True), ret)
    return ret

@track_processed_nodes
@limit_depth
def build_deliverable_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[str|LatexObject|NE]:
    """
    Build a block of text in LaTeX for the deliverable type using the content
    of supplied node and its notes.

    Parameters
    ----------
    node : Node
        The node containing the information of deliverable
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap (ignored here) as it is
        a standalone block of text.
    builders: Dict[str, Callable]
        A dictionary of builders to be used for building the document
        components. The keys are the node types and values are the
        corresponding builder functions
    Returns
    -------
    list[str|LatexObject|NE]
        A list of strings, LaTeX objects, or NE objects representing the
        content of deliverable.
    """
    ret = list()
    if is_ignore_type(node):  # do not proceed if node is to be ignored
        return ret
    if ht := get_hypertarget(node, doc.ctx):
        ret.append(ht)

    # Deliverable-details
    deliverable_name = EL(str(node))
    deliverable_id = EL(get_fpc_id(
        node, NE(r"\faChevronLeft not specified\faChevronRight"))
    )
    accountable_person = EL(
        ", ".join(
            re.split(
                r" *; *",
                get_fpc_accountables(
                    node, NE(
                        r"\faChevronLeft not specified\faChevronRight"
                    )
                )
            )
        )
    )
    delivery_date = get_fpc_delivery_date(node, 'None')
    if delivery_date != 'None':
        try:
            delivery_date = dateparser.parse(
                delivery_date, dayfirst=True).strftime("%B %d, %Y")
        except Exception as ec:
            raise ValueError(
                f"Could not parse delivery-date '{delivery_date}' supplied "
                f"for the attribute fpcDeliveryDate in node {node} with id "
                f"'{deliverable_id}'. Original error: {ec}"
            ) from ec
    else:
        delivery_date = NE(r"\faChevronLeft not specified\faChevronRight")

    delivery_details = list()
    if node.notes:
        delivery_details.extend(get_processed_note_lines(node, doc.ctx))
    
    title = [
        Command("tinytosmall"),
        NE(bold(doc.config.translations.deliverable_id)),  
        ": ", NE(r"\xspace"),
        # EL(deliverable_id) if to_bool(node.attributes.get("fpcIsActive", "yes")) \
        EL(deliverable_id) if to_bool(get_fpc_is_active(node, "yes")) \
            else Command("sout", EL(deliverable_id)),
        Command("normalsize"),
    ]

    fbody = list()
    enter_floating_environment(doc)  # Getting into the floating environment
    fbody.append(NE(fr"""
%\renewcommand{{\arraystretch}}{{1.3}}
%\setlength{{\tabcolsep}}{{8pt}}
\begin{{tabularx}}{{{doc.config.fancybox2.table1_width}}}{{l X}}
\rowcolor{{{doc.ctx.regcol(
    doc.config.fancybox2.table_rowcolor_1)}}}"""))
    fbody.append(NE(fr"\tinytosmall{{\textbf{{{doc.config.translations.deliverable}}}}} & "))
    fbody.append(Command(
        "tinytosmall",
        EL(deliverable_name) if to_bool(get_fpc_is_active(node, "yes")) else \
            Command("sout", EL(deliverable_name))))
    fbody.append(NE(r"\\"))
    fbody.append(NE(fr"""
\rowcolor{{{doc.ctx.regcol(doc.config.fancybox2.table_rowcolor_2)}}} \tinytosmall{{\textbf{{{doc.config.translations.accountable}}}}} & \tinytosmall{{{accountable_person}}} \\
\rowcolor{{{doc.ctx.regcol(doc.config.fancybox2.table_rowcolor_3)}}} \tinytosmall{{\textbf{{{doc.config.translations.delivery_date}}}}} & \tinytosmall{{{delivery_date}}} \\
\end{{tabularx}}"""))

    # Rest of the content to be rendered in smalltext
    fbody.extend([Command("par"), Command("small")])

    # Clarifications as numbered list with better spacing
    if delivery_details:
        fbody.extend([
            Command(
                "vspace",
                (NE(r"0.25\baselineskip"), )
            ),
            Command(
                "rule",
                (NE(r"\textwidth"), doc.config.fancybox2.hrule_width),
            ),
            Command("newline"),
            Command(
                "vspace",
                (NE(r"0.25\baselineskip"), )
            ),
        ])
        fbody.append(NE(r"\small"))
        if len(delivery_details) == 1:
            # fbody.extend(delivery_details[0])
            for element in delivery_details[0]:
                fbody.append(element)
        else:
            fbody.append(NE(r"\begin{enumerate}[leftmargin=*, label=\arabic*.]"))
            for line in delivery_details:
                fbody.append(NE(r"\item "))
                fbody.extend(line)
            fbody.append(NE(r"\end{enumerate}"))
        fbody.append(NE(r"\normalsize"))

    idx = 0
    if node.children:  # Create a table if there are any children
        child_content = [NE(r"\par"), ]
        child_content.append(NE(fr"\rowcolors{{2}}{{{doc.ctx.regcol(doc.config.fancybox2.table_rowcolor_2)}}}"))
        child_content.append(NE(fr"{{{doc.ctx.regcol(doc.config.fancybox2.table_rowcolor_3)}}}"))
        child_content.append(NE(fr"\begin{{tabularx}}{{{doc.config.fancybox2.table2_width}}}{{X}}"))
        for child in node.children:
            if is_ignore_type(child):
                continue
            idx += 1
            child_content.append(fr"{idx}. ")
            child_content.extend(
                builders[get_fpc_block_type(child, "plaintext")](child, doc, depth, builders))
            child_content.append(NE(r"\\"))
        child_content.append(Command("end", "tabularx"))

    if idx > 0:  # If children of this node has non-ignore type nodes
        fbody.extend(child_content)

    # Revert to normal text
    fbody.append(Command("normalsize"))

    # Build blocks required to render fancybox2
    ret.extend(
        create_box( title, fbody, doc, doc.config, box_type="fancybox2")
    )

    # Include backreferences, if any
    if brefs := get_references(node, back_ref=True):
        doc.ctx.flush_margin_comments(brefs, ret)
    exit_floating_environment(doc, ret)

    return ret

@track_processed_nodes
def build_pagebreak_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[str|LatexObject|NE]:
    """
    Introduces a page-break in the document.

    Parameters
    ----------
    node : Node
        The node containing the marker to capture pagebreak-section. It is a
        placeholder node and would not contain any text though.
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap.
    builders: Dict[str, Callable]
        A dictionary of builders to be used for building the document
        components. The keys are the node types and values are the
        corresponding builder functions
    Returns
    -------
    list[str|LatexObject|NE]
        A list containing a \newpage command.
    
    """
    if is_ignore_type(node):  # do not proceed if node is to be ignored
        return list()
    return [Command("newpage"), ]

@track_processed_nodes
@limit_depth
def build_trackchanges_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[str|LatexObject|NE]:
    """
    Build a block of text in LaTeX for the trackchanges type.

    Parameters
    ----------
    node : Node
        The node containing the marker to capture trackchange-section. It is a
        placeholder node and would not contain any text though.
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap.
    builders: Dict[str, Callable]
        A dictionary of builders to be used for building the document
        components. The keys are the node types and values are the
        corresponding builder functions
    Returns
    -------
    list[str|LatexObject|NE]
        An empty list, as this block doesn't contain any visual element at the
        moment.
    """
    if is_ignore_type(node):  # do not proceed if node is to be ignored
        return list()

    if doc.ctx.docinfo["trackchange_section"]:
        if doc.ctx.changeset_node:  # Ensure changeset node doesn't exist already
            raise InvalidNodeException(
                f'Node "{str(doc.ctx.changeset_node)}(ID: {doc.ctx.changeset_node.id})" is '
                " already marked as changeset node. More than one changeset "
                "nodes are not allowed to be maintained in a document. "
                f'Remove either that node or the node "{str(node)}" (ID: {node.id}) '
                "from the mindmap to continue."
            )
        doc.ctx.changeset_node = node
        doc.ctx.changeset_section = list()
        return [
            doc.sections[depth](NE(EL(str(node))), label=False),
            doc.ctx.changeset_table,
        ]
    return []

@track_processed_nodes
def build_dbschema_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[str|LatexObject|NE]:
    """
    Build a standalone dbschema block in LaTeX using the content of supplied
    node and its notes.

    Parameters
    ----------
    node : Node
        The node containing the details of dbschema.
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap (ignored here) as it is
        a standalone block of text.
    builders: Dict[str, Callable]
        A dictionary of builders to be used for building the document
        components. The keys are the node types and values are the
        corresponding builder functions
    Returns
    -------
    list[str|LatexObject|NE]
        A list of strings, LaTeX objects, or NE objects representing the
        content of dbschema.
    """
    ret = list()
    if is_ignore_type(node):  # do not proceed if node is to be ignored
        return ret

    if ht := get_hypertarget(node, doc.ctx):
        ret.append(ht)
    
 
    dbtables = list()
    if node.children:
        for table in node.children:
            dbtable = DBTable(str(table))
            dbtable.label = get_label(table.id)  # LaTeX label for table
            dbtable.node = table  # To identify and build cross-references

            if table.notes:
                dbtable.notes = retrieve_note_lines(str(table.notes))
            if table.children:
                for field in table.children:
                    tbfield = DBTableField(
                        mangled_info=str.strip(str(field))
                    )

                    tbfield.node = field  # To build cross-references
                    if field.notes:
                        tbfield.notes = retrieve_note_lines(field.notes)
                    dbtable.append_field(tbfield)
            dbtables.append(dbtable)

    if not dbtables:
        return ret

    longtab = LongTable(r"p{0.6\textwidth} p{0.34\textwidth}", pos="t")

    # Ordering of attributes of fields in displayed table
    fields = OrderedDict()
    fields["name"] = "field"
    fields["field_type"] = "type"
    fields["unique"] = "unique"
    fields["null"] = "null"
    fields["default"] = "default"

    # Build blocks for tables
    for idx, dbtable in enumerate(dbtables):
        longtab.add_row(
            [NE(fr"\textbf{{\textcolor{{{doc.ctx.regcol(doc.config.dbschema.tbl1_header_text_color)}}}{{{idx+1}. {EL(dbtable.name)}}}}}"), ""],
            color=doc.ctx.regcol(doc.config.dbschema.tbl1_header_row_color))
        longtab.append(NE(r"\rowcolor{white}"))

        mp1 = MiniPage(width=NE(r"\linewidth"), pos="t")
        mp1.append(NE(r"\small"))
        mp1.append(NE(fr'\hypertarget{{{dbtable.label}}}{{}}'))
        mp1.append(NE(fr"\rowcolors{{2}}{{{doc.ctx.regcol(doc.config.dbschema.tbl2_rowcolor_1)}}}"))
        mp1.append(NE(fr"{{{doc.ctx.regcol(doc.config.dbschema.tbl2_rowcolor_2)}}}"))
        tab_mp1 = Tabularx(NE(r">{\raggedright\arraybackslash}l l X X l"), width_argument=NE(r"\linewidth"), pos="t")
        tab_mp1.add_hline(color=doc.ctx.regcol(doc.config.dbschema.tbl2_header_line_color))

        header_text = list()
        for f in fields.keys():
            header_text.append(
                NE(
                    fr"\textcolor{{{doc.ctx.regcol(doc.config.dbschema.tbl2_header_text_color)}}}{{{EL(italic(fields[f]))}}}"
                )
            )

        tab_mp1.add_row(
            header_text,
            color=doc.ctx.regcol(
                doc.config.dbschema.tbl2_header_row_color
            )
        )
        tab_mp1.add_hline(color=doc.ctx.regcol(doc.config.dbschema.tbl2_header_line_color))

        # Build blocks for fields
        field_notes = OrderedDict()
        for tbfield in dbtable:
            if tbfield.notes:  # Preserve notes from table-fields
                field_notes[tbfield.name] = tbfield.notes
            row_text = list()
            for f in fields.keys():
                if f == "name":
                    cell_content = verbatim(getattr(tbfield, f))
                    if tbfield.pk:
                        cell_content = fr"{cell_content} \tiny{{\faKey }}"
                    if tbfield.ai:
                        cell_content = fr"{cell_content} \tiny{{\faArrowUp}}"
                    if tbfield.node.arrowlinked:
                        cell_content = fr"\hypertarget{{{get_label(tbfield.node.id)}}}{{{cell_content}}}"
                        margin_notes = list()
                        for arrowlink in tbfield.node.arrowlinked:
                            margin_notes.append(fr"\tiny{{$\Lsh$ \hyperlink{{{get_label(arrowlink.id)}}}{{{EL(arrowlink.parent)}: {EL(arrowlink).split(":")[0]}}}}}")
                        if len(margin_notes) > 0:
                            cell_content = fr"{cell_content} \marginnote{{{NE(r"\newline ".join(margin_notes))}}}"
                    elif tbfield.node.arrowlinks:
                        if len(tbfield.node.arrowlinks) > 1:
                            raise InvalidRefException(fr"More than one arrowlinks found for field {tbfield.name} in table {dbtable.name}")
                        else:
                            fk_label = get_label(tbfield.node.arrowlinks[0].id)
                            cell_content = fr"\mbox{{\makecell[l]{{{cell_content} \\ \tiny{{(\faKey \xspace \hyperlink{{{fk_label}}}{{{EL(tbfield.node.arrowlinks[0].parent)}}}}})}}}}\hypertarget{{{get_label(tbfield.node.id)}}}"
                    row_text.append(NE(cell_content))
                else:
                    val = getattr(tbfield, f)
                    row_text.append(val if val else " ")
            tab_mp1.add_row(row_text)

        tab_mp1.add_hline(color=doc.ctx.regcol(doc.config.dbschema.tbl2_header_line_color))
        mp1.append(tab_mp1)

        mp2 = MiniPage(width=NE(r"\linewidth"), pos="t")
        mp2.append(NE(r"\vspace{0.08cm}"))
        mp2.append(NE(r"\tinytosmall"))

        if field_notes:
            itmz = DBItemize(options=("nolistsep", "noitemsep"))
            for field_name in field_notes.keys():
                if len(field_notes[field_name]) > 1:
                    itmz.add_item(NE(verbatim(field_name+": ")))
                    inner_itmz = Itemize(options=("nolistsep", "noitemsep"))
                    for line in field_notes[field_name]:
                        inner_itmz.add_item(EL(line))
                    itmz.append(inner_itmz)
                else:
                    itmz.add_item(
                        NE(fr"""
{verbatim(field_name)}: {EL(field_notes[field_name][0])}
"""))
            mp2.append(itmz)

        longtab.add_row(mp1, mp2)
        longtab.append(NE(r"\rowcolor{white}"))

        mp3 = MiniPage(width=NE(r"\linewidth"), pos="t")
        mp3.append(NE(r"\tinytosmall"))
        if dbtable.notes:
            itmz = Itemize(options=["nolistsep", "noitemsep"])
            for note in dbtable.notes:
                itmz.add_item(EL(note))
            mp3.append(itmz)
            mp3.append(NE(r"\vspace{.2cm}"))

        longtab.append(NE(r"\multicolumn{2}{l}{"))
        longtab.append(mp3)
        longtab.append(NE(r"}\\"))
    ret.append(NE(r"\reversemarginpar"))
    ret.append(longtab)
    return ret

@track_processed_nodes
@limit_depth
def build_plaintext_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[str|LatexObject|NE]:
    """
    Build a plaintext-block in LaTeX using the content of supplied node.
    There could be one ore more paragraphs in the node-text. It is usually
    used to display non-section sepecific text, like content of a list item.

    Parameters
    ----------
    node : Node
        The node whose content and notes would be used to build this block of
        text.
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap
    builders: Dict[str, Callable]
        A dictionary of builders to be used for building the document
        components. The keys are the node types and values are the
        corresponding builder functions
    Returns
    -------
    list[str|LatexObject|NE]
        A list of strings, LaTeX objects, or NE objects representing the
        content of this node and its children
    """
    ret = list()
    if is_ignore_type(node):  # do not proceed if node is to be ignored
        return ret

    if ht := get_hypertarget(node, doc.ctx):
        ret.append(ht)

    ret.extend(get_node_text_blocks(node, doc.config, doc.ctx))

    child_list = list()

    if node.children:
        # If any paretnt was a list, then some special treatment is required here
        is_in_list_tree = list_exists_in_parent_path(node.parent, builders)
        if is_in_list_tree:
            child_list.append(Command("begin", "itemize")) \
                if doc.ctx.list_type_stack[-1] == "ul" \
                else child_list.append(Command("begin", "enumerate"))

        # Prepare content from child nodes
        for child in node.children:
            if is_ignore_type(child):
                continue

            if is_in_list_tree:
                child_list.append(Command("item"))
                # block_type = child.attributes.get(
                #     "fpcBlockType", doc.ctx.list_type_stack[-1])
                block_type = get_fpc_block_type(child, doc.ctx.list_type_stack[-1])
            else:
                block_type = "plaintext"
            child_content = builders[block_type](child, doc, depth, builders)
            child_list.extend(child_content)

        if is_in_list_tree:
            child_list.append(Command("end", "itemize")) \
                if doc.ctx.list_type_stack[-1] == "ul" \
                else child_list.append(Command("end", "enumerate"))

    if is_stopframe_type(node):
        note_text_blocks = get_stopframe_block(node, doc.ctx)
    else:
        note_text_blocks = get_note_text_blocks(node, doc.config, doc.ctx)
    notes_position = get_direction(
        # node.attributes.get("fpcNotesPosition", "n"))
        get_fpc_notes_position(node, "n"))
    if notes_position == "n":  # notes of node should appear before children
        ret.append(Command("par"))
        ret.extend(note_text_blocks)

        # Check if any items other than begin and end commands are present in
        # the child-list (means not all children are of ignore type).
        if len(child_list) > 2:
            ret.extend(child_list)
    elif notes_position == "s":  # notes of node should appear after children
        ret.extend(child_list)
        ret.extend(note_text_blocks)
    else:
        raise ValueError(
            f"Invalid value for fpcNotesPosition attribute: '{notes_position}'"
            f" found for node '{node}' with id {node.id}. Only 'north' and "
            "'south' are allowed."
        )
    doc.ctx.flush_margin_comments(
        get_flag_refs(node, doc.config,doc.ctx), ret)
    doc.ctx.flush_margin_comments(get_references(node, back_ref=True), ret)
    return ret

def _construct_list_of_type(
        list_type: str, node: Node, doc: GeneralDoc,
        depth: int, builders: Dict[str, Callable]
) -> List[str|LatexObject|NE]:
    """
    Build and return a list of LaTeXObject, str, or NE.
     ----------
    list_type: str
        The type of list to be built. It can be either "ul" or "ol".
    node : Node
        The node containing the children who would be part of the list
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap
    builders: Dict[str, Callable]
        Dictionary of builder functions
    Returns
    -------
    list[str|LatexObject|NE]
        A list of strings, LaTeX objects, or NE objects representing the
        content of the unordered-list 
    """

    if list_type not in ["ul", "ol"]:
        raise ValueError(
            f"Invalid value for list_type: '{list_type}' found for node "
            f"'{node}' with id {node.id}. Only 'ul' and 'ol' are allowed."
        )

    ret = list()
    if is_ignore_type(node):
        return ret
    if ht := get_hypertarget(node, doc.ctx):
        ret.append(ht)
    
    # Register current list-type which would be used by appropriate builder
    # functions of child nodes to identify the type of list to be built, if
    # none were specified explicitly.
    doc.ctx.list_type_stack.append(list_type)

    # If any node in the path from current node to the root node is of
    # type orderedlist, or unorderedlist, then this node can not be of
    # type default. That means its text should be rendered as a mere
    # item-text and its notes. Else node-text should be a suitable
    # section-header.
    # Build current node's text-blocks based on above conditions.
    if list_exists_in_parent_path(node.parent, builders):
        node_text_blocks = get_node_text_blocks(node, doc.config, doc.ctx)
        note_position = get_fpc_notes_position(node, "n")
    else:
        node_text_blocks = doc.sections[depth](NE(EL(str(node))), label=False)

        # notes always come after section-name, but before child-content
        note_position = "n"

    # Build current node's note-blocks.
    if is_stopframe_type(node):
        note_text_blocks = get_stopframe_block(node, doc.ctx)
    else:
        note_text_blocks = get_note_text_blocks(node, doc.config, doc.ctx)

    # Now build children-blocks, if any, using suitable builder functions and
    # create a unified list of all childred and grandchildren.
    has_children = True if node.children else False
    children_block = list()
    if has_children:
        # Initialize the list-type based on the input list_type.
        begin_cmd = Command("begin", "itemize") if list_type == "ul" \
            else Command("begin", "enumerate")
        end_cmd = Command("end", "itemize") if list_type == "ul" \
            else Command("end", "enumerate")

        child_blocks = list()
        for child in node.children:
            if is_ignore_type(child):
                continue
            block_type = get_fpc_block_type(child, "plaintext")
            child_content = [Command("item"), ]
            child_content.extend(
                builders[block_type](child, doc, depth, builders))
            child_blocks.extend(child_content)
        if child_blocks:
            children_block.append(begin_cmd)
            children_block.extend(child_blocks)
            children_block.append(end_cmd)

    # Based on the note-position, arrange node's text-block, child-contents
    # and note-text in ret list and return it.
    ret.append(node_text_blocks) if type(node_text_blocks) is not list \
        else ret.extend(node_text_blocks)
    if note_position == "s":
        ret.extend(children_block)
        ret.append(Command("par"))
        ret.extend(note_text_blocks)
    else:  # it is "n"
        ret.append(Command("par"))
        ret.extend(note_text_blocks)
        ret.extend(children_block)

    # Unregister current list-type and return the block built by now
    doc.ctx.list_type_stack.pop()
    return ret

@track_processed_nodes
@limit_depth
def build_unorderedlist_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[str|LatexObject|NE]:
    """
    Build an unordered-list block in LaTeX using the content of supplied node.

    Parameters
    ----------
    node : Node
        The node containing the children who would be part of the unordered-list
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap
    builders: Dict[str, Callable]
        Dictionary of builder functions
    Returns
    -------
    list[str|LatexObject|NE]
        A list of strings, LaTeX objects, or NE objects representing the
        content of the unordered-list 
    """
    return _construct_list_of_type("ul", node, doc, depth, builders)

@track_processed_nodes
@limit_depth
def build_orderedlist_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[str|LatexObject|NE]:
    """
    Build an ordered-list block in LaTeX using the content of supplied node.

    Parameters
    ----------
    node : Node
        The node containing the children who would be part of the ordered-list
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap
    builders: Dict[str, Callable]
        Dictionary of builder functions
    Returns
    -------
    list[str|LatexObject|NE]
        A list of strings, LaTeX objects, or NE objects representing the
        content of the ordered-list 
    """
    return _construct_list_of_type("ol", node, doc, depth, builders)
    
@track_processed_nodes
def build_image_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[str|LatexObject|NE]:
    """
    Build an image-block in LaTeX using the image associated with supplied
    node, if any.

    Parameters
    ----------
    node : Node
        The current node containing the image
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap
    builders: Dict[str, Callable]
        Dictionary of builder functions
    Returns
    -------
    list[str|LatexObject|NE]
        A list of LaTeX objects containing an image block
    """
    ret = list()
    if is_ignore_type(node):  # do not proceed if node is to be ignored
        return list()

    if not node.imagepath:  # No imagepath found
        return ret
    if ht := get_hypertarget(node, doc.ctx):
        ret.append(ht)

    # img_path = self.get_absolute_file_path(Path(node.imagepath))
    img_path = doc.get_absolute_file_path(PurePosixPath(node.imagepath))

    f_ext = img_path.suffix.lower()
    if f_ext == ".svg":  # SVG images need conversion to PDF
        new_img_path = PurePosixPath(str(doc.ctx.images_dir), img_path.stem+".pdf")

        # Convert SVG image to PDF
        try:
            svg2pdf(url=str(img_path), write_to=str(new_img_path))
        except Exception as e:
            raise UnsupportedFileException(
                f"Failed to convert SVG file {node.imagepath} to PDF: {str(e)}"
            )
    # Other images must be either of type JPEG, or PNG only
    elif f_ext not in {".jpg", ".png", ".jpeg"}:
        raise UnsupportedFileException(
            f"File {node.imagepath} is not of type embeddable to PDF "
                "document. Please use an image file of type JPG, PNG, or SVG."
        )
    else:  # Use original absolute image path
        new_img_path = img_path

    # if to_bool(node.attributes.get("fpcShowCaption", "True")):
    if to_bool(get_fpc_show_caption(node, "True")):
        fig = build_latex_figure_object(
            new_img_path, doc.config.main.figure_width, str(node)
        )
    else:
        fig = build_latex_figure_object(
            new_img_path, doc.config.main.figure_width)

    note_text = get_processed_note_lines(node, doc.ctx)
    if len(note_text):  # if notes exist, render its content
        notes_position = get_direction(
            get_fpc_notes_position(node, "s"))
        if notes_position == "n":
            for line in note_text:
                ret.extend(line)
            ret.append(fig)
        elif notes_position == "s":
            ret.append(fig)
            for line in note_text:
                ret.extend(line)
        else:
            raise ValueError(
                f"Unknown value for attribue fpcNotesPosition '{notes_position}'"
                f" found for node '{node}' with id {node.id}.")
    else:
        ret.append(fig)
    doc.ctx.flush_margin_comments(
        get_flag_refs(node, doc.config,doc.ctx), ret)
    doc.ctx.flush_margin_comments(get_references(node, back_ref=True), ret)
    return ret

@track_processed_nodes
def build_verbatim_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[str|LatexObject|NE]:
    """
    Build a block of text in monospace fixed-font format using the supplied
    node-content and return it along with node-notes, if any. It is used mostly
    to display code-items, JSON or XML based content where fixed indentation is
    required.

    The position of note-text is decided based on the value supplied for the
    node-attribute fpcNotesPosition. They are printed first if value of this
    attribute is 'n'. If its value is 's', then they are printed below the
    content of the node.

    Parameters
    ----------
    node : Node
        The current node being processed for building the verbatim node-text
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap
    builders: Dict[str, Callable]
        Dictionary of builder functions
    Returns
    -------
    list[str|LatexObject|NE]
        A list of LaTeX objects representing either verbatim and non-verbatim
        text.
    """
    ret = list()
    if is_ignore_type(node):  # do not proceed if node is to be ignored
        return ret

    if ht := get_hypertarget(node, doc.ctx):
        ret.append(ht)

    fblocks = get_flag_blocks(node, doc.config, doc.ctx)
    ftext = " ".join([dump(b) for b in fblocks]) if fblocks else ""

    frefs = get_flag_refs(node, doc.config, doc.ctx)
    note_lines = []
    if node.notes:
        note_lines.extend(get_processed_note_lines(node, doc.ctx))


    # Prepare verbatim content using the node-text and flag-text, if any.
    content = list()
    if ftext:
        content.extend([NE(ftext), NE(r"\xspace")])

    content.append(NE(fr"""
\begin{{verbatim}}
{NE(str(node))}
\end{{verbatim}}"""))

    # Add references to change-sets, if any
    if len(frefs):
        doc.ctx.flush_margin_comments(frefs, ret)

    # Collect back-references, if any
    if backrefs := get_references(node, back_ref=True):
        doc.ctx.flush_margin_comments(backrefs, ret)

    if len(note_lines):
        notes_position = get_direction(
            get_fpc_notes_position(node, "s"))
        if  notes_position == "s":
            ret.extend(content)
            for line in note_lines:
                ret.extend(line)
                ret.append(NE(r"\par"))
            ret[-1] = ""  # remove last \par to prevent unnecessary newline
            return ret

        elif notes_position == "n":
            for line in note_lines:
                ret.extend(line)
                ret.append(NE(r"\par"))
            ret[-1] = ""  # remove last \par to prevent unnecessary newline
            ret.extend(content)
            return ret
        else:
            raise ValueError(f"Invalid value '{notes_position}' supplied for"
                             " node-attribute fpcNotesPosition in node '{node}'."
                             " It must be either 's' (south) or 'n' (north).")
    ret.extend(content)
    return ret

@track_processed_nodes
def build_verbatimnotes_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[Optional[str|LatexObject|NE]]:
    """
    Build a block of LaTeX verbatim text using the notes associated with
    supplied node, if any. It is used mostly to display code-text, JSON or XML
    based content which should be rendered in fixed-width fonts.

    NOTE: Please note that it is not possible at presesnt to suppport
    stop-frame as well as notes in verbatim mode. The former won't render.

    Parameters
    ----------
    node : Node
        The current node being processed for building the verbatim note-text
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap
    builders: Dict[str, Callable]
        Dictionary of builder functions
    Returns
    -------
    list[str|LatexObject|NE]
        A list of str, LaTeX, or NE objects representing the verbatim text
        found in the notes of the node, along with other applicable content
    """
    ret = list()
    if is_ignore_type(node):  # do not proceed if node is to be ignored
        return ret

    if ht := get_hypertarget(node, doc.ctx):
        ret.append(ht)

    # The node-text is captured and rendered first as no direction for notes
    # is applicable in this mode of rendering. Notes always come later.
    ret.extend(get_node_text_blocks(node, doc.config, doc.ctx))
    if node.notes:
        ret.append(f"\\begin{{verbatim}}\n{node.notes}\n\\end{{verbatim}}")
    return ret

@track_processed_nodes
def build_ucpackage_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[str|LatexObject|NE]:
    """
    Build and return usecase-specific blocks of LaTeX elements using the
    supplied node and its children.

    Parameters
    ----------
    node : Node
        The current node being processed for building the usecase block
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap
    builders: Dict[str, Callable]
        Dictionary of builder functions
    Returns
    -------
    list[str|LatexObject|NE]
        A list of strings, LaTeX objects, or NE objects representing the
        content of this node and its children
    """
    ret = list()
    if is_ignore_type(node):  # do not proceed if node is to be ignored
        return ret

    if ht := get_hypertarget(node, doc.ctx):
        ret.append(ht)

    actor_nodes: Set[Node] = set()
    action_nodes: List[Node] = list()  # to be used in building text-segments
    child_nodes: List[Node] = list()
    if node.children:
        # Process children and build data structures required for usecase
        # blocks.
        for child in node.children:
            if is_ignore_type(child):
                continue

            # Retrieve usecase related data now.
            if is_ucaction_type(child) or is_ucpackage_type(child):
                child_nodes.append(child)

                # Collect actor nodes which are connected only to an action node.
                if is_ucaction_type(child):
                    action_nodes.append(child)
                    for item in child.arrowlinked:
                        if is_actor_node(item):
                            actor_nodes.add(item)
            else: # Only action-nodes and package-nodes are allowed
                raise InvalidNodeException(
                    f"Invalid node '{child}' having id {child.id} of type "
                    f"{get_fpc_block_type(child, "<no-type>")} "
                    f"found under usecase system: '{node}' having id {node.id}. "
                    "All nodes under any usecase package-node must be of type "
                    "UCPackage, or UCAction only. Please fix the mindmap "
                    "accordingly."
                )

        dia = UseCaseDiagram(doc.config.uml)

        # Actor nodes are kept out of the package.
        for acr_node in actor_nodes:
            actor: Actor = ActorFactory.create_actor(acr_node)
            dia.add_component(actor)

        # Then include package node
        dia.add_component(Package(node))

        for child_node in child_nodes:
            child = Usecase(child_node)
            dia.add_component(child)
            for actor_node in child_node.arrowlinked:
                if is_actor_node(actor_node): # Ensure linked node is an actor node
                    # Create a relationship between the actor and the child nodes
                    rel = Relationship(actor_node, child_node)
                    dia.add_component(rel)

        # Create PUML file in the working directory
        file_name = f"{node.id}"
        puml_file_path = Path(str(
            doc.ctx.working_dir), f"{file_name}.puml")
        with open(puml_file_path, "w") as puml_file:
            puml_file.write(str(dia))
        try:
            puml2svg(
                doc.config.uml.plantuml_cmd,
                puml_file_path,
                Path(str(doc.ctx.images_dir))
            )
            svg_file_path = Path(str(doc.ctx.images_dir), f"{file_name}.svg")
            pdf_file_path = Path(str(doc.ctx.images_dir), f"{file_name}.pdf")
            svg2pdf(url=str(svg_file_path), write_to=str(pdf_file_path))
        except Exception as e:
            raise FileConversionException(f"Unable to convert {puml_file_path} to PDF: {e}")

        ret.append(NE(r"\noindent"))

        # image part
        img_segment = NE(
            r"\begin{center}"
            fr"\includegraphics[width={doc.config.uml.usecase_diagram_width}]{{{pdf_file_path}}}"
            r"\end{center}"
        )
        ret.append(img_segment)

        # Build tabular segment for the usecase-details
        tbl_segment = build_ucaction_tabular_segments(action_nodes)
        if tbl_segment:
            # Small font-size for the usecase details
            ret.append(NE(r"\small"))
            ret.extend(tbl_segment)
            ret.append(NE(r"\normalsize"))
    return ret


@track_processed_nodes
@limit_depth
def build_default_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[str|LatexObject|NE]:
    """
    Build a section/subsection/subsubsection/... kind of block in LaTeX using
    the content of supplied node. The node-text would be treated as respective
    section-header, and its note-text would be the content of the corresponding
    section. There could be one ore more lines in the note-text, which would be
    treated as part of separate paragraphs.

    Parameters
    ----------
    node : Node
        The node containing the header-text
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap
    builders: Dict[str, Callable]
        A dictionary of builders to be used for building the document
        components. The keys are the node types and values are the
        corresponding builder functions
    Returns
    -------
    list[str|LatexObject|NE]
        A list of strings, LaTeX objects, or NE objects representing the
        content of this block of text
    """
    ret = list()
    if is_ignore_type(node):  # do not proceed if node is to be ignored
        return ret

    if ht := get_hypertarget(node, doc.ctx):
        ret.append(ht)
    
    fblocks = get_flag_blocks(node, doc.config, doc.ctx)
    ftext = " ".join([dump(b) for b in fblocks]) if fblocks else ""

    if ftext:
        ret.append(
            doc.sections[depth](
                NE(fr"{ftext}\xspace {EL(str(node))}"), label=False))
    else:
        ret.append(doc.sections[depth](NE(EL(str(node))), label=False))

    note_text_blocks = get_note_text_blocks(node, doc.config, doc.ctx)
    ret.extend(note_text_blocks)

    # Changeset section specific backreferences
    doc.ctx.flush_margin_comments(
        get_flag_refs(node, doc.config, doc.ctx), ret)


    # Add backreferences to that node, if any
    doc.ctx.flush_margin_comments(get_references(node, back_ref=True), ret)
    
    # Process children (if any) too in the same manner
    if node.children:
        for child in node.children:
            block_type = get_fpc_block_type(child, "default")
            child_content = builders[block_type](child, doc, depth+1, builders)
            ret.extend(child_content)

    return ret

@track_processed_nodes
def build_numbertable_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[str|LatexObject|NE]:
    """
    Build a number-table-block in LaTeX using the contents of the chidren of
    the supplied node.

    Parameters
    ----------
    node : Node
        The current node containing the content of the number-table
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap (not used here)
    builders: Dict[str, Callable]
        Dictionary of builder functions (not used here)
    Returns
    -------
    list[str|LatexObject|NE]
        A list of LaTeX objects containing a number-table block
    """
    ret = list()
    if is_ignore_type(node):  # do not proceed if node is to be ignored
        return ret

    if ht := get_hypertarget(node, doc.ctx):
        ret.append(ht)

    fblocks = get_flag_blocks(node, doc.config, doc.ctx)
    ftext = " ".join([dump(b) for b in fblocks]) if fblocks else ""

    # Find out if parent of this node comes under a list type or
    # section/subsection/... type of node. or under some kind of list. Based on that the content of its
    # block of test would change.
    if list_exists_in_parent_path(node.parent, builders):
        if ftext:
            ret.append(NE(fr"{ftext}\xspace {EL(str(node))}"))
        else:
            ret.append(EL(str(node)))
    else:
        if ftext:
            ret.append(
                doc.sections[depth](
                    NE(fr"{ftext}\xspace {EL(str(node))}"), label=False))
        else:
            ret.append(doc.sections[depth](NE(EL(str(node))), label=False))

    # Following keys are expected in the following dictionary:
    # "alingments", "headers", "rows", "totals", "notes", "tblprops"
    tbl_data = retrieve_number_table_data(node, doc.ctx)

    tab = Tabular("".join(tbl_data["alignments"]), pos="c")
    tab.add_hline(color=doc.ctx.regcol(doc.config.table.line_color))
    row = [
        NE(
            fr"""
\small{{\color{{{doc.ctx.regcol(doc.config.table.header_text_color)}}}%
\textsf{{{bold(tbl_data["tblprops"]["column1"])}}}}}"""
        ),
    ]
    row.extend(
        [
            NE(fr"""
\small{{\color{{{doc.ctx.regcol(doc.config.table.header_text_color)}}}%
\textsf{{{bold(hdr)}}}}}"""
            ) for hdr in tbl_data["headers"]
        ]
    )
    tab.add_row(
        *row,
        color=doc.ctx.regcol(doc.config.table.header_row_color),
        strict=True)
    tab.add_hline(color=doc.ctx.regcol(doc.config.table.line_color))
    for row in tbl_data["rows"]:
        tab.add_row(*row)
    tab.add_hline(color=doc.ctx.regcol(doc.config.table.line_color))

    # If summing required, then add a row for totals
    if tbl_data["totals"]:
        row = [NE(fr"""
\small{{\color{{{doc.ctx.regcol(doc.config.table.header_text_color)}}}%
\textsf{{{bold("Total")}}}}}"""), ]
        for hdr in tbl_data["headers"]:
            if tbl_data["totals"].get(hdr, None):
                row.append(NE(fr"""
\small{{\color{{{doc.ctx.regcol(doc.config.table.header_text_color)}}}%
\textsf{{{bold(tbl_data["totals"][hdr])}}}}}"""))
            else:
                row.append(NE(""))
        tab.add_row(
            *row,
            color=doc.ctx.regcol(doc.config.table.footer_row_color),
            strict=True
        )
        tab.add_hline(color=doc.ctx.regcol(doc.config.table.line_color))

    # Section-notes are collected now
    section_note_lines = get_processed_note_lines(node, doc.ctx)
    notes_position = get_direction(get_fpc_notes_position(node, "n"))
    if notes_position == "n":
        for line in section_note_lines:
            ret.extend(line)
            ret.append(Command("par"))

    # Append tabular object
    ret.append(Command("begin", arguments=("center", )))
    ret.append(tab)

    # Then check if notes are to be collected for the same node
    if tbl_data["notes"]:
        ret.append(tbl_data["notes"])
    ret.append(Command("end", arguments=("center", )))

    if notes_position == "s":
        for line in section_note_lines:
            ret.extend(line)
            ret.append(Command("par"))

    # Now return the full block's content
    return ret

@track_processed_nodes
def build_table_block(
        node: Node,
        doc: GeneralDoc,
        depth: int,
        builders: Dict[str, Callable]
    ) -> List[str|LatexObject|NE]:
    """
    Build a table-block in LaTeX using the contents of the chidren of the
    supplied node.

    Parameters
    ----------
    node : Node
        The current node containing the content of the table
    doc : GeneralDoc
        The document being built
    depth : int
        Depth of the node supplied in the mindmap (not used here)
    builders: Dict[str, Callable]
        Dictionary of builder functions (not used here)
    Returns
    -------
    list[str|LatexObject|NE]
        A list of LaTeX objects containing a table block
    """
    ret = list()
    if is_ignore_type(node):  # do not proceed if node is to be ignored
        return ret

    if tab_notes := retrieve_table_and_notelist(
        node, doc.config, doc.ctx):
        if ht := get_hypertarget(node, doc.ctx):
            ret.append(ht)

        ret.append(Command("begin", arguments=("center", )))  # Align center
        ret.append(tab_notes[0])
        ret.append(Command("end", arguments=("center", )))
        if len(tab_notes) > 1:  # Note-text is to be rendered
            itmz = Itemize()
            for h, c in tab_notes[1]:
                if len(c) == 1:  # Single line note is to be rendered
                    itmz.add_item(NE(f"{bold(h)}: "))
                    for i in c[0]:
                        itmz.append(i)
                else:  # Multiline notes are rendered as unordered list
                    itmz.add_item(NE(f"{bold(h)}:\n"))
                    item = Itemize()
                    for i in c:
                        item.append(Command("item"))
                        for j in i:
                            item.append(j)
                    itmz.append(item)
            ret.append(itmz)
    return ret

# Reusing some of the existing builder functions for certain block-types
build_meeting_block = build_default_block
build_project_block = build_default_block
build_modules_block = build_default_block
build_risks_block = build_orderedlist_block
build_agenda_block = build_orderedlist_block
build_actions_block = build_orderedlist_block
build_requirements_block = build_orderedlist_block
build_ucactors_block = build_unorderedlist_block
build_participants_block = build_orderedlist_block

# Few canonical names of list-blocks
build_ol_block = build_orderedlist_block
build_ul_block = build_unorderedlist_block
