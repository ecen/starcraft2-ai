from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features
from absl import app
import numpy as np

np.set_printoptions(threshold=np.inf)
#-------------------------------------Input Space--------------------------------------------------------------
#-------------------------------------SCREEN DATA GET FUNCTIONS------------------------------------------------
#These return a 2d array of bytes, where the bytes represent different things
#Getters for creep(zerg only), power(protoss only), shields(protoss only)
def getHeightMinimap(obs):
    return obs.observation.feature_minimap.height_map
def getVisiblityMinimap(obs):
    return obs.observation.feature_minimap.visibility_map
def getCameraMinimap(obs):
    return obs.observation.feature_minimap.camera
#Returns relative faction to player, 1 = player unit, 2 = hostile?, 3 = neutral, 0 = no unit
def getFactionsMinimap(obs):
    return obs.observation.feature_minimap.player_relative
#Returns true player numbers, compared to the relative version above.
def getFactionsRawMinimap(obs):
    return obs.observation.feature_minimap.player_id
def getSelectedMinimap(obs):
    return obs.observation.feature_minimap.selected

def getHeightScreen(obs):
    return obs.observation.feature_screen.height_map
def getVisibilityScreen(obs):
    return obs.observation.feature_screen.visibility_map
def getFactionsScreen(obs):
    return obs.observation.feature_screen.player_relative
def getFactionsRawScreen(obs):
    return obs.observation.feature_screen.player_id
def getUnitsScreen(obs):
    return obs.observation.feature_screen.unit_type
def getSelectedScreen(obs):
    return obs.observation.feature_screen.selected
def getHPScreen(obs):
    return obs.observation.feature_screen.unit_hit_points
def getHPRatioScreen(obs):
    return obs.observation.feature_screen.unit_hit_points_ratio
def getManaScreen(obs):
    return obs.observation.feature_screen.unit_energy
def getManaRatioScreen(obs):
    return obs.observation.feature_screen.unit_energy_ratio
def getDensityScreen(obs):
    return obs.observation.feature_screen.unit_density
#Anti-aliased version of density
def getDensityAAScreen(obs):
    return obs.observation.feature_screen.unit_density_aa
#This is probably aoes, anyways
def getAOEsScreen(obs):
    return obs.observation.feature_screen.effects
#--------------------------------------END SCREEN GETS-------------------------------
#--------------------------------------Numeric Value Inputs--------------------------
def getMinerals(obs):
    return obs.observation.player.vespene
def getGas(obs):
    return obs.observation.player.minerals
def getSupply(obs):
    return obs.observation.player.food_used
def getSupplyMax(obs):
    return obs.observation.player.food_cap
#Returns difference between current and max, maybe used
def getSupplyFree(obs):
    return getSupplyMax(obs)-getSupply(obs)
def getSupplyWorkers(obs):
    return obs.observation.player.food_workers
def getSupplyArmy(obs):
    return obs.observation.player.food_army
def getPlayerID(obs):
    return obs.observation.player.player_id


class MarineAgent(base_agent.BaseAgent):
    def step(self, obs):
        super(MarineAgent, self).step(obs)


        exit()

        return actions.FUNCTIONS.no_op()


def main(unused_argv):
    agent = MarineAgent()
    try:
        while True:
            with sc2_env.SC2Env(
                    map_name="AbyssalReef",
                    players=[sc2_env.Agent(sc2_env.Race.terran),
                             sc2_env.Bot(sc2_env.Race.terran,
                                         sc2_env.Difficulty.very_easy)],
                    agent_interface_format=features.AgentInterfaceFormat(
                        feature_dimensions=features.Dimensions(screen=84, minimap=64)),
                    step_mul=16,
                    game_steps_per_episode=0,
                    visualize=True) as env:

                agent.setup(env.observation_spec(), env.action_spec())

                timesteps = env.reset()
                agent.reset()

                while True:
                    step_actions = [agent.step(timesteps[0])]
                    if timesteps[0].last():
                        break
                    timesteps = env.step(step_actions)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    app.run(main)