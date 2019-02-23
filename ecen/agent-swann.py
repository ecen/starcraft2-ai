from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features

_PLAYER_SELF = features.PlayerRelative.SELF
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL  # beacon/minerals
_PLAYER_ENEMY = features.PlayerRelative.ENEMY

FUNCTIONS = actions.FUNCTIONS


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
    def step(self, obs):
        super(SwannCraft, self).step(obs)

        return FUNCTIONS.no_op()
