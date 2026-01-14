import re
from freeplane import Node
import threading
from functools import wraps

from fp_convert.colors import Color
from fp_convert.errors import MaximumSectionDepthException

# from peek import peek


_local = threading.local()

def if_processed_already(node: Node):
    processed_nodes = _get_local_processed_nodes()
    return node.id in processed_nodes

def mark_as_processed(node: Node):
    processed_nodes = _get_local_processed_nodes()
    processed_nodes.add(node.id)

def _get_local_processed_nodes():
    try:
        return _local.processed_nodes
    except AttributeError:
        _local.processed_nodes = set()
        return _local.processed_nodes

def _get_local_flagged_nodes():
    try:
        return _local.flagged_nodes
    except AttributeError:
        _local.flagged_nodes = set()
        return _local.flagged_nodes

def _get_local_color_register():
    try:
        return _local.color_register
    except AttributeError:
        _local.color_register = set()
        return _local.color_register


def register_color(method):
    """
    A decorator to inject the latex color command into the latex doc.

    The decorator will create a thread-local set of colors included into the
    document so far.

    Parameters
    ----------
    method : callable
        The method to be decorated. Should be an instance method of class of
        Doc from one of the supported templates - like psdoc.
        class that accepts a color-name string. The decorator injects the
        same into the instance of the FPDoc class. Then it invokes the called
        method and returns the result.
    """

    @wraps(method)
    def decorated(ctx, color: str, *args, **kwargs):
        registered_colors = _get_local_color_register()

        # Retrieve individual colors, if supplied color is a mixed one
        if "!" in color:
            mixed_colors = re.findall(r"([a-z]+[)'a-z0-9(/]+)", color)
        else:  # add supplied single color to this list
            mixed_colors = [color]

        for colr in mixed_colors:
            if colr not in registered_colors:
                c = Color(colr)
                color_name, color_model, color_specs = c.name, "rgb", c.rgbval

                ctx.colors.append((color_name, color_model, color_specs))
                registered_colors.add(color_name)
        return method(ctx, color, *args, **kwargs)

    return decorated


def track_processed_nodes(method):
    """
    A decorator that maintains a set of processed nodes across recursive calls.
    This decorator is specifically designed for methods that traverse node trees
    and need to track which nodes have been processed to avoid duplicates.

    The decorator will:
    1. Create a processed_nodes set as a thread-local variable if it doesn't
       exist
    2. Maintain the set's state throughout the recursion

    Parameters
    ----------
    method : callable
        The method to be decorated which should not be an instance method, by
        the way.
    """

    @wraps(method)
    def decorated(node, doc, *args, **kwargs):
        processed_nodes = _get_local_processed_nodes()
        if node.id in processed_nodes:
            return []
        processed_nodes.add(node.id)
        return method(node, doc, *args, **kwargs)

    return decorated

def track_flagged_nodes(method):
    """
    A decorator that maintains a set of flagged nodes across recursive calls.

    The decorator will:
    1. Create a flagged_nodes set as a thread-local variable if it doesn't
       exist
    2. Maintain the set's state throughout the recursion

    Parameters
    ----------
    method : callable
        The method to be decorated which should not be an instance method, by
        the way.
    """

    @wraps(method)
    def decorated(node, config, ctx, *args, **kwargs):
        flagged_nodes = _get_local_flagged_nodes()
        if node.id in flagged_nodes:
            return []
        flagged_nodes.add(node.id)
        return method(node, config, ctx, *args, **kwargs)

    return decorated

def limit_depth(method):
    """
    A decorator that limits the depth of sections to config.main.max_sec_depth.

    Parameters
    ----------
    method : callable
        The function to be decorated to ensure compliance to max-depth while
        building various sections of the document. Only build_*_block kind of
        builder functions are expected to be decorated by it.
    """

    @wraps(method)
    def decorated(node, doc, depth, builders, *args, **kwargs):
        if depth > doc.config.main.max_sec_depth:
            raise MaximumSectionDepthException(
                f"Maximum depth of {doc.config.main.max_sec_depth} has been "
                f"reached for node {str(node)}(id: {node.id})."
                )
        return method(node, doc, depth, builders, *args, **kwargs)
    return decorated
