"""
Various utility functions to generate generate code to render usecase diagrams
and associated details in LaTeX.
"""

from pathlib import Path
import subprocess
from freeplane import Node
from typing import List, Set
from cairosvg import svg2pdf
from pylatex import LongTable, MultiColumn, MultiRow
from pylatex.utils import NoEscape as NE

from fp_convert.utils.helpers import (
    DocContext,
    Theme,
    is_ignore_type,
    node_type_detector_factory,
)
from fp_convert.utils.uml.plantuml import (
    Package, ActorFactory, Actor, Relationship, Usecase, UseCaseDiagram
)
from fp_convert.errors import InvalidNodeException

node_type_codes = {
    "up": {  # Usecase-System
        "icons": set(),
        "attr": "ucpackage",
    },
    "ur": {  # Usecase-Actors
        "icons": set(),
        "attr": "ucactors",
    },
    "ua": {  # Usecase-Action
        "icons": set(),
        "attr": "ucaction",
    },
}

# Node-type detectors for the above node-types
is_ucpackage_type = node_type_detector_factory("up", node_type_codes)
is_ucactors_type = node_type_detector_factory("ur", node_type_codes)
is_ucaction_type = node_type_detector_factory("ua", node_type_codes)

def is_actor_node(node: Node) -> bool:
    """
    Check if the supplied node is a usecase-actor node.

    Parameters:
        node: Node
            The node to be checked.

    Returns:
        bool: True if the node is a usecase-actor node, False otherwise.
    """
    if node:
        # Check if its parent is a usecase-actors node
        if node.parent and is_ucactors_type(node.parent):
            return True
    return False

def build_ucaction_tabular_segments(action_nodes: List[Node]) -> List[LongTable]:
    """
    Build and return a tabular segment for the usecase actions.

    Parameters:
    action_nodes: List[Node]
        List of action nodes to be included in the tabular segment.
    """
    ret: List[LongTable] = []
    for action_node in action_nodes:
        if is_ignore_type(action_node) or not action_node.children:
            continue  # Skip if ignored or no conditions are present

        conditions: dict[Node, list[Node]] = {}
        for condition in action_node.children:
            if is_ignore_type(condition):
                continue  # skip if ignored

            flows: List[Node] = list()
            for flow in condition.children:
                if is_ignore_type(flow):
                    continue  # skip if ignored or no flows are present
                flows.append(flow)
            if flows:
                conditions[condition] = flows

        if not conditions:
            continue  # Nothing to do if relevant nodes are absent

        tbl = LongTable(
            r"|p{0.15\textwidth} p{0.78\textwidth}|"
            # "ll"
        )
        tbl.add_hline()
        tbl.add_row((MultiColumn(2, align='|c|', data=str(action_node)),))
        tbl.end_table_header()
        tbl.add_hline()

        # Build tabular conent having conditions and flow details
        for condition, flows in conditions.items():
            for idx, item in enumerate(flows[:-1]):
                tbl.add_row("", f"{str(item)}")

            # Add the multirow section at the end to ensure that row-text
            # always renders on top layer. Otherwise it may get hidden.
            tbl.add_row((MultiRow(NE(-abs(len(flows))), data=f"{str(condition)}"), f"{str(flows[-1])}"))
            tbl.add_hline()

        ret.append(tbl)

    return ret

def build_usecase_blocks(node: Node, ctx: DocContext, theme: Theme) -> List:
    """
    Build and return usecase blocks using supplied node and its children.
    """
    ret = list()
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
                    f"{child.attributes.get("fpcBlockType", "<no-type>")} "
                    f"found under usecase system: '{node}' having id {node.id}. "
                    "All nodes under any usecase package-node must be of type "
                    "UCPackage, or UCAction only. Please fix the mindmap "
                    "accordingly."
                )

        dia = UseCaseDiagram(theme)

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
        puml_file_path = Path(str(ctx.working_dir), f"{file_name}.puml")
        with open(puml_file_path, "w") as puml_file:
            puml_file.write(str(dia))
        puml2svg(
            theme.config.uml_plantuml_cmd,
            puml_file_path,
            Path(str(ctx.images_dir))
        )
        svg_file_path = Path(str(ctx.images_dir), f"{file_name}.svg")
        pdf_file_path = Path(str(ctx.images_dir), f"{file_name}.pdf")
        svg2pdf(url=str(svg_file_path), write_to=str(pdf_file_path))

        # Two-column layout with small font-size for the usecase details
        ret.append(NE(r"\small"))
        ret.append(NE(r"\noindent"))

        # image part
        img_segment = NE(
            r"\begin{center}"
            fr"\includegraphics[width={theme.geometry.uml_usecase_diagram_width}]{{{pdf_file_path}}}"
            r"\end{center}"
        )
        ret.append(img_segment)

        # Build text segment for the usecase diagram
        ret.extend(build_ucaction_tabular_segments(action_nodes))
        ret.append(NE(r"\normalsize"))
    return ret

def puml2svg(puml_cmd: str, puml_file: Path, output_dir: Path) -> None:
    """
    Convert a PlantUML file to SVG format.

    Parameters:
    puml_cmd: str
        The command to invoke PlantUML.
    puml_file: Path
        The path to the PlantUML file.
    output_dir: Path
        The directory where the SVG file will be saved.
    """
    # Convert PUML to SVG using plantuml command line tool
    subprocess.run(
        [puml_cmd, '-tsvg', str(puml_file), '-o', str(output_dir)],
        check=True
    )

