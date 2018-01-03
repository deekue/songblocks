#!/usr/bin/env python

import ConfigParser
import logging
import logging.config
import nfc
import soco
import time

class NFCPollForTagID(object):
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
        logging.info("no tag detected")
        if self.poll_last_tag is not None:
          logging.info("  tag %s was present last time" % self.poll_last_tag)
          self.poll_last_tag = None
          if tagRemoved is not None:
            tagRemoved()
      else:
        logging.info("tag detected: %s" % tag)
        if tag == self.poll_last_tag:
          logging.info("  same tag as last time")
        else:
          logging.info("  new tag")
          self.poll_last_tag = tag
          if tagPresent is not None:
            tagPresent(tag)
    
      time.sleep(self.poll_interval_secs)
 

class NFCSonosController(object):
  _player = None

  def __init__(self, configFile):
    self._configFile = configFile
    self.config = ConfigParser.SafeConfigParser()
    self.config.read(configFile)

  def connect(self, player_name=None):
    if player_name is None:
      player_name = self.config.get("Config", "player_name")
    self.player_name = player_name
    self._player = soco.discovery.by_name(player_name)
    return self._player

  def sonosPlayUri(self, uri):
    logging.info("  playing URI %s" % uri)
    try:
      self._player.clear_queue()
      self._player.add_uri_to_queue(uri)
      self._player.play_from_queue(index=0)
    except soco.SoCoException, e:
      logging.exception(e)

  def sonosStop(self):
    logging.info("stop playing")
    try:
      self._player.stop()
    except soco.SoCoException, e:
      logging.exception(e)

  def action_sonos_uri(self, tagConfig):
    if tagConfig.has_key(tagConfig['uri']):
      logging.info("  playing %s" % tagConfig['name'])
      self.sonosPlayUri(tagConfig['uri'])

  def action_sonos_playlist(self, tagConfig):
    logging.info("  playing playlist '%s'" % tagConfig['playlist'])
    try:
      playlist = self._player.get_sonos_playlist_by_attr('title', tagConfig['playlist'])
      self.sonosPlayUri(playlist.get_uri())
    except ValueError:
      logging.info("  Sonos playlist %s not found" % tagConfig['playlist'])

  def tagPresent(self, tag):
    logging.info("play song for tag %s" % tag)
    tagSection = "tag-%s" % tag
    if self.config.has_section(tagSection):
      tagConfig = dict(self.config.items(tagSection))
      actionName = 'action_%s' % tagConfig['action'].lower().replace(' ', '_')
      action = getattr(self, actionName, None)
      if action is not None:
        action(tagConfig)
      else:
        logging.warning("  unknown action %s for [%s] in %s" % (actionName, tagSection, self._configFile))
    else:
      logging.warning("  [%s] not found in %s" % (tagSection, self._configFile))

  def tagRemoved(self):
    self.sonosStop()

  def run(self, device_path=None):
    if device_path is None:
      device_path = self.config.get("Config", "nfc_device_path")
    poller = NFCPollForTagID(device_path)
    poller.run(tagPresent=self.tagPresent, tagRemoved=self.tagRemoved)


# main
if __name__ == "__main__":
  logging.config.fileConfig('songblocks.ini')

  controller = NFCSonosController(configFile='songblocks.ini')
  if controller.connect() is not None:
    controller.run()
  else:
    logging.error("Sonos player %s not found" % controller.player_name)

