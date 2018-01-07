songblocks
==========

A python script to remotely control a Sonos music player with NFC tags.
Based on [Songblocks](http://shawnrk.github.io/songblocks).
  
I had to rewrite [shawnrk](http://github.com/shawnrk)'s code as enough had changed in the intervening 3 years
that I couldn't get it working.

Changes:

* added a config file (songblocks.ini)
* added support for playing a Sonos playlist in addition to individual tracks
* added Chromecast support (using pychromecast)
* removed Twitter support
* removed time-of-day restrict
* removed track seek and volume control
  
I used the [FTDI Serial TTL-232 USB Cable](https://www.adafruit.com/product/70)
initially so I could work on my laptop.  I haven't bothered switching to I2C or
SPI on the Raspberry Pi as the USB cable works fine :)
However If you kill the process while it's
talking to the NFC board, the board gets wedged and you have to power cycle it
(pull the USB cable and replug).

# Installation (WIP)
1. sudo apt install pip
1. sudo pip install -r requirements.txt
1. $EDITOR songblocks.ini
   * set the player_name to the Sonos device you want to control
   * set the nfc_device_path as per [nfcpy docs](http://nfcpy.readthedocs.io/en/latest/overview.html)
1. python songblocks.py

# Hardware
## Reader
* Raspberry Pi (an RPi 1 works fine)
* [PN532 NFC/RFID controller breakout board](https://www.adafruit.com/product/364)
* [FTDI Serial TTL-232 USB Cable](https://www.adafruit.com/product/70)

## Blocks
* [13.56MHz RFID/NFC white tag 1KB](https://www.adafruit.com/product/360)
* [Magnetic Pin Back](https://www.adafruit.com/product/1170)
* 6" piece of pine 2x4 I had stashed in the garage

## Tools
* soldering iron + solder (to solder headers to PN532 board)
* 1/2" and 1-1/8" Forstner drill bits (drill slots for magnets/tags in blocks and drawer)
* cordless drill
* dual edge pullsaw (cut 2x4 into kid-size blocks)
* wood glue
* sandpaper
* various clamps
