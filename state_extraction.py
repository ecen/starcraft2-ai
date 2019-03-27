from sc2reaper import unit_extraction
from sc2reaper import resources_extraction
from sc2reaper import supply_extraction
from google.protobuf.json_format import MessageToDict
import bson
import pickle
import pysc2.lib.features as feat
import numpy as np
from pysc2.lib import named_array
# -------------------------------------Input Space--------------------------------------------------------------
# -------------------------------------SCREEN DATA GET FUNCTIONS------------------------------------------------
# These return a 2d array of bytes, where the bytes represent different things
# Getters for creep(zerg only), power(protoss only), shields(protoss only)

def getVisibilityMinimap(obs):
    return obs.feature_minimap.visibility_map


def getCameraMinimap(obs):
    return obs.feature_minimap.camera


# Returns relative faction to player, 1 = player unit, 2 = hostile?, 3 = neutral, 0 = no unit
def getFactionsMinimap(obs):
    return obs.feature_minimap.player_relative


# Returns true player numbers, compared to the relative version above.
def getFactionsRawMinimap(obs):
    return obs.feature_minimap.player_id


def getSelectedMinimap(obs):
    return obs.feature_minimap.selected


def getHeightScreen(obs):
    return obs.feature_screen.height_map


def getVisibilityScreen(obs):
    return obs.feature_screen.visibility_map


def getFactionsScreen(obs):
    return obs.feature_screen.player_relative


def getFactionsRawScreen(obs):
    return obs.feature_screen.player_id


def getUnitsScreen(obs):
    return obs.feature_screen.unit_type


def getSelectedScreen(obs):
    return obs.feature_screen.selected


def getHPScreen(obs):
    return obs.feature_screen.unit_hit_points


def getHPRatioScreen(obs):
    return obs.feature_screen.unit_hit_points_ratio


def getManaScreen(obs):
    return obs.feature_screen.unit_energy


def getManaRatioScreen(obs):
    return obs.feature_screen.unit_energy_ratio


def getDensityScreen(obs):
    return obs.feature_screen.unit_density


# Anti-aliased version of density
def getDensityAAScreen(obs):
    return obs.feature_screen.unit_density_aa


# This is probably aoes, anyways
def getAOEsScreen(obs):
    return obs.feature_screen.effects


# --------------------------------------END SCREEN GETS-------------------------------


def get_state(observation, obsParent):
    """
    This function returns a state, defined as a dict holding
        - a frame counter
        - the actual frame being recorded
        - resources of the player
        - supply
        - allied units (under the key "units")
        - allied units in progress (in "units_in_progress")
        - visible enemy units
        - seen enemy units (i.e. all the ones I have seen in the past).

    Recall that the observation object is defined here:
    https://github.com/deepmind/pysc2/blob/master/docs/environment.md#structured

    Yet, we heavily encourage just printing it to get a sense of what's inside.
    Since we're dealing with replays instead of games, the observations and
    the name of their attributes change.
    """

    # Creating the state
    state = {}

    # a.k.a game loop (or something similar when multiple actions are being stored)
    state["resources"] = {
        "minerals": resources_extraction.get_minerals(observation),
        "vespene": resources_extraction.get_vespene(observation),
    }

    state["supply"] = {
        "used": supply_extraction.get_used_supply(observation),
        "total": supply_extraction.get_total_supply(observation),
        "army": supply_extraction.get_army_supply(observation),
        "workers": supply_extraction.get_worker_supply(observation),
    }
    featuresInstance = feat.Features(agent_interface_format=feat.AgentInterfaceFormat(feature_dimensions=feat.Dimensions(screen=84, minimap=64), use_feature_units=False))


    pysc2Observation = featuresInstance.transform_obs(obsParent)
    #print(asdfasdf)

    state["minimap"] = {
        "factions": bson.binary.Binary(pickle.dumps(getFactionsMinimap(pysc2Observation), protocol=2)),
        "selected": bson.binary.Binary(pickle.dumps(getSelectedMinimap(pysc2Observation), protocol=2)),
        "vision": bson.binary.Binary(pickle.dumps(getVisibilityMinimap(pysc2Observation), protocol=2))
    }
    state["screen"] = {
        "factions": bson.binary.Binary(pickle.dumps(getFactionsScreen(pysc2Observation), protocol=2)),
        "units": bson.binary.Binary(pickle.dumps(getUnitsScreen(pysc2Observation), protocol=2)),
        "hp": bson.binary.Binary(pickle.dumps(getHPScreen(pysc2Observation), protocol=2)),
        "selected": bson.binary.Binary(pickle.dumps(getSelectedScreen(pysc2Observation), protocol=2)),
        "height": bson.binary.Binary(pickle.dumps(getHeightScreen(pysc2Observation), protocol=2)),
        "vision": bson.binary.Binary(pickle.dumps(getVisibilityScreen(pysc2Observation), protocol=2))
    }
    # Units in progress

    ## Adding buildings in progress
    state["units_in_progress"] = {}
    units_in_progress = unit_extraction.get_allied_units_in_progress(observation)
    for unit_type, unit_tag in units_in_progress:
        if str(unit_type) not in state["units_in_progress"]:
            state["units_in_progress"][str(unit_type)] = {
                str(unit_tag): units_in_progress[unit_type, unit_tag]
            }
        else:
            state["units_in_progress"][str(unit_type)][
                str(unit_tag)
            ] = units_in_progress[unit_type, unit_tag]

    state["upgrades"] = [upgrade for upgrade in observation.raw_data.player.upgrade_ids]

    return state
