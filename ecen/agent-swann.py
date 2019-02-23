from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features

FUNCTIONS = actions.FUNCTIONS

# Functions
_BUILD_SUPPLYDEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
_NOOP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id

# Features
_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index

_PLAYER_SELF = features.PlayerRelative.SELF
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL  # beacon/minerals
_PLAYER_ENEMY = features.PlayerRelative.ENEMY

# Unit IDs
_TERRAN_COMMANDCENTER = 18
_TERRAN_SCV = 45

# Parameters
_PLAYER_SELF = 1
_NOT_QUEUED = [0]
_QUEUED = [1]


def _xy_locs(mask):
   """Mask should be a set of bools from comparison with a feature layer."""
   print(mask)
   y, x = mask.nonzero()
   return list(zip(x, y))

class SwannMoveToBeacon(base_agent.BaseAgent):
   """An agent specifically for solving the MoveToBeacon map."""

   def step(self, obs):
      super(SwannMoveToBeacon, self).step(obs)
      if FUNCTIONS.Move_screen.id in obs.observation.available_actions:
         player_relative = obs.observation.feature_screen.player_relative
         beacon = _xy_locs(player_relative == _PLAYER_NEUTRAL)
         if not beacon:
            return FUNCTIONS.no_op()
         beacon_center = numpy.mean(beacon, axis=0).round()
         return FUNCTIONS.Move_screen("now", beacon_center)
      else:
         return FUNCTIONS.select_army("select")

class SwannCraft(base_agent.BaseAgent):
    """Agent for playing the Simple64 map."""
    base_top_left = None # True if our base is the top left one.

    # Detect if our base is the top left one by taking the mean y-coordinate of our units.
    if self.base_top_left is None:
        player_y, player_x = (obs.observation["minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
        self.base_top_left = player_y.mean() <= 31

    # Transform coordinates and distances based on where our base is.
    def transformLocation(self, x, x_distance, y, y_distance):
        if not self.base_top_left:
            return [x - x_distance, y - y_distance]

        return [x + x_distance, y + y_distance]

    def step(self, obs):
        super(SwannCraft, self).step(obs)

        return FUNCTIONS.no_op()
