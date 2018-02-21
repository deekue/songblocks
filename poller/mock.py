#!/usr/bin/env python
#
#

import logging

import abc

class MockPoller(abc.Poller):
  def poll_for_tag(self):
    # TODO add a way to trigger mock tags
    return '2b1f76dd'


