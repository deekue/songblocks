#!/usr/bin/env python
#
#

class PlayerBase(object):
    """ABC for a player, something that will play music based on info from the
    config file."""

    def action_actionname(self, tagConfig):
        """example action executed when a tag == present.
        eg. action_sonos_uri -> songblocks.ini [tag-238fab] action = Sonos URI
        """
        pass

    def stop(self):
        """stop playing music on configured player."""
        pass

