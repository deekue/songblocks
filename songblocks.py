#!/usr/bin/env python

import ConfigParser
import logging
import logging.config
import os
import time
import sys
from optparse import OptionParser

# TODO add class/method docstrings

class SongblocksException(Exception):
  pass


class Poller(object):
  """ABC for a polling device to provide 'tag' UUIDs."""

  def __init__(self, device_path):
      pass

  def run(self, tagPresent=None, tagRemoved=None):
      pass


class NFCPoller(Poller):
  poll_last_tag = None

  def __init__(self, device_path, poll_interval_secs=0.5):
    self.poll_interval_secs = poll_interval_secs
    self.device_path = device_path

  def poll_for_tag(self):
    """Poll device at device_path for a tag, return the UID if found, None if not. """
    with nfc.clf.ContactlessFrontend(self.device_path) as clf:
        target = clf.sense(nfc.clf.RemoteTarget("106A"))
        if target is not None:
            tag = nfc.tag.activate(clf, target)
            return str(tag.identifier).encode('hex')
        else:
            return None

  def run(self, tagPresent=None, tagRemoved=None):
    while True:
      tag = self.poll_for_tag()
      if tag is None:
        logging.debug("no tag detected")
        if self.poll_last_tag is not None:
          logging.debug("  tag %s was present last time" % self.poll_last_tag)
          self.poll_last_tag = None
          if tagRemoved is not None:
            tagRemoved()
      else:
        logging.debug("tag detected: %s" % tag)
        if tag == self.poll_last_tag:
          logging.debug("  same tag as last time")
        else:
          logging.debug("  new tag")
          self.poll_last_tag = tag
          if tagPresent is not None:
            tagPresent(tag)
    
      time.sleep(self.poll_interval_secs)


class MockNFCPoller(NFCPoller):
  def poll_for_tag(self):
    # TODO add a way to trigger mock tags
    return '2b1f76dd'


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
      if action is not None:
        action(tagConfig)
      else:
        logging.error("  unknown action %s for [%s] in config file" % (actionName, tagSection))
    else:
      logging.error("  [%s] not found in config file" % tagSection)

  def tagRemoved(self):
    self.player.stop()

  def run(self):
    self.poller.run(tagPresent=self.tagPresent, tagRemoved=self.tagRemoved)


def importPlayer(player_type, player_name):
  try:
    if player_type == "Sonos":
      from player.sonos import SonosController
      player = SonosController(player_name)
    elif player_type == "Chromecast":
      from player.chromecast import ChromecastController
      player = ChromecastController(player_name)
    else:
      raise SongblocksException("Unknown player_type %s" % player_type)
  except ImportError:
    from player.mock import MockController
    player = MockController(player_name)
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
  device_path = config.get("Config", "nfc_device_path")
  player_name = config.get("Config", "player_name")
  player_type = config.get("Config", "player_type").lower().capitalize()

  try:
    import nfc
    poller = NFCPoller(device_path)
  except ImportError:
    poller = MockNFCPoller(device_path)
  
  player = importPlayer(player_type, player_name)

  controller = SongBlocks(config, poller, player)
  controller.run()

if __name__ == "__main__":
  sys.exit(main())
