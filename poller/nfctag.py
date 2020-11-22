#!/usr/bin/env python
#
#

import fcntl
import logging
import nfc
import os
import pyudev
import time

import abc

logging.getLogger(__name__).addHandler(logging.NullHandler())

class NFCPoller(abc.Poller):
  
  def poll_for_tag(self):
    """Poll device at device_path for a tag, return the UID if found, None if not. """
    tag = None
    with nfc.clf.ContactlessFrontend(self.device_path) as clf:
        target = clf.sense(nfc.clf.RemoteTarget("106A"))
        if target is not None:
            tag_obj = nfc.tag.activate(clf, target)
            if tag_obj is not None:
              tag = str(tag_obj.identifier).encode('hex')
    return tag

class USBNFCPoller(NFCPoller):
  tty_device_node = None
  usb_device_node = None

  def __init__(self, device_path, poll_interval_secs=0.5):
    super(USBNFCPoller, self).__init__(device_path, poll_interval_secs)
    # check we can use the device, try to reset once if it fails
    try:
      with nfc.clf.ContactlessFrontend(self.device_path) as clf:
          target = clf.sense(nfc.clf.RemoteTarget("106A"))
    except Exception as e:
      logging.error('failed to access %s in USBNFCPoller.__init__: %s' % (self.device_path, e))
      self._reset_usb()

  def _reset_usb(self):
    USBDEVFS_RESET = 21780
 
    if self.tty_device_node is None:
      # nfc library device path tty:USB0:pn526 = /dev/ttyUSB0
      (tty, usb, _) = self.device_path.split(':')
      self.tty_device_node = '/dev/%s%s' % (tty, usb)
      logging.debug('tty_device_node: %s' % self.tty_device_node)
    if self.usb_device_node is None:
      context = pyudev.Context()
      tty_device = pyudev.Devices.from_device_file(context, self.tty_device_node)
      self.usb_device_node = tty_device.find_parent('usb', 'usb_device').device_node
      logging.debug('usb_device_node: %s' % self.usb_device_node)
    try:
        logging.debug('Trying to reset device: %s' % self.usb_device_node)
        with open(self.usb_device_node, 'w', os.O_WRONLY) as node:
            fcntl.ioctl(node, USBDEVFS_RESET, 0)
    except Exception as ex:
        logging.error('Failed to reset device! Error: %s' % ex)
        raise ex
    time.sleep(3) # wait for device to settle
    logging.error('Successfully reset %s' % self.usb_device_node)

