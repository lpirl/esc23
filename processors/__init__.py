import abc
from pkgutil import walk_packages
from inspect import getmembers, isclass

class AbstractBaseProcessor(metaclass=abc.ABCMeta):
    """
    Base processor for all processors
    """

    __metaclass__ = abc.ABCMeta

    order = 1000
    """
    Order when this processor should be executed.

    Lower numbers are executed earlier.
    """

    def __init__(self):

        self.post_init()
        """hook for subclasses"""


    def post_init(self):
        """
        Hook for subclasses.

        So that they do not need to override __init__.
        """
        pass


    def add_cli_args(self, parser):
        """
        Adds this class' arguments to the parser .
        """
        pass


    def read_cli_args(self, args):
        """
        Reads arguments of interest specified using the CLI.
        """
        pass

    @staticmethod
    def get_and_increment_id_counter(tree):
        """
        Reads and returns the id counter from the session (``tree``)
        ans saves the id counter incremented by one.
        """
        session_element = tree.getroot()
        next_id = int(session_element.get("id-counter"))
        session_element.set("id-counter", str(next_id+1))
        return next_id

    @abc.abstractmethod
    def process(self, a2_tree, a3_tree):
        """
        Modifies the ``a3_tree`` with possibly additional information
        from ``a2_tree``.
        """
        pass

"""
Import all processors dynamically
"""
for module_loader, module_name, _ in walk_packages(__path__):
    module = module_loader.find_module(module_name).load_module(module_name)
    for cls_name, cls in getmembers(module):
        if not isclass(cls):
            continue
        if not issubclass(cls, AbstractBaseProcessor):
            continue
        if cls_name.startswith("Abstract"):
            continue
        exec('from %s import %s' % (module_name, cls_name))
