from sys import argv
from os.path import join as path_join, dirname
import logging
from xml.etree.ElementTree import ElementTree

from processors import AbstractBaseProcessor

BASEDIR = dirname(argv[0]) or '.'

class AddMonitorBus(AbstractBaseProcessor):

    order = 1000
    MONITOR_BUS_FILE = path_join(BASEDIR,
        "processors/static/monitor_bus.xmlpart")

    def post_init(self):
        self.monitor_bus = ElementTree(file=self.MONITOR_BUS_FILE)
        self.enabled = True

    def add_cli_args(self, parser):
        parser.add_argument('--no-monitor', action='store_true', default=False,
                            help='Do not insert the Ardour3-style monitor bus')

    def read_cli_args(self, args):
        self.enabled = args.no_monitor

    def process(self, tree):
        if tree.findall(".//Route[@name='monitor']"):
            logging.debug("monitor bus already exists - skipping")
            return
        routes = tree.find("Routes")
        logging.debug("adding monitor bus")
        routes.append(self.monitor_bus.getroot())
