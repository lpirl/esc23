from processors import AbstractBaseProcessor

import logging
from xml.etree.ElementTree import ElementTree

class AddMonitorBus(AbstractBaseProcessor):

    order = 1000
    MONITOR_BUS_FILE = "processors/static/monitor_bus.xmlpart"

    def post_init(self):
        self.monitor_bus = ElementTree(file=self.MONITOR_BUS_FILE)
        self.enabled = True

    def add_args(self, parser):
        parser.add_argument('-m', '--no-monitor', action='store_true', default=False,
                            help='Do NOT insert the Ardour3-style monitor bus')

    def read_args(self, args):
        self.enabled = args.no_monitor

    def process(self, tree):
        if tree.findall(".//Route[@name='monitor']"):
            logging.debug("monitor bus already exists")
            return
        routes = tree.find("Routes")
        routes.append(self.monitor_bus.getroot())
