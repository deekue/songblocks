#!/usr/bin/env python
#
#

import logging

import abc

logging.getLogger(__name__).addHandler(logging.NullHandler())

class MockPoller(abc.Poller):
  def poll_for_tag(self):
    # TODO add a way to trigger mock tags
    return '2b1f76dd'


