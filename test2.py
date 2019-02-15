from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
import random
import tensorflow as tf
import numpy as np

from absl import app


class NetworkingHandlingThingy:
    def __init__(self):
        self.memory = []

        self.gamma = 0.95 #future rewards thing?

        self.epsilon = 0.10 #Chance of doing random stuff
        self.epsilonDecay = 0.95
        self.epsilonMin = 0.01

        self.learningRate = 0.001

        self.ann = self.createNetwork()

    def createNetwork(self):
        ann = tf.keras.models.Sequential()
        ann.add(tf.keras.layers.Dense(2, activation='relu', input_shape=(2,)))
        ann.add(tf.keras.layers.Dense(2, activation='relu'))
        ann.add(tf.keras.layers.Dense(3, activation='linear'))

        ann.compile(optimizer='adam',
                    loss='mse',
                    metrics=['mae'])
        return ann

    def remember (self, state, action, reward):
        self.memory = self.memory + [(state, action, reward)]

    def getMemory(self):
        return self.memory

    def replay(self, batchSize):
        samples = []
        while batchSize > 0:
            batchSize-=1
            #print(self.memory)
            #print(len(self.memory))
            i = random.randint(0,len(self.memory)-2)
            samples = samples + [(self.memory[i][0],self.memory[i][1],self.memory[i][2],self.memory[i+1][0])]
        #print(samples)

        for sample in samples:
            target = sample[2] + self.gamma*np.amax(self.ann.predict(sample[3])[0]) #target = reward+self.gamma*npamax(self.model.predict(next_state)[0]
            target_f = self.ann.predict(sample[0])
            target_f[0][sample[1]-1] = target

            self.ann.fit(sample[0], target_f, epochs=1, verbose=0)

        if self.epsilon > self.epsilonMin:
            self.epsilon *= self.epsilonDecay

networkThingy = NetworkingHandlingThingy()

class MiningAgent(base_agent.BaseAgent):
    actionIndex = 1
    justSelectedWorker = 0
    idleWorkersLast = 0
    def step(self, obs):
        super(MiningAgent, self).step(obs)
        #V----------Logic goes here------------V
        if obs.first():
            self.justSelectedWorker = 0
            self.idleWorkersLast = obs.observation["player"][7]

        workers = [unit for unit in obs.observation.feature_units
                  if unit.unit_type == units.Terran.SCV]

        minerals = [unit for unit in obs.observation.feature_units
                   if unit.unit_type == units.Neutral.MineralField]
        rMineral = random.choice(minerals)


        idleWorkers = obs.observation["player"][7]
        #test = obs.observation["player"][7]
        annInput = np.array([self.justSelectedWorker,idleWorkers],ndmin=2)
        #annInput = np.random.random(1,2)
        annOutput = networkThingy.ann.predict(annInput)
        #test = ann.
        #print(annOutput)


        #----Print actions----
        #for action in obs.observation.available_actions:
        #    print(actions.FUNCTIONS[action])

        if np.random.rand() > networkThingy.epsilon:
            self.actionIndex = np.argmax(annOutput)
        else:
            self.actionIndex = random.randint(1,3)

        networkThingy.remember(annInput, self.actionIndex, -0.05 + (self.idleWorkersLast - idleWorkers))
        self.idleWorkersLast = idleWorkers

        if self.actionIndex == 1:
            self.actionIndex = 2
            self.justSelectedWorker = 1
            return actions.FUNCTIONS.select_idle_worker("select")
        elif self.actionIndex == 2:
            self.actionIndex = 0
            if self.justSelectedWorker == 1 and idleWorkers > 1: #Prevents crashes
                self.justSelectedWorker = 0
                return actions.FUNCTIONS.Harvest_Gather_screen("now", (rMineral.x,rMineral.y))
            self.justSelectedWorker = 0
        else:
            self.justSelectedWorker = 0
            return actions.FUNCTIONS.no_op()

        #if self.test ==0:
        #    if len(workers) > 0:
        ##        self.test += 1
        #       return actions.FUNCTIONS.select_idle_worker("select")


        #return actions.FUNCTIONS.no_op()
        return actions.FUNCTIONS.no_op()


#Stuff to run the game
def main(unused_argv):
    agent = MiningAgent()
    maxIterations = 200
    i = 1

    try:
        while i <= maxIterations:
            i += 1
            print(networkThingy.epsilon)
            with sc2_env.SC2Env(
                    map_name="CollectMineralsAndGas",
                   # map_name="AbyssalReef",
                   # players=[sc2_env.Agent(sc2_env.Race.zerg),
                   #          sc2_env.Bot(sc2_env.Race.zerg,             #Change this to fight self?
                   #                      sc2_env.Difficulty.very_easy)],
                    players=[sc2_env.Agent(sc2_env.Race.zerg)],
                    agent_interface_format=features.AgentInterfaceFormat(
                        feature_dimensions=features.Dimensions(screen=84, minimap=64),
                        use_feature_units=True),
                    step_mul=16,
                    game_steps_per_episode=50000,
                    visualize=False) as env:

                agent.setup(env.observation_spec(), env.action_spec())

                timesteps = env.reset()
                agent.reset()

                while True:
                    step_actions = [agent.step(timesteps[0])]
                    if timesteps[0].last():
                        break
                    timesteps = env.step(step_actions)

            print(len(networkThingy.memory))
            networkThingy.replay(200)
            networkThingy.memory = []

    except KeyboardInterrupt:
        pass



if __name__ == "__main__":
    app.run(main)