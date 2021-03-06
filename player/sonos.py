#!/usr/bin/env python
#
#

import logging
import soco

import abc

logging.getLogger(__name__).addHandler(logging.NullHandler())


class SonosControllerException(Exception):
  pass


class SonosController(abc.PlayerBase):
  _player = None
  _currentAction = None

  def __init__(self, player_name):
    self.player_name = player_name
    logging.debug("Searching for Sonos device, %s" % player_name)
    try:
      self._player = soco.discovery.by_name(player_name)
    except soco.SoCoException, e:
      raise SonosControllerException('Sonos player "%s" not found. Error: %s' % (player_name, e))
    if self._player == None:
      raise SonosControllerException('Sonos player "%s" not found' % player_name)

  def playUri(self, uri, actionConfig):
    logging.debug("  playing URI %s" % uri)
    try:
      if actionConfig.has_key('play_mode'):
          self._player.play_mode = actionConfig['play_mode']
      if actionConfig.has_key('volume'):
          self._player.ramp_to_volume(actionConfig['volume'])
      self._player.clear_queue()
      self._player.add_uri_to_queue(uri)
      self._player.play_from_queue(index=0)
    except soco.SoCoException, e:
      logging.error("soco threw an exception in playUri()", exc_info=True)
    self._currentAction = actionConfig

  def stop(self):
    logging.debug("stop playing")
    if self._currentAction != None:
      stop_on_remove = self._currentAction.get('stop_on_remove', 'true').lower()
      if stop_on_remove == 'true':
        try:
          self._player.stop()
        except soco.SoCoException, e:
          logging.error("soco threw an exception in stop()", exc_info=True)
        finally:
          self._currentAction = None
      else:
        logging.debug("not stopping")
    else:
      logging.error("self._currentAction is None in stop()")

  def action_sonos_uri(self, actionConfig):
    if actionConfig.has_key('uri'):
      logging.debug("  playing %s" % actionConfig.get('name', actionConfig['uri']))
      self.playUri(actionConfig['uri'], actionConfig['uri'])
    else:
      logging.error("  uri not defined")

  def action_sonos_playlist(self, actionConfig):
    if actionConfig.has_key('playlist'):
      logging.debug("  playing playlist %s" % actionConfig['playlist'])
      try:
        playlist = self._player.get_sonos_playlist_by_attr('title', actionConfig['playlist'])
      except ValueError:
        logging.error("  Sonos playlist %s not found" % actionConfig['playlist'])
      self.playUri(playlist.get_uri(), actionConfig)
    else:
      logging.error("  playlist not defined")


