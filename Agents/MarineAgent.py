from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units

from absl import app
import numpy as np
import keras
from simpleSC2API import *
from stateHandler import *

np.set_printoptions(threshold=np.inf)


WR = keras.models.load_model("999.h5")


class MarineAgent(base_agent.BaseAgent):
    i = 0

    def step(self, obs):
        super(MarineAgent, self).step(obs)
        # This is the code that handles actions that require multiple steps, don't touch and leave at the top
        doingMultiAction = executeMultiAction(obs)
        if doingMultiAction != False:
            return doingMultiAction
        # End of multistep action code
        if obs.first():
            self.i = 0

        self.i = self.i+1
        if self.i == 1:
            return actMultiTrainSCV(obs)
        if self.i == 5:
            return actSelectAllSCVs(obs)
        if self.i == 30:
            return actBuildSupplyDepot(obs, 5, 5)
        if self.i == 80:
            return actBuildBarracks(obs, 50, 5)
        if self.i == 179:
            return actMultiTrainMarine(obs)
        if self.i == 380:
            return actSelectAllMarines(obs)
        if self.i == 381:
            return actSelectAddAllSCVs(obs)
        if self.i == 382:
            return actAttackMinimap(obs, 10, 10)
        #q = actHarvestScreen(obs, 20, 20)
        # print(q)
        # return q
        #concMinimap = np.array([[getFactionsMinimap(obs), getVisiblityMinimap(obs), getSelectedMinimap(obs)]])
        #concMinimap = np.moveaxis(concMinimap, 1, 3)
        numInput, input = getIngameNormalisedState(obs)
        #print(input.shape)
        #exit()
        numInput = np.array([numInput])
        input = np.array([input])
        input = np.moveaxis(input, 1, 3)
        print(WR.predict([numInput,input]))
        # exit()

        return actions.FUNCTIONS.no_op()


def main(unused_argv):
    agent = MarineAgent()
    try:
        while True:
            with sc2_env.SC2Env(
                    map_name="Automaton",
                    players=[sc2_env.Agent(sc2_env.Race.terran),
                             sc2_env.Bot(sc2_env.Race.terran,
                                         sc2_env.Difficulty.very_easy)],
                    agent_interface_format=features.AgentInterfaceFormat(
                        feature_dimensions=features.Dimensions(screen=64, minimap=64), use_feature_units=True),
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
