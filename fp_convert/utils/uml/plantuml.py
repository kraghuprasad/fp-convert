# PlantUML text generators for Python
# See https://plantuml.com
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import List
from enum import StrEnum

from freeplane import Node
from fp_convert.utils.helpers import retrieve_note_lines

class Direction(StrEnum):
    """
    Enumeration of possible directions in a plantuml based diagram
    """
    LR = "left to right direction"
    TB = "top to bottom direction"
    RO = "right of"
    LO = "left of"
    TO = "top of"
    BO = "bottom of"
    L = "left"
    R = "right"
    U = "up"
    D = "down"

class PUMLEntity(ABC):
    @abstractmethod
    def __init__(self, node: Node):
        """
        Initialize the object.

        This method must be overridden in any concrete subclass of
        PUMLEntity. It is used to initialize the object with the
        necessary information from the freeplane node.

        Parameters
        ----------
        node : freeplane.Node
            The freeplane node containing the information to be
            used to initialize the object.
        """
        self.node = node

class ActorFactory:
    """
    A factory for creating and managing unique actors identified by their
    respective node-ids.
    """
    _repo: dict[str, 'Actor'] = {}
    """
    A repository to hold all actors uniquely identified by their IDs.
    This is a class variable, so it is shared across all instances of Actors.
    """

    @classmethod
    def create_actor(cls, node: Node) -> 'Actor':
        """
        Create a new actor and add it to the repository.

        Parameters
        ----------
        node : Node
            The node representing the actor.

        Returns
        -------
        Actor
            The created actor.
        """
        if node.id not in cls._repo:
            cls._repo[node.id] = Actor(node)
        return cls._repo[node.id]


class Actor(PUMLEntity):
    def __init__(self, node: Node):
        """
        Constructor of the Actor.

        :param node: The node representing the actor. It must contain an attribute
        "fpcBlockType" with value "UCActor".
        """
        super().__init__(node)

    def __str__(self) -> str:
        return f"actor \"{self.node}\" as {self.node.id} {self.node.attributes.get('fpcStereoType', '')}\n{Note(self.node)}"


class Note(PUMLEntity):
    def __init__(self, node: Node):
        self.notes = "\n".join(retrieve_note_lines(node.notes)) if node.notes else None
        self.direction = Direction[node.attributes.get('fpcNotesDirection', 'LO')]
        if self.direction not in {Direction.RO, Direction.LO, Direction.TO, Direction.BO}:
            raise ValueError(f"Invalid direction specified for notes in the node '{node}'. It must be one of: RO, LO, TO, or BO.")
        super().__init__(node)

    def __str__(self):
        return f"note {self.direction} {self.node.id}\n{self.notes}\nend note" if self.notes else ""


class Package(PUMLEntity):
    def __init__(self, node: Node):
        """
        Constructor of the Package.

        :param node: The node representing the package. It must contain an attribute
        "fpcBlockType" with value "UCSystem".
        """
        self.direction = Direction[node.attributes.get('fpcUCPDirection', 'LR')]
        if self.direction not in {Direction.LR, Direction.TB}:
            raise ValueError(
                f"Invalid direction specified for package '{node} with id "
                f"{node.id}'. It must be one of: LR or TB.")
        super().__init__(node)

    def __str__(self) -> str:
        return str(self.direction)

class Usecase(PUMLEntity):
    def __init__(self, node: Node):
        """
        Constructor of the Usecase.

        :param node: The node representing the usecase. It must contain an attribute
        "fpcBlockType" with value "UCAction".
        """
        super().__init__(node)
    
    def __str__(self) -> str:
        return f"({self.node}) as {self.node.id}"

class Relationship(PUMLEntity):
    def __init__(self, src_node: Node, dst_node: Node, label: str = ""):
        """
        Constructor of the Relationship.

        :param src_node: The source node of the relationship.
        :param dst_node: The destination node of the relationship.
        :param label: An optional label for the relationship.
        """
        self.src_node = src_node
        self.dst_node = dst_node
        self.label = label

    def __str__(self) -> str:
        return f"{self.src_node.id} --> {self.dst_node.id} : {self.label}" \
            if self.label else f"{self.src_node.id} --> {self.dst_node.id}"

class Diagram:
    """
    Base class for all PlantUML diagrams.
    This class provides a common interface for all diagrams and
    allows for easy extension and customization.
    """
    def __init__(self, theme=None):
        self.components = []
        self.repo: set[PUMLEntity] = set()
        self.theme = theme

    def add_component(self, component: PUMLEntity) -> None:
        """
        Add a component to the diagram.

        Parameters
        ----------
        component : PUMLEntity
            The component to be added to the diagram.
        """
        if self.repo and component in self.repo:
            # If the component already exists in the repository, do not add it again
            return

        self.repo.add(component)
        self.components.append(component)


    def _build_package_blocks(
            self,
            package: Package,
            components: List[PUMLEntity],
            ret: List[str]) -> None:
        """
        Build and return a list of string-blocks under supplied package.

        Parameters
        ----------
        package : Package
            The package under which the components are to be built.
        components : List[PUMLEntity]
            The list of components to be converted to strings under supplied
            package.
        ret : List[str]
            A list to hold the string representations of the components.
        """
        if not isinstance(package, Package):
            # Supplied package must be a Package instance.
            raise TypeError(f"Expected a Package instance, got {type(package)}")

        with container(package, ret) as lst:
            for idx, component in enumerate(components):
                if not isinstance(component, Package):
                    # If the component is not a Package, add it to the list
                    # and continue.
                    lst.append(str(component))
                else:  # Recursively build the package blocks
                    self._build_package_blocks(
                        component, components[idx+1:], lst)

    def __str__(self) -> str:
        """
        Generate the PlantUML text representation of the diagram.

        Returns
        -------
        str
            The PlantUML text representation of the diagram.
        """
        ret: List[str] = []
        if self.theme:
            ret.append(f"skinparam actorBackgroundColor {self.theme.colors.uml_actor_background_color}")
            ret.append(f"skinparam actorBorderColor {self.theme.colors.uml_actor_border_color}")
            ret.append(f"skinparam actorColor {self.theme.colors.uml_actor_color}")
            ret.append(f"skinparam backgroundColor {self.theme.colors.uml_background_color}")
            ret.append(f"skinparam componentBackgroundColor {self.theme.colors.uml_component_background_color}")
            ret.append(f"skinparam componentBorderColor {self.theme.colors.uml_component_border_color}")
            ret.append(f"skinparam componentColor {self.theme.colors.uml_component_color}")
            ret.append(f"skinparam defaultTextAlignment {self.theme.config.uml_default_text_alignment}")
            ret.append(f"skinparam lineType {self.theme.config.uml_connector_line_type}")
            ret.append(f"skinparam noteBackgroundColor {self.theme.colors.uml_note_background_color}")
            ret.append(f"skinparam noteBorderColor {self.theme.colors.uml_note_border_color}")
            ret.append(f"skinparam noteColor {self.theme.colors.uml_note_color}")
            ret.append(f"skinparam packageBackgroundColor {self.theme.colors.uml_package_color}")
            ret.append(f"skinparam packageBorderColor {self.theme.colors.uml_package_border_color}")
            ret.append(f"skinparam usecaseBackgroundColor {self.theme.colors.uml_usecase_color}")
            ret.append(f"skinparam usecaseBorderColor {self.theme.colors.uml_usecase_border_color}")

        for idx, component in enumerate(self.components):
            if isinstance(component, Package):
                # If the component is a Package, build the package blocks with
                # remaining components.
                self._build_package_blocks(component, self.components[idx+1:], ret)
                break
            else:
                ret.append(str(component))

        # Join all components into a single string
        if ret:
            components_str = "\n".join(ret)
        else:  # Raise error as there is nothing to draw
            raise ValueError(
                "No UML components in the diagram. Please fix the mindmap "
                "first. There must be at least one node with attribute "
                "'fpcBlockType' set to a valid UML component-type value "
                "like UCAction, UCActor, or Relationship to build a UML "
                "diagram. Please refer the documentation of fp-convert "
                "for more details.")

        # Return the PlantUML text for the resultant diagram
        return f"@startuml\n{components_str}\n@enduml"


class UseCaseDiagram(Diagram):
    def __init__(self, theme=None):
        super().__init__(theme)


class SequenceDiagram(Diagram):
    def __init__(self, theme=None):
        super().__init__(theme)


class ContextDiagram(Diagram):
    def __init__(self, theme=None):
        super().__init__(theme)


class TreeDiagram(Diagram):
    def __init__(self, theme=None):
        super().__init__(theme)


class WBSDiagram(Diagram):
    def __init__(self, theme=None):
        super().__init__(theme)


class ActivityDiagram(Diagram):
    def __init__(self, theme=None):
        super().__init__(theme)


class StateDiagram(Diagram):
    def __init__(self, theme=None):
        super().__init__(theme)


class StateMachineDiagram(Diagram):
    def __init__(self, theme=None):
        super().__init__(theme)


class ClassDiagram(Diagram):
    def __init__(self, theme=None):
        super().__init__(theme)


class ComponentDiagram(Diagram):
    def __init__(self, theme=None):
        super().__init__(theme)


class DeploymentDiagram(Diagram):
    def __init__(self, theme=None):
        super().__init__(theme)

@contextmanager
def container(obj: PUMLEntity, lst: List[str]):
    try:
        lst.append(f"{obj.__class__.__name__.lower()} \"{str(obj.node)}\" {{")
        if isinstance(obj, Package):  # PUMLEntity specific handling
            lst.append(str(obj.direction))
        yield lst
    finally:
        lst.append("}")

    def __str__(self) -> str:
        return f"{self.__class__.__name__.lower()} {self.node} as {self.node.name}"

