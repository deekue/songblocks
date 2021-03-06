#!/usr/bin/env python
#
#

import logging

import abc

logging.getLogger(__name__).addHandler(logging.NullHandler())

class MockController(abc.PlayerBase):

    def __init__(self, player_name):
        pass

    def action_sonos_uri(self, tagConfig):
        logging.debug("action_sonos_uri called with %s" % tagConfig)

    def action_sonos_playlist(self, tagConfig):
        logging.debug("action_sonos_playlist called with %s" % tagConfig)

    def action_chromecast_uri(self, tagConfig):
        logging.debug("action_chromecast_uri called with %s" % tagConfig)

    def stop(self):
        logging.debug("stop")
