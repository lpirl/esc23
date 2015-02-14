import logging

from processors import AbstractBaseProcessor

class ReassignPlaylistsToTracks(AbstractBaseProcessor):

    order = 1000

    def post_init(self):
        self.enabled = True

    def add_cli_args(self, parser):
        parser.add_argument('--no-playlist-reassign', action='store_true',
                            default=False,
                            help='Do not attempt to re-assign playlists to tracks')

    def read_cli_args(self, args):
        self.enabled = args.no_playlist_reassign

    def process(self, tree):
        for playlist in tree.iterfind(".//Playlist"):
            playlist_id = int(playlist.get("id"))

            diskstream_id = playlist.get("orig-track-id")
            if diskstream_id is None:
                logging.debug(
                    "playlist %i not assigned to a Diskstream" % playlist_id +
                    " - skipping"
                )
                continue
            diskstream_id = int(diskstream_id)

            if tree.find(".//Route[@id='%i']" % diskstream_id) is not None:
                logging.debug(
                    "playlist %i already assigned to a route" % playlist_id +
                    " - skipping"
                )
                continue

            if tree.find(".//Diskstream[@id='%u']" % diskstream_id) is None:
                logging.debug(
                    "cannot find Diskstream %i" % diskstream_id
                )
                continue

            route = tree.find(".//Diskstream[@id='%u'].." % diskstream_id)
            if not route.tag == "Route":
                logging.debug(
                    "expected to find a Route but found a %s" % route.tag +
                    " - skipping"
                )
                continue

            route_name = route.get("name")
            route_id = int(route.get("id"))

            logging.debug(
                "assigning playlist '%s' to route '%s'" % (
                    playlist.get("name"),
                    route.get("name")
                )
            )
            playlist.set("orig-track-id", str(route_id))
