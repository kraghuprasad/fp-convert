"""
Common classes used in documenting Software Development specifications.
"""
import re
from typing import List
from freeplane import Node

from ..utils.helpers import (
    is_ignore_type,
    get_fpc_block_type,
    get_fpc_data_type,
    get_fpc_visibility,
    get_fpc_message,
)
from ..errors import InvalidNodeException

class Attribute:
    def __init__(
        self, name:str, data_type:str, description:str,
        visibility:str='public', node: Node = None
    ):
        self.name:str = name
        self.data_type:str = data_type
        self.visibility:str = visibility
        self.description:str = description
        self.node = node
    
    def __str__(self):
        return f'{self.name}: {self.data_type}'

class Argument:
    def __init__(
        self, name:str, data_type:str, description:str,
        node: Node = None
    ):
        self.name:str = name
        self.data_type:str = data_type
        self.description:str = description
        self.node = node

        # Hold nodes containing options for Argument
        self.options = list()
        for child in node.children:
            self.options.append(child)

    def __str__(self):
        return f'{self.name}'

class Exc:
    def __init__(
        self, name:str, status:str, message:str="",description:str="",
        node: Node = None
    ):
        self.name = name
        self.status = status
        self.message = message
        self.description = description
        self.node = node

    def __str__(self):
        return f'{self.name}({self.status})'

class Returns:
    def __init__(
        self, data_type:str, description:str="",
        notes:str="", node: Node = None
    ):
        self.data_type: str = data_type
        self.description: str = description
        self.notes: str = notes
        self.node: Node = node

        # Hold nodes containing options for Return
        self.options: List[Node] = list()
        for child in node.children:
            self.options.append(child)

    def __str__(self):
        return f'{self.data_type}'

class Function:
    def __init__(
        self, name:str, visibility:str='public', description:str='',
        arguments:List[Argument]=[],
        exceptions: List[Exc]=[],
        returns:Returns=None, node: Node=None
    ):
        self.name = name
        self.visibility:str = visibility
        self.description:str = description
        self.arguments:List[Argument] = arguments
        self.returns:Returns = returns
        self.exceptions:List[Exc] = exceptions
        self.node = node
    
    def __str__(self):
        return f'{self.name}({', '.join([str(arg) for arg in self.arguments])})'

class Klass:
    def __init__(  # All arguments are mandatory
        self, name:str, visibility:str, description:str,  # Node-text
        attributes: List[Attribute],  # Individual attributes
        attributes_node: Node,  # Contains node holding all attributes
        attributes_description: str,  # Notes of the attributes-container node
        functions: List[Function],  # Individual functions
        functions_node: Node,  # Contains node holding all functions
        functions_description: str,  # Notes of the functions-container node
        node: Node = None
    ):
        self.name:str = name
        self.visibility:str = visibility
        self.description:str = description
        self.attributes:List[Attribute] = attributes
        self.attributes_node: Node = attributes_node
        self.attributes_description = attributes_description
        self.functions:List[Function] = functions
        self.functions_node: Node = functions_node
        self.functions_description = functions_description
        self.node = node
    
    def __str__(self):
        return f'{self.name}'

    def add_attribute(self, attribute:Attribute):
        self.attributes.append(attribute)

    def add_function(self, function:Function):
        self.functions.append(function)

    def add_exception(self, exception:Exc):
        self.exceptions.append(exception)

def build_klass(node: Node) -> Klass:
    """Builds a Klass object from a freeplane node."""
    # Collect details to build Klass object
    name = str(node)
    visibility = get_fpc_visibility(node, 'public')  # Public by default
    description = str(node.notes)
    # description = ""
    # if node.notes:
    #     description = str(node.notes)

    attributes = list()
    attributes_node = None
    functions = list()
    functions_node = None

    for child in node.children:
        if is_ignore_type(child):
            continue

        attributes_node_count = 0
        functions_node_count = 0

        block_type = get_fpc_block_type(child, "")
        if block_type in {'attributes', 'constants'}:  # It is attributes-container
            if attributes_node_count > 1:
                raise InvalidNodeException(
                    'More than one nodes of type "Attributes" were found '
                    f'under the node "{node} (ID: {node.id})" which is of '
                    'Class-type. Only one node of type "Attributes" is '
                    'allowed under a Class-type node.'
                )
            else:
                attributes_node_count += 1

            attributes_node = child
            attributes_description = str(child.notes)
            # if child.notes:
            #     attributes_description = str(child.notes)
            # else:
            #     attributes_description = ""

            for attr_node in child.children:
                if is_ignore_type(attr_node):
                    continue

                attr_node_type = get_fpc_block_type(attr_node, "")
                if attr_node_type != 'attribute':
                    raise InvalidNodeException(
                        f'Invalid block-type "{attr_node_type}" found for node '
                        f'"{str(attr_node)}(ID: {str(attr_node.id)})" which is a '
                        'child of Attributes-type node '
                        f'"{attr_node.parent}(ID: {str(attr_node.parent.id)})". '
                        'Only Attribute-type nodes are allowed under it.'
                    )
                if attr_node.children:
                    raise InvalidNodeException(
                        'One or more invalid child-nodes found under node '
                        f'"{str(attr_node)}(ID: {attr_node.id})". No child-nodes '
                        'are allowed under node of type "Attribute".'
                    )
                attributes.append(build_attribute(attr_node))

        elif block_type == 'functions':  # It is functions-container
            if functions_node_count > 1:
                raise InvalidNodeException(
                    'More than one nodes of type "Functions" were found '
                    f'under the node "{node} (ID: {node.id})" which is of '
                    'Class-type. Only one node of type "Functions" is '
                    'allowed under a Class-type node.'
                )
            else:
                functions_node_count += 1

            functions_node = child
            functions_description = str(child.notes)
            # if child.notes:
            #     functions_description = str(child.notes)
            # else:
            #     functions_description = ""

            for func_node in child.children:
                if is_ignore_type(func_node):
                    continue

                func_node_type = get_fpc_block_type(func_node, "")
                if func_node_type != 'function':
                    raise InvalidNodeException(
                        f'Invalid block-type "{func_node_type}" found for node '
                        f'"{str(func_node)}(ID: {str(func_node.id)})" which is a '
                        'child of Functions-type node '
                        f'"{func_node.parent}(ID: {str(func_node.parent.id)})". '
                        'Only Function-type nodes are allowed under it.'
                    )
                functions.append(build_function(func_node))
        else:
            raise InvalidNodeException(
                f'Invalid block-type "{block_type}" found for node '
                f'"{str(child)}(ID: {str(child.id)})" which is a child of '
                f'a Class-type node "{child.parent}(ID: {str(child.parent.id)})". '
                'Only "Attributes" and "Functions" blocks are allowed under it.'
            )
    return Klass(
        name=name,
        visibility=visibility,
        description=description,
        attributes=attributes,
        attributes_node = attributes_node,
        attributes_description=attributes_description,
        functions=functions,
        functions_node = functions_node,
        functions_description=functions_description,
        node=node
    )

def build_function(node: Node) -> Function:
    """Builds a Function object from a freeplane node."""
    name = str(node)
    visibility = get_fpc_visibility(node, 'public')

    description = ""
    if node.notes:
        description = str(node.notes)

    arguments = []
    exceptions = []
    returns = None

    for child in node.children:
        if is_ignore_type(child):
            continue
        block_type = get_fpc_block_type(child, "")
        if block_type == 'arguments':
            for arg_node in child.children:
                arg_node_type = get_fpc_block_type(arg_node, "")
                if not arg_node_type == 'argument':
                    raise InvalidNodeException(
                        f'Invalid block-type "{arg_node_type}" found for node '
                        f'"{str(arg_node)}(ID: {str(arg_node.id)})" which is a '
                        'child of Exceptions-type node '
                        f'"{arg_node.parent}({str(arg_node.parent.id)})". '
                        'Only Argument-type nodes are allowed under it.'
                    )
                # if arg_node.children:
                #     raise InvalidNodeException(
                #         'One or more invalid child-nodes found under node '
                #         f'"{str(arg_node)}(ID: {arg_node.id})". No child-nodes '
                #         'are allowed under node of type "Argument".'
                #     )
                arguments.append(build_argument(arg_node))

        elif block_type == 'exceptions':
             for exc_node in child.children:
                exc_node_type = get_fpc_block_type(exc_node, "")
                if not exc_node_type == 'exception':
                    raise InvalidNodeException(
                        f'Invalid block-type "{exc_node_type}" found for node '
                        f'"{str(exc_node)}(ID: {str(exc_node.id)})" which is a '
                        'child of Exceptions-type node '
                        f'"{exc_node.parent}({str(exc_node.parent.id)})". '
                        'Only Exception-type nodes are allowed under it.'
                    )
                if exc_node.children:
                    raise InvalidNodeException(
                        'One or more invalid child-nodes found under node '
                        f'"{str(exc_node)}(ID: {exc_node.id})". No child-nodes '
                        'are allowed under node of type "Exception".'
                    )
                exceptions.append(build_exception(exc_node))
        elif block_type == 'returns':
            returns = build_returns(child)
        else:
            raise InvalidNodeException(
                f'Invalid block-type "{block_type}" found for node '
                f'"{str(child)}(ID: {str(child.id)})" which is a child of '
                f'a Function-type node "{child.parent}({str(child.parent.id)})". '
                'Only "Arguments" and "Exceptions" blocks are allowed under it.'
            )

    return Function(
        name=name,
        visibility=visibility,
        description=description,
        arguments=arguments,
        returns=returns,
        exceptions=exceptions,
        node=node
    )

def build_attribute(node: Node) -> Attribute:
    """Builds an Attribute object from a freeplane node."""
    name = str(node)
    data_type = get_fpc_data_type(node, '')
    visibility = get_fpc_visibility(node, 'public')
    description = str(node.notes)

    # if node.notes:
    #     description = str(node.notes)
    # else:
    #     description = ""

    return Attribute(
        name=name,
        data_type=data_type,
        visibility=visibility,
        description=description,
        node=node
    )

def build_argument(node: Node) -> Argument:
    """Builds an Argument object from a freeplane node."""
    name = str(node)
    data_type = node.attributes.get('fpcDataType', '')

    description = ""
    if node.notes:
        description = str(node.notes)

    return Argument(
        name=name,
        data_type=data_type,
        description=description,
        node=node
    )

def build_exception(node: Node) -> Exception:
    """Builds an Exception object from a freeplane node."""
    match = re.match(r"(.+?)\s*\((\d+)\)", str(node))
    if not match:
        # Or raise an error, for now just use the whole text as name
        name = str(node)
        status = ""
    else:
        name = match.group(1)
        status = match.group(2)

    message = get_fpc_message(node, "")

    if node.notes:
        description = str(node.notes)
    else:
        description = ""

    return Exc(
        name=name, status=status, message=message,
        description=description, node=node
    )

def build_returns(node: Node) -> Returns:
    """Builds a Returns object from a freeplane node."""
    description = str(node.notes)
    notes=""
    if node.notes:
        notes = node.notes

    if data_type := get_fpc_data_type(node, ''):
        return Returns(
            data_type=data_type, description=description,
            notes=notes, node=node
        ) 

    return Returns(
        data_type=None, description=description,
        notes=notes, node=node
    ) 