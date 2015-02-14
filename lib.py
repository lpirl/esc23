import logging
from copy import deepcopy
from inspect import getmembers, isclass

import processors as processors_module

class Esc23(object):

    def __init__(self):
        self.load_processors()

    def load_processors(self):
        """
        Acquires all processors (classes) in the module 'processors',
        sorts and stores.
        """
        processor_classes = [t[1] for t in
                            getmembers(processors_module, isclass)
                            if not t[0].startswith("Abstract") ]
        processor_classes.sort(key=lambda processor: processor.order)
        logging.debug("found and sorted processors: %s" % str(
            [s.__name__ for s in processor_classes]
        ))
        self.processors = [P() for P in processor_classes]

    def add_cli_args(self, parser):
        """
        Adds processors' command line arguments to the specified parser.
        """
        logging.debug("processors add CLI arguments")
        for processor in self.processors:
            processor.add_cli_args(parser)

    def read_cli_args(self, args):
        """
        Lets all processors read the command line arguments.
        """
        logging.debug("processors read CLI arguments")
        for processor in self.processors:
            processor.read_cli_args(args)

    def process(self, a2_tree, a3_tree):
        """
        Modifies the ``a3_tree`` and provides the ``a2_tree`` as
        an information resource to the processors.
        """
        for processor in self.processors:
            logging.debug("running processor: %s" % processor.__class__.__name__)
            processor.process(a2_tree, a3_tree)
