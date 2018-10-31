#!/usr/bin/env python
#
#

import logging
import time

logging.getLogger(__name__).addHandler(logging.NullHandler())

class Poller(object):
  """ABC for a polling device to provide 'tag' UUIDs."""
  poll_last_tag = None

  def __init__(self, device_path, poll_interval_secs=0.5):
    self.poll_interval_secs = poll_interval_secs
    self.device_path = device_path

  def run(self, tagPresent=None, tagRemoved=None):
    while True:
      tag = self.poll_for_tag()
      if tag == None:
        logging.debug("no tag detected")
        if self.poll_last_tag != None:
          logging.debug("  tag %s was present last time" % self.poll_last_tag)
          self.poll_last_tag = None
          if tagRemoved != None:
            tagRemoved()
      else:
        logging.debug("tag detected: %s" % tag)
        if tag == self.poll_last_tag:
          logging.debug("  same tag as last time")
        else:
          logging.debug("  new tag")
          self.poll_last_tag = tag
          if tagPresent != None:
            tagPresent(tag)
    
      time.sleep(self.poll_interval_secs)

  def poll_for_tag(self):
    """Poll device at device_path for a tag, return the UID if found, None if not. """
    pass

