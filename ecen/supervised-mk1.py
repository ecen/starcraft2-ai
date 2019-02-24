import random
import math

import numpy as np

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features

_NO_OP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_BUILD_SUPPLY_DEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
_BUILD_BARRACKS = actions.FUNCTIONS.Build_Barracks_screen.id
_TRAIN_MARINE = actions.FUNCTIONS.Train_Marine_quick.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_ATTACK_MINIMAP = actions.FUNCTIONS.Attack_minimap.id

_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index
_PLAYER_ID = features.SCREEN_FEATURES.player_id.index

_PLAYER_SELF = 1

_TERRAN_COMMANDCENTER = 18
_TERRAN_SCV = 45
_TERRAN_SUPPLY_DEPOT = 19
_TERRAN_BARRACKS = 21

_NOT_QUEUED = [0]
_QUEUED = [1]


DO_NOTHING = 'donothing'
SELECT_SCV = 'selectscv'
BUILD_SUPPLY_DEPOT = 'buildsupplydepot'
BUILD_BARRACKS = 'buildbarracks'
SELECT_BARRACKS = 'selectbarracks'
BUILD_MARINE = 'buildmarine'
SELECT_ARMY = 'selectarmy'
ATTACK = 'attack'

goals = [
    DO_NOTHING,
    SELECT_SCV,
    BUILD_SUPPLY_DEPOT,
    BUILD_BARRACKS,
    SELECT_BARRACKS,
    BUILD_MARINE,
    SELECT_ARMY,
    ATTACK,
]


class Mk1(base_agent.BaseAgent):
   def transformLocation(self, x, x_distance, y, y_distance):
      if not self.base_top_left:
         return [x - x_distance, y - y_distance]

      return [x + x_distance, y + y_distance]

   def step(self, obs):
      super(Mk1, self).step(obs)

      # Get player location
      player_y, player_x = (
          obs.observation['feature_minimap'][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
      self.base_top_left = 1 if player_y.any() and player_y.mean() <= 31 else 0

      # Choose random action
      goal = goals[random.randrange(0, len(goals))]

      if goal == SELECT_SCV:
         print("Selecting SCV")
         unit_type = obs.observation['feature_screen'][_UNIT_TYPE]
         unit_y, unit_x = (unit_type == _TERRAN_SCV).nonzero()
         if unit_y.any():
            i = random.randint(0, len(unit_y) - 1)
            target = [unit_x[i], unit_y[i]]
            return actions.FunctionCall(
                _SELECT_POINT, [_NOT_QUEUED, target])

      elif goal == BUILD_SUPPLY_DEPOT:
         if _BUILD_SUPPLY_DEPOT in obs.observation['available_actions']:
            unit_type = obs.observation['feature_screen'][_UNIT_TYPE]
            unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()
            if unit_y.any():
               print("Building Supply")
               target = self.transformLocation(
                   int(unit_x.mean()), 0, int(unit_y.mean()), 20)
               return actions.FunctionCall(
                   _BUILD_SUPPLY_DEPOT, [_NOT_QUEUED, target])

      elif goal == BUILD_BARRACKS:
         if _BUILD_BARRACKS in obs.observation['available_actions']:
            unit_type = obs.observation['feature_screen'][_UNIT_TYPE]
            unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()
            if unit_y.any():
               target = self.transformLocation(
                   int(unit_x.mean()), 20, int(unit_y.mean()), 0)
               print("Building Barracks")
               return actions.FunctionCall(
                   _BUILD_BARRACKS, [_NOT_QUEUED, target])

      elif goal == SELECT_BARRACKS:
         unit_type = obs.observation['feature_screen'][_UNIT_TYPE]
         unit_y, unit_x = (unit_type == _TERRAN_BARRACKS).nonzero()

         if unit_y.any():
            target = [int(unit_x.mean()), int(unit_y.mean())]
            print("Selecting Barracks")
            return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])

      elif goal == BUILD_MARINE:
         if _TRAIN_MARINE in obs.observation['available_actions']:
            print("Training Marine")
            return actions.FunctionCall(_TRAIN_MARINE, [_QUEUED])

      elif goal == SELECT_ARMY:
         if _SELECT_ARMY in obs.observation['available_actions']:
            print("Selecting Army")
            return actions.FunctionCall(_SELECT_ARMY, [_NOT_QUEUED])

      elif goal == ATTACK:
         print("Trying to Attack")
         if _ATTACK_MINIMAP in obs.observation["available_actions"]:
            print("Attacking")
            if self.base_top_left:
               return actions.FunctionCall(_ATTACK_MINIMAP, [_NOT_QUEUED, [39, 45]])

            return actions.FunctionCall(_ATTACK_MINIMAP, [_NOT_QUEUED, [21, 24]])

      print("Noop")
      return actions.FunctionCall(_NO_OP, [])
