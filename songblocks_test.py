#!/usr/bin/python
#
#

import ConfigParser
import logging
import logging.config
import os
import sys
from optparse import OptionParser

import songblocks


class MockNFCPoller(songblocks.NFCPoller):
  def poll_for_tag(self):
    # TODO add a way to trigger mock tags
    return '2b1f76dd'


class MockChromecastController(songblocks.ChromecastController):
    def __init__(self, cast_name):
        self.cast_name = cast_name

    def playUri(self, uri, content_type):
        logging.debug("play URI %s" % uri)

    def stop(self):
        logging.debug("stop playing")


class MockSonosController(songblocks.SonosController):
    def __init__(self, player_name):
        self.player_name = player_name

    def playUri(self, uri, actionConfig):
        logging.debug("play URI %s" % uri)

    def stop(self):
        logging.debug("stop playing")



if __name__ == "__main__":

  parser = OptionParser()
  parser.add_option("-c", "--config", dest="config_file",
                    default=os.path.join(os.path.dirname(__file__),
                      "songblocks.ini"),
                    help="config file [%default]")

  (options, args) = parser.parse_args(args=sys.argv)
  logging.config.fileConfig(options.config_file)
  config = ConfigParser.SafeConfigParser()
  config.read(options.config_file)
  device_path = config.get("Config", "nfc_device_path")
  player_name = config.get("Config", "player_name")
  player_type = config.get("Config", "player_type").lower().capitalize()

  poller = MockNFCPoller(device_path)
  if player_type == "Sonos":
    player = MockSonosController(player_name)
  elif player_type == "Chromecast":
    player = MockChromecastController(player_name)
  else:
    raise SongblocksException("Unknown player_type %s" % player_type)

  controller = songblocks.SongBlocks(config, poller, player)
  controller.run()

