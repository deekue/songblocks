#!/usr/bin/env python
#
#

import logging
import pychromecast

import abc

logging.getLogger(__name__).addHandler(logging.NullHandler())

class ChromecastControllerException(Exception):
  pass

class ChromecastController(abc.PlayerBase):
  _cast = None

  def __init__(self, cast_name):
    self.cast_name = cast_name
    logging.debug("searching for local Chromecast devices...")
    chromecasts = pychromecast.get_chromecasts()
    logging.debug("found %s" % chromecasts)
    self._cast = next(cc for cc in chromecasts if cc.device.friendly_name == cast_name)
    if self._cast == None:
      raise ChromecastControllerException("Chromecast %s not found" % cast_name)
    self._mc = self._cast.media_controller

  def playUri(self, uri, content_type):
    try:
      self._mc.play_media(uri, content_type)
    except pychromecast.PyChromecastError:
      logging.error("pychromecast threw an exception in playUri()",
              exc_info=True)

  def action_chromecast_uri(self, actionConfig):
    if actionConfig.has_key('uri'):
      logging.debug("  playing %s" % actionConfig.get('name', actionConfig['uri']))
      content_type = actionConfig.get('content_type', 'audio/mp3')
      self.playUri(actionConfig['uri'], content_type)
    else:
      logging.error("  uri not defined")

  def stop(self):
    self._mc.stop()


