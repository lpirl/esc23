#!/usr/bin/python3

from sys import argv
import argparse
import logging
from xml.etree.ElementTree import ElementTree
from os.path import isfile, splitext
from datetime import datetime
from shutil import copy

from lib import Esc23

if __name__ != '__main__':
    raise NotImplementedError(
        "This is module should only be called directly from command line."
    )

parser = argparse.ArgumentParser(
    description="Extends Ardour3 sessions converted from Ardour2.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument('-d', '--debug', action='store_true', default=False,
                    help='Turn on debug messages?')

# sadly, argparse does not allow us to suppress the "(default …)"
# message easily, so here is a workaround:
BACKUP_FILE_DEFAULT = "$(basename a3_file .ardour)_pre-esc23_<timestamp>.ardour"
parser.add_argument('-b', type=str, dest="backup_file",
                    default=BACKUP_FILE_DEFAULT,
                    help='File to backup the Ardour3 session to ')

parser.add_argument('a3_file', type=str,
                    help='The Ardour3 session file to extend')

A2_FILE_DEFAULT = ("default Ardour3 created backup file from Ardour2 session"
    " (the '-2000'-file)")
parser.add_argument('a2_file', type=str, nargs='?',
                    default=A2_FILE_DEFAULT,
                    help='The Ardour2 session file to read from')

# set up logger
logging.getLogger().name = "esc23"
if '-d' in argv:
	logging.getLogger().setLevel(logging.DEBUG)

esc23 = Esc23()
esc23.add_cli_args(parser)
args = parser.parse_args()
esc23.read_cli_args(args)

# arg sanitize: Ardour3 session file
if not isfile(args.a3_file):
    print("'%s' seems to be not a file" % args.a3_file)
    exit(1)

# arg sanitize: Ardour2 session file
if args.a2_file == A2_FILE_DEFAULT:
    in_a3_path, in_a3_ext = splitext(args.a3_file)
    args.a2_file = "%s-2000%s" % (
        in_a3_path, in_a3_ext)

    if not isfile(args.a2_file):
        print("Cannot autodetect Ardour2 session file, "
                "(tried '%s') please specify it manually." % args.a2_file)
        exit(1)

# arg sanitize: backup file
if args.backup_file == BACKUP_FILE_DEFAULT:
    in_a3_path, in_a3_ext = splitext(args.a3_file)
    args.backup_file = "%s_pre-esc23_%s%s" % (
        in_a3_path, datetime.now().isoformat(), in_a3_ext)

# load existing sessions
logging.debug("loading from '%s'" % args.a2_file)
a2_tree = ElementTree(file=args.a2_file)
logging.debug("loading from '%s'" % args.a3_file)
a3_tree = ElementTree(file=args.a3_file)

# backup
print("backed up to '%s'" % args.backup_file)
copy(args.a3_file, args.backup_file)

esc23.process(a2_tree, a3_tree)

# write new session
logging.debug("writing to '%s'" % args.a3_file)
a3_tree.write(args.a3_file, encoding="UTF-8", xml_declaration=True)
