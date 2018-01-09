#!/usr/bin/env python

import ConfigParser
import logging
import logging.config
import time

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


class MockNFCPoller(NFCPoller):
  def poll_for_tag(self):
    # TODO add a way to trigger mock tags
    return '2b1f76dd'


class PlayerController(object):

  def action_foobar(self, actionConfig):
      pass

  def stop(self):
      pass


class ChromecastController(PlayerController):
  _cast = None

  def __init__(self, cast_name):
    self.cast_name = cast_name
    logging.info("searching for local Chromecast devices...")
    chromecasts = pychromecast.get_chromecasts()
    logging.info("found %s" % chromecasts)
    self._cast = next(cc for cc in chromecasts if cc.device.friendly_name == cast_name)
    if self._cast is None:
      raise SongblocksException("Chromecast %s not found" % cast_name)
    self._mc = self._cast.media_controller

  def playUri(self, uri, content_type):
    self._mc.play_media(uri, content_type)

  def action_chromecast_uri(self, actionConfig):
    if actionConfig.has_key('uri'):
      logging.info("  playing %s" % actionConfig.get('name', actionConfig['uri']))
      content_type = actionConfig.get('content_type', 'audio/mp3')
      self.playUri(actionConfig['uri'], content_type)
    else:
      logging.error("  uri not defined")
      pass

  def stop(self):
    self._mc.stop()


class MockChromecastController(ChromecastController):
    def __init__(self, cast_name):
        self.cast_name = cast_name

    def playUri(self, uri, content_type):
        logging.debug("play URI %s" % uri)

    def stop(self):
        logging.debug("stop playing")


class SonosController(PlayerController):
  _player = None

  def __init__(self, player_name):
    self.player_name = player_name
    logging.info("Searching for Sonos device, %s" % player_name)
    self._player = soco.discovery.by_name(player_name)
    if self._player is None:
      raise SongblocksException('Sonos player "%s" not found' % player_name)

  def playUri(self, uri):
    logging.info("  playing URI %s" % uri)
    try:
      self._player.clear_queue()
      self._player.add_uri_to_queue(uri)
      self._player.play_from_queue(index=0)
    except soco.SoCoException, e:
      logging.exception(e)

  def playPlaylist(self, playlistName):
    logging.info("  playing playlist '%s'" % playlistName)
    try:
      playlist = self._player.get_sonos_playlist_by_attr('title', playlistName)
      self.playUri(playlist.get_uri())
    except ValueError:
      logging.error("  Sonos playlist %s not found" % playlistName)
    except soco.SoCoException, e:
      logging.exception(e)

  def stop(self):
    logging.info("stop playing")
    try:
      self._player.stop()
    except soco.SoCoException, e:
      logging.exception(e)

  def action_sonos_uri(self, actionConfig):
    if actionConfig.has_key('uri'):
      logging.info("  playing %s" % actionConfig.get('name', actionConfig['uri']))
      self.playUri(actionConfig['uri'])
    else:
      logging.error("  uri not defined")

  def action_sonos_playlist(self, actionConfig):
    if actionConfig.has_key('playlist'):
      logging.info("  playing %s" % actionConfig['playlist'])
      self.playPlaylist(actionConfig['playlist'])
    else:
      logging.error("  playlist not defined")


class MockSonosController(SonosController):
    def __init__(self, player_name):
        self.player_name = player_name

    def playUri(self, uri):
        logging.debug("play URI %s" % uri)

    def playPlaylist(self, playlistName):
        logging.debug("play playlist %s" % playlistName)

    def stop(self):
        logging.debug("stop playing")


class SongBlocks(object):

  def __init__(self, config, poller, player):
    self.config = config
    self.poller = poller
    self.player = player

  def tagPresent(self, tag):
    logging.info("play song for tag %s" % tag)
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


# main
if __name__ == "__main__":
  # TODO add CLI args
  configFile = 'songblocks.ini'
  logging.config.fileConfig(configFile)

  config = ConfigParser.SafeConfigParser()
  config.read(configFile)
  device_path = config.get("Config", "nfc_device_path")
  player_name = config.get("Config", "player_name")
  player_type = config.get("Config", "player_type").lower().capitalize()
  testing = config.get('Config', 'testing').lower() 
  if testing == "true":
    testing = True
  else:
    testing = False

  if testing:
    # TODO do this with test cases instead
    poller = MockNFCPoller(device_path)
    if player_type == "Sonos":
      player = MockSonosController(player_name)
    elif player_type == "Chromecast":
      player = MockChromecastController(player_name)
    else:
      raise SongblocksException("Unknown player_type %s" % player_type)
  else:
    import nfc
    poller = NFCPoller(device_path)

    if player_type == "Sonos":
      import soco
      player = SonosController(player_name)
    elif player_type == "Chromecast":
      import pychromecast
      player = ChromecastController(player_name)
    else:
      raise SongblocksException("Unknown player_type %s" % player_type)


  controller = SongBlocks(config, poller, player)
  controller.run()

