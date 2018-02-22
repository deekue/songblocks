#!/usr/bin/env python
#
#

import logging
import signal

import abc

logging.getLogger(__name__).addHandler(logging.NullHandler())

tags = [
    "2b1f76dd",
    "86eb5713",
    "06707b13",
    "00000001", # not in config
    ]



def interrupted(signum, frame):
  logging.debug('input timeout reached')
  raise Exception('input timeout reached')

signal.signal(signal.SIGALRM, interrupted)

def input():
  try:
      print "tag sim [0123s]: "
      result = raw_input()
      return result
  except:
      # timeout
      return


class MockPoller(abc.Poller):
  def poll_for_tag(self):
    signal.alarm(2)
    s = input()
    signal.alarm(0)

    if s is not None:
      if s.isdigit():
        result = tags[int(s)]
      elif s.isalpha():
        if s == "s":
          result = None
    else:
      result = self.poll_last_tag

    return result

