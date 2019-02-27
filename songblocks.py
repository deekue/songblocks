#!/usr/bin/env python

import ConfigParser
import logging
import logging.config
import os
import sys
from optparse import OptionParser

# TODO add class/method docstrings

class SongblocksException(Exception):
  pass


class SongBlocks(object):

  def __init__(self, config, poller, player):
    self.config = config
    self.poller = poller
    self.player = player

  def tagPresent(self, tag):
    logging.debug("play song for tag %s" % tag)
    tagSection = "tag-%s" % tag
    if self.config.has_section(tagSection):
      tagConfig = dict(self.config.items(tagSection))
      actionName = 'action_%s' % tagConfig['action'].lower().replace(' ', '_')
      action = getattr(self.player, actionName, None)
      if action != None:
        action(tagConfig)
      else:
        logging.error("  unknown action %s for [%s] in config file" % (actionName, tagSection))
    else:
      logging.error("  [%s] not found in config file" % tagSection)

  def tagRemoved(self):
    self.player.stop()

  def run(self):
    self.poller.run(tagPresent=self.tagPresent, tagRemoved=self.tagRemoved)


def importPoller(poller_type, device_path):
  if poller_type == "Nfctag":
    from poller.nfctag import NFCPoller
    poller = NFCPoller(device_path)
    logging.debug("chose NFCPoller")
  elif poller_type == "Mock":
    from poller.mock import MockPoller
    poller = MockPoller(device_path)
    logging.debug("chose MockPoller")
  else:
    raise SongblocksException("Unknown poller_type %s" % poller_type)
  return poller

def importPlayer(player_type, player_name):
  if player_type == "Sonos":
    from player.sonos import SonosController
    player = SonosController(player_name)
  elif player_type == "Chromecast":
    from player.chromecast import ChromecastController
    player = ChromecastController(player_name)
  elif player_type == "Mock":
    from player.mock import MockController
    player = MockController(player_name)
    logging.debug("chose MockController")
  else:
    raise SongblocksException("Unknown player_type %s" % player_type)
  return player

def main(argv=None):
  parser = OptionParser()
  parser.add_option("-c", "--config", dest="config_file",
                    default=os.path.join(os.path.dirname(__file__),
		      "songblocks.ini"),
                    help="config file [%default]")

  (options, args) = parser.parse_args(args=argv)

  logging.config.fileConfig(options.config_file)

  config = ConfigParser.SafeConfigParser()
  config.read(options.config_file)
  poller_type = config.get("Config", "poller_type").lower().capitalize()
  device_path = config.get("Config", "poller_device_path")
  player_name = config.get("Config", "player_name")
  player_type = config.get("Config", "player_type").lower().capitalize()

  poller = importPoller(poller_type, device_path)
  player = importPlayer(player_type, player_name)

  controller = SongBlocks(config, poller, player)
  controller.run()

if __name__ == "__main__":
  sys.exit(main(sys.argv))
