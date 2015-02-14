import logging
from sys import argv
from copy import deepcopy
from os.path import join as path_join, dirname
from xml.etree.ElementTree import ElementTree

from processors import AbstractBaseProcessor

BASEDIR = dirname(argv[0]) or '.'

class EditGroupsToGroups(AbstractBaseProcessor):

    order = 1000

    GROUP_TEMPLATE_FILE = path_join(BASEDIR,
        "processors/static/group.xmlpart")

    def post_init(self):
        self.group_template = ElementTree(
            file=self.GROUP_TEMPLATE_FILE
        )
        self.enabled = True

    def add_cli_args(self, parser):
        parser.add_argument('--no-groups', action='store_true',
                            default=False,
                            help='Do not translate edit groups to groups')

    def read_cli_args(self, args):
        self.enabled = args.no_playlists

    def get_group(self, xml_id, name):
        group = deepcopy(self.group_template).getroot()
        group.set("name", name)
        group.set("id", str(xml_id))
        return group

    def process(self, a2_tree, a3_tree):

        ROUTES_LOOKUP = ".//Route[@edit-group='%s']"
        edit_groups = {g : a2_tree.findall(ROUTES_LOOKUP % g.get("name"))
            for g in a2_tree.iterfind(".//EditGroups/RouteGroup")}

        new_groups_element = a3_tree.find("RouteGroups")

        new_group_id = int(a3_tree.getroot().get("id-counter"))

        for old_group, old_routes in edit_groups.items():

            group_name = old_group.get("name")

            # create the new RouteGroup
            new_group = self.get_group(
                new_group_id,
                group_name
            )

            if new_groups_element.find("RouteGroup[@name='%s']" % group_name) is not None:
                logging.debug(
                    "group '%s' already exists - skipping" % group_name
                )
                continue
            new_groups_element.append(new_group)

            # get all new route IDs, wire routes to group
            # (uses diskstream IDs to translate from A2 to A3)
            new_route_ids = list()
            for old_route in old_routes:

                # lookup diskstram IDs of old routes
                diskstream_id = old_route.get("diskstream-id")
                if diskstream_id is None:
                    logging.debug(
                        "old route %i not assigned to a " % playlist_id +
                        "Diskstream - skipping"
                    )
                    continue
                diskstream_id = int(diskstream_id)

                # get A3 route with help of A2 diskstream ID
                new_route = a3_tree.find(".//Diskstream[@id='%u'].." % diskstream_id)
                if not new_route.tag == "Route":
                    logging.debug(
                        "expected to find a Route "
                        "but found a %s - skipping" % new_route.tag
                    )
                    continue

                # check if route not wired yet
                if new_route.get("route-group") is not None:
                    logging.debug(
                        "new route '%s' " % new_route.get("name") +
                        "already assigned to a group - skipping"
                    )
                    continue

                new_route_ids.append(int(new_route.get("id")))

                # wire RouteGroup <- Route
                logging.debug("wiring Route '%s' -> Group '%s'" % (
                    new_route.get("name"), group_name
                ))

                new_route.set("route-group", group_name)

            # wire RouteGroup -> Routes
            new_route_ids_as_strings = [str(i) for i in new_route_ids]
            logging.debug("reverse-wiring Group '%s' (%i -> Routes %s)" % (
                group_name, new_group_id, ', '.join(new_route_ids_as_strings)
            ))
            new_group.set("routes", ' '.join(new_route_ids_as_strings))

            new_group_id += 1

        a3_tree.getroot().set("id-counter", str(new_group_id))
