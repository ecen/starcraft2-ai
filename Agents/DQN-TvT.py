from pysc2.agents import base_agent
from pysc2.env import sc2_env
import random
import tensorflow as tf
import numpy as np
import os
import datetime
from simpleSC2API import *

from collections import deque
import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from time import time
from simpleSC2API import *

from absl import app

# Log variables
timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
trainingStartTime = time()
stepCounter = 0

SUPPLY_LOCATIONS = [
        (30, 8), (34, 8), (38, 8), (42, 8), (46, 8), (50, 8),
        (30, 12), (34, 12), (38, 12), (42, 12), (46, 12), (50, 12), 
        (30, 16), (34, 16), (38, 16), (42, 16), (46, 16), (50, 16), 
        (30, 20), (34, 20), (38, 20), (42, 20), (46, 20), (50, 20)
    ]

#<editor-fold desc="Network"
####Most code for DQNSolver from https://github.com/gsurma/cartpole####
#This is the network, structure is defined in __init__
#Other hyper parameters are here

#Future rewards discount
GAMMA = 0.99
LEARNING_RATE = 0.00001

MEMORY_SIZE = 1000000
#Size of minibatches used during learning
BATCH_SIZE = 20
#Chance to take random action instead of using the network's output
#Max = starting chance, is multiplied by decay after each experience replay
#until it reaches min chance
EXPLORATION_MAX = 1.0
EXPLORATION_MIN = 0.2
EXPLORATION_DECAY = 0.99999

loadNetworkOnlyExploit = False #TODO True if loading trained network
class DQNSolver:
    def __init__(self, observation_space, action_space):

        self.action_space = action_space
        self.memory = deque(maxlen=MEMORY_SIZE)
        global loadNetworkOnlyExploit
        if not loadNetworkOnlyExploit:
            self.exploration_rate = EXPLORATION_MAX

            #Creation of network, topology stuff goes here
            asd = keras.initializers.VarianceScaling(scale=2) #https://towardsdatascience.com/tutorial-double-deep-q-learning-with-dueling-network-architectures-4c1b3fb7f756
            self.model = Sequential()
            self.model.add(Dense(32, input_shape=(observation_space,), activation="relu", kernel_initializer=asd)) # TODO: Is asd a typo?
            self.model.add(Dense(16, activation="relu", kernel_initializer=asd))
            self.model.add(Dense(self.action_space, activation="linear", kernel_initializer=asd))
            self.model.compile(loss="logcosh", optimizer=Adam(lr=LEARNING_RATE))

        else:
            self.exploration_rate = 0
            #TODO Path of network to load if loading network
            self.model = keras.models.load_model("testNetwork5005.h5")


    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() < self.exploration_rate:
            return random.randrange(self.action_space)
        q_values = self.model.predict(state)
        #print('Q values: {}'.format(q_values))
        return np.argmax(q_values[0])
        #print('Selecting: {}'.format(np.argmax(q_values[0])))
        #return getRandomWeightedIndex(q_values[0])

    def experience_replay(self):
        if len(self.memory) < BATCH_SIZE:
            return
        batch = random.sample(self.memory, BATCH_SIZE)
        for state, action, reward, state_next, terminal in batch:
            q_update = reward
            if not terminal:
                q_update = (reward + GAMMA * np.amax(self.model.predict(state_next)[0]))

            # print('State: {}'.format(state))
            q_values = self.model.predict(state)
            q_values[0][action] = q_update
            # print('Q_table: {} action: {} Q_update = {} state: {} state_next: {}'.format(q_values,action,q_update,state,state_next))
            self.model.fit(state, q_values, verbose=0)
        self.exploration_rate *= EXPLORATION_DECAY
        self.exploration_rate = max(EXPLORATION_MIN, self.exploration_rate)

    def save(self, name):
        self.model.save(name+'.h5')

#Size of input
obsSpace = 4
#Size of output /availble actions
actSpace = 5
#init of network
dqn_solver = DQNSolver(obsSpace, actSpace)

class MarineAgent(base_agent.BaseAgent):
    state = None
    action = None
    justSelectWorker = -1
    freeWorkersOld = 12
    nextSupplyNr = 0

    def step(self, obs):
        super(MarineAgent, self).step(obs)
        global dqn_solver #Let python access the global variable dqn_solver
        global stepCounter 
        stepCounter += 1
        if obs.last():
            print(dqn_solver.exploration_rate)
            score = obs.observation.score_cumulative.collected_minerals
            if dqn_solver.exploration_rate <= EXPLORATION_MIN:
                compareResultsAndSave(score)
            # Log score to file
            t1 = time() - trainingStartTime
            logFile = open(timestamp + ".log","a+")
            logFile.write("score=%4d, explore=%.4f, time=%7ds, steps=%8d, supplyWorkers=%2d\n" % (score, dqn_solver.exploration_rate, t1, stepCounter, getSupplyWorkers(obs)))
            logFile.close()

        # <editor-fold> desc="Multistep action stuff, leave it alone"
        #This is the code that handles actions that require multiple steps, don't touch and leave at the top
        doingMultiAction = executeMultiAction(obs)
        if doingMultiAction != False:
            return doingMultiAction
        #</editor-fold>

        # <editor-fold> desc="Read game data / input, handle it"
        newState = np.array([[(min(getMinerals(obs),100)-50)/50, getFreeWorkers(obs)/20, getSupplyFree(obs)/20, self.justSelectWorker]])

        #Reset justSelectWorker variable now that it has been read
        self.justSelectWorker = -1

        # </editor-fold>
        # <editor-fold> desc="Things that should happen on first frame only"
        if obs.first():
            #Currently saves the first state and do no_op.
            #Reason behind this is that the learning requires info on a state and the following state
            #And because we can't know the future state before reaching it(easily anyways), might as well
            #use the last state and the current state instead.
            self.state = newState
            self.action = 0
            self.justSelectWorker = -1
            self.freeWorkersOld = 12
            self.nextSupplyNr = 0
            random.seed(1) # Use same random seed every time.
            return actions.FUNCTIONS.no_op()
        # </editor-fold>
        #<editor-fold> desc="Calculate reward"

        #reward = ((getSupplyWorkers(obs)-(getFreeWorkers(obs)*2))/50)#*(1)+getMinerals(obs)/5000)
        reward = (abs(self.freeWorkersOld - getFreeWorkers(obs)))*(0.5+getSupplyWorkers(obs)/50)
        self.freeWorkersOld = getFreeWorkers(obs)
        print (reward)
        #reward = self.justSelectWorker


        #</editor-fold>

        newAction = dqn_solver.act(newState) #Use network to get a new action

        # <editor-fold> desc="Learning stuff"
        global loadNetworkOnlyExploit
        if not loadNetworkOnlyExploit:
        #Save last state, last action, reward on this state, this state
        #Same as state,action,reward,nextState but backwards
            dqn_solver.remember(self.state,self.action,reward,newState,False)

            if obs.last():
                dqn_solver.remember(self.state,self.action,reward,None,True)

        #Save current state and action that will be taken so that it can
        #be used on the next frame.
        self.state = newState
        self.action = newAction

        #Memory playback, teach network using random previous frames.
        if not loadNetworkOnlyExploit:
            dqn_solver.experience_replay()
        # </editor-fold>



        # <editor-fold> desc="Action usage"
        if self.action == 4: # Build supply
            #x = random.randrange(30,50)
            #y = random.randrange(8,25)
            x = SUPPLY_LOCATIONS[self.nextSupplyNr][0]
            y = SUPPLY_LOCATIONS[self.nextSupplyNr][1]
            self.nextSupplyNr += 1
            if (self.nextSupplyNr >= len(SUPPLY_LOCATIONS)):
                self.nextSupplyNr = 0
            return actBuildSupplyDepot(obs, x, y)
        elif self.action == 3: # Order selected worker to mine
            minerals = [unit for unit in obs.observation.feature_units
                        if unit.unit_type == units.Neutral.MineralField]
            rMineral = random.choice(minerals)
            return actHarvestScreen(obs,rMineral.x,rMineral.y)
        elif self.action == 2: # Select worker
            self.justSelectWorker = 1
            return actSelectIdleWorker(obs)
            
        # Train worker
        posActions = [actions.FUNCTIONS.no_op(),actMultiTrainSCV(obs)]
        return posActions[self.action]
        # </editor-fold>

        return actions.FUNCTIONS.no_op() #Left here so things don't crash when changing action usage

savedNetworkScores = deque(maxlen=10)

def compareResultsAndSave(score):
    # Save network
    filePrefix="testNetwork"
    if(len(savedNetworkScores) == 0 or max(savedNetworkScores) < score):
        if len(savedNetworkScores) < savedNetworkScores.maxlen:
            savedNetworkScores.append(score)
            dqn_solver.save(filePrefix+str(score))
        else:
            poppedScore = savedNetworkScores.popleft()
            savedNetworkScores.append(score)

            os.remove(filePrefix+str(poppedScore)+'.h5')
            dqn_solver.save(filePrefix+str(score))
    print(savedNetworkScores)

def main(unused_argv):
    agent = MarineAgent()
    i = 0
    try:
        # <editor-fold> desc="Loop running game sessions"
        while True:
            i = i+1
            print(i)
            with sc2_env.SC2Env(
                    map_name="CollectMineralsAndGas",
                    players=[sc2_env.Agent(sc2_env.Race.terran)],
                    agent_interface_format=features.AgentInterfaceFormat(
                        feature_dimensions=features.Dimensions(screen=84, minimap=64), use_feature_units=True),
                    step_mul=16,
                    game_steps_per_episode=0,
                    visualize=False) as env:

                agent.setup(env.observation_spec(), env.action_spec())

                timesteps = env.reset()
                agent.reset()
                # <editor-fold> desc="Loop running the actual game, frame by frame"
                while True:
                    step_actions = [agent.step(timesteps[0])]
                    if timesteps[0].last():
                        break
                    timesteps = env.step(step_actions)
                # </editor-fold>
        #</editor-fold>

    except KeyboardInterrupt:
        pass

def getRandomWeightedIndex(list):
    total = 0
    for l in list:
        total += max(l, 0)
    rand = total * random.random()
    for i in range(0, len(list)):
        l = list[i]
        rand = rand - max(l, 0);
        if (rand <= 0.00001):
            return i;


if __name__ == "__main__":
    app.run(main)