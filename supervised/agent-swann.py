from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy
import time

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features

FUNCTIONS = actions.FUNCTIONS

# Functions
_BUILD_SUPPLYDEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
_BUILD_BARRACKS = actions.FUNCTIONS.Build_Barracks_screen.id
_TRAIN_MARINE = actions.FUNCTIONS.Train_Marine_quick.id
_RALLY_UNITS_MINIMAP = actions.FUNCTIONS.Rally_Units_minimap.id
_NOOP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_ATTACK_MINIMAP = actions.FUNCTIONS.Attack_minimap.id

# Features
_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index

_PLAYER_SELF = features.PlayerRelative.SELF
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL  # beacon/minerals
_PLAYER_ENEMY = features.PlayerRelative.ENEMY

# Unit IDs
_TERRAN_COMMANDCENTER = 18
_TERRAN_BARRACKS = 21
_TERRAN_SCV = 45

# Parameters
_PLAYER_SELF = 1
_NOT_QUEUED = [0]
_QUEUED = [1]
_SUPPLY_USED = 3
_SUPPLY_MAX = 4


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
   base_top_left = None  # True if our base is the top left one.
   scv_selected = False
   supply_depot_built = False
   barracks_built = False
   barracks_selected = False
   barracks_rallied = False
   supply_offset = 0
   army_selected = False
   army_rallied = False

   # Transform coordinates and distances based on where our base is.
   def transformLocation(self, x, x_distance, y, y_distance):
      if not self.base_top_left:
         return [x - x_distance, y - y_distance]

      return [x + x_distance, y + y_distance]

   def select(self, unit):
      self.scv_selected = False
      self.barracks_selected = False
      self.army_selected = False
      if (unit == "scv"):
         print("Selected SCV")
         self.scv_selected = True
      elif (unit == "barracks"):
         print("Selected Barracks")
         self.barracks_selected = True
      elif (unit == "army"):
         print("Selected Army")
         self.army_selected = True
      else:
         print("Error in selecting " + unit)

   def step(self, obs):
      super(SwannCraft, self).step(obs)
      time.sleep(0.016)
      # Detect if our base is the top left one by taking the mean y-coordinate of our units.
      if self.base_top_left is None:
         # print("PRINT: " + obs.observation.items())
         player_y, player_x = (
             obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
         self.base_top_left = player_y.mean() <= 31

      # Build supply depot if not built already
      if not self.supply_depot_built:
         # Select SCV
         if not self.scv_selected:
            unit_type = obs.observation["feature_screen"][_UNIT_TYPE]
            unit_y, unit_x = (unit_type == _TERRAN_SCV).nonzero()

            target = [unit_x[0], unit_y[0]]
            self.select("scv")
            return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
         # Build supply depot
         elif _BUILD_SUPPLYDEPOT in obs.observation["available_actions"]:
            unit_type = obs.observation["feature_screen"][_UNIT_TYPE]
            unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()

            print("BUILDING: " + str(self.supply_offset))
            target = self.transformLocation(
                int(unit_x.mean()), 0 + self.supply_offset,
                int(unit_y.mean()), 20)
            self.supply_offset += 4

            self.supply_depot_built = True

            return actions.FunctionCall(_BUILD_SUPPLYDEPOT, [_NOT_QUEUED, target])
      # After supply depot is built, build a barracks
      elif not self.barracks_built:
         if _BUILD_BARRACKS in obs.observation["available_actions"]:
            unit_type = obs.observation["feature_screen"][_UNIT_TYPE]
            unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()

            target = self.transformLocation(
                int(unit_x.mean()), 20, int(unit_y.mean()), 0)

            self.barracks_built = True

            return actions.FunctionCall(_BUILD_BARRACKS, [_NOT_QUEUED, target])
      elif not self.barracks_rallied:
         if not self.barracks_selected:
            unit_type = obs.observation["feature_screen"][_UNIT_TYPE]
            unit_y, unit_x = (unit_type == _TERRAN_BARRACKS).nonzero()

            # If there is any barracks
            if unit_y.any():
               # Set the barracks as our target
               target = [int(unit_x.mean()), int(unit_y.mean())]
               self.select("barracks")
               # Action to select our target barracks
               return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
         else:
            self.barracks_rallied = True

            if self.base_top_left:
               return actions.FunctionCall(_RALLY_UNITS_MINIMAP, [_NOT_QUEUED, [29, 21]])

            return actions.FunctionCall(_RALLY_UNITS_MINIMAP, [_NOT_QUEUED, [29, 46]])
      elif obs.observation["player"][_SUPPLY_USED] < \
              obs.observation["player"][_SUPPLY_MAX]:
         if not self.barracks_selected:
            unit_type = obs.observation["feature_screen"][_UNIT_TYPE]
            unit_y, unit_x = (unit_type == _TERRAN_BARRACKS).nonzero()
            # If there is any barracks
            if unit_y.any():
               # Set the barracks as our target
               target = [int(unit_x.mean()), int(unit_y.mean())]
               self.select("barracks")
               # Action to select our target barracks
               return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
         elif _TRAIN_MARINE in obs.observation["available_actions"]:
            print("Train marine")
            self.army_rallied = False
            return actions.FunctionCall(_TRAIN_MARINE, [_QUEUED])
#      elif obs.observation["player"][_SUPPLY_USED] >= \
#              obs.observation["player"][_SUPPLY_MAX] - 2 and \
#              self.supply_offset < 30:
#         self.supply_depot_built = False
      elif not self.army_rallied:
         print("Rally army")
         if not self.army_selected:
            print("Select army")
            if _SELECT_ARMY in obs.observation["available_actions"] and \
                    not self.army_selected:
               self.select("army")
               return actions.FunctionCall(_SELECT_ARMY, [_NOT_QUEUED])
         elif _ATTACK_MINIMAP in obs.observation["available_actions"]:
            self.army_rallied = True
            self.army_selected = False

            print("Attack!")
            if self.base_top_left:
               return actions.FunctionCall(_ATTACK_MINIMAP, [_NOT_QUEUED, [39, 45]])

            return actions.FunctionCall(_ATTACK_MINIMAP, [_NOT_QUEUED, [21, 24]])
      return FUNCTIONS.no_op()
