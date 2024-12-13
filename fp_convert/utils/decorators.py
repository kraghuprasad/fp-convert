import threading
from functools import wraps

_local = threading.local()


def _get_local_processed_nodes():
    try:
        return _local.processed_nodes
    except AttributeError:
        _local.processed_nodes = set()
        return _local.processed_nodes


def track_processed_nodes(method):
    """
    A decorator that maintains a set of processed nodes across recursive calls.
    This decorator is specifically designed for methods that traverse node trees
    and need to track which nodes have been processed to avoid duplicates.

    The decorator will:
    1. Create a processed_nodes set as a thread-local variable if it doesn't exist
    2. Maintain the set's state throughout the recursion

    Parameters
    ----------
    method : callable
        The method to be decorated. Should be an instance method that processes nodes.
    """

    @wraps(method)
    def decorated(self, node, *args, **kwargs):
        processed_nodes = _get_local_processed_nodes()
        if node.id in processed_nodes:
            return None
        processed_nodes.add(node.id)
        return method(self, node, *args, **kwargs)

    return decorated
