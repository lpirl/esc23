#!/usr/bin/python3

from sys import argv
import argparse
import logging
from inspect import getmembers, isclass
from xml.etree.ElementTree import ElementTree
from os import chdir
from os.path import isfile, dirname

import processors as processors_module

if __name__ != '__main__':
    raise NotImplementedError(
        "This is module should only be called directly from command line."
    )

def get_processors():
    """
    Acquires all processors (classes) in the module 'processors'.
    """
    processors = [	t[1] for t in
                    getmembers(processors_module, isclass)
                        if not t[0].startswith("Abstract") ]
    logging.debug("found processors: %s" % str([s.__name__ for s in processors]))
    return processors

def get_processors_sorted():
    """
    Sames as get_processors but processors are sorted,
    starting with most important.
    """
    processors = get_processors()
    processors.sort(key=lambda processor: processor.order)
    logging.debug("sorted processors: %s" % str([s.__name__ for s in processors]))
    return processors

parser = argparse.ArgumentParser(
	description="Extends Ardour3 sessions converted from Ardour2.",
	formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument('-f', '--force', action='store_true', default=False,
                    help='Will overwrite the output file')
parser.add_argument('-d', '--debug', action='store_true', default=False,
                    help='Turn on debug messages?')
parser.add_argument('in_file', type=str,
                    help='The Ardour3 session file to read from')
parser.add_argument('out_file', type=str,
                    help='The Ardour3 session file to write to')

chdir(dirname(argv[0]) or '.')

# set up logger
logging.getLogger().name = "asc23"
if '-d' in argv:
	logging.getLogger().setLevel(logging.DEBUG)

# initialize processors
processors = [P() for P in get_processors_sorted()]
for processor in processors:
    processor.add_args(parser)
args = parser.parse_args()
for processor in processors:
    processor.read_args(args)

# arguments sanity checks
if isfile(args.out_file) and not args.force:
    print("Output session file already exists - will not overwrite.")
    exit(1)

# load old session
logging.debug("loading from '%s'" % args.in_file)
session = ElementTree(file=args.in_file)

# process
for processor in processors:
    logging.debug("running processor: %s" % processor.__class__.__name__)
    processor.process(session)

# write new session
logging.debug("writing to '%s'" % args.out_file)
session.write(args.out_file, encoding="UTF-8", xml_declaration=True)
