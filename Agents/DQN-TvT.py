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
        (60, 8),
        (60, 12),
        (60, 18),
        (60, 24)
    ]
BARRACK_LOCATIONS = [(30, 50), (40, 50), (50, 50)]

BASE_LOCATIONS_MINI = [(16,24), (42,24), (22,40),(48,40)]

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
EXPLORATION_MIN = 0.1
EXPLORATION_DECAY = 0.999996
DIMENSIONS = 64
GAMESTEPS = 15000

initAPI(DIMENSIONS,DIMENSIONS,DIMENSIONS,DIMENSIONS)

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
        return np.argmax(q_values[0])

    def experience_replay(self):
        if len(self.memory) < BATCH_SIZE:
            return
        batch = random.sample(self.memory, BATCH_SIZE)
        for state, action, reward, state_next, terminal in batch:
            q_update = reward
            if not terminal:
                q_update = (reward + GAMMA * np.amax(self.model.predict(state_next)[0]))

            q_values = self.model.predict(state)
            q_values[0][action] = q_update
            self.model.fit(state, q_values, verbose=0)
        self.exploration_rate *= EXPLORATION_DECAY
        self.exploration_rate = max(EXPLORATION_MIN, self.exploration_rate)

    def save(self, name):
        self.model.save(name+'.h5')

#Size of input
obsSpace = 12
#Size of output /availble actions
actSpace = 12
#init of network
dqn_solver = DQNSolver(obsSpace, actSpace)




class MarineAgent(base_agent.BaseAgent):
    state = None
    action = None
    nextSupplyNr = 0
    nextBarrackNr = 0
    stepCounter = 0
    oldReward = 0
    oldBarracks = 0
    oldSupplyDepots = 0
    oldIdleWorkerTime = 0
    oldIdleProductionTime = 0

    workSupp = 0
    armySupp = 0
    barracks = 0
    supplyDepots = 0

    baseX = 0
    baseY = 0

    def step(self, obs):
        super(MarineAgent, self).step(obs)
        global dqn_solver #Let python access the global variable dqn_solver
        global stepCounter
        stepCounter += 1
        if obs.last():
            print(dqn_solver.exploration_rate)
            score = stepCounter
            global EXPLORATION_MIN
            if dqn_solver.exploration_rate <= EXPLORATION_MIN * 2:
                compareResultsAndSave(score)
            # Log score to file
            t1 = time() - trainingStartTime
            logFile = open(timestamp + ".log","a+")
            logFile.write("score=%4d, explore=%.4f, time=%7ds, steps=%8d, supplyWorkers=%3d, supplyArmy=%3d, totalUnits=%4d, totalUnitsKilled=%5d, totalStructuresKilled=%5d, idleWorkerTime=%5d, idleProductionTime=%5d\n" % (score, dqn_solver.exploration_rate, t1, stepCounter, getSupplyWorkers(obs), getSupplyArmy(obs), getCumulativeUnits(obs), getCumulativeUnitsKilledValue(obs), getCumulativeStructuresKilledValue(obs), getIdleWorkerTime(obs), getIdleProductionTime(obs)))
            logFile.close()

        # <editor-fold> desc="Multistep action stuff, leave it alone"
        #This is the code that handles actions that require multiple steps, don't touch and leave at the top
        doingMultiAction = executeMultiAction(obs)
        if doingMultiAction != False:
            return doingMultiAction
        #</editor-fold>
        # <editor-fold> desc="Read game data / input, handle it"
        newState = np.array([[(min(getMinerals(obs),150)-75)/75, getFreeWorkers(obs)/2,
                              getSupplyFree(obs)/20, getSupplyArmy(obs)/20,
                              getSupplyWorkers(obs)/20, getSelectSCVCount(obs)/20,
                              getSelectMarineCount(obs)/20, getBarrackCount(obs)/3,
                              getSupplyDepotCount(obs)/4, getMarineCount(obs)/20,
                              getSCVCount(obs)/20, (self.baseX-20)/20]])

        # </editor-fold>
        # <editor-fold> desc="Things that should happen on first frame only"
        if obs.first():
            #Cred to https://itnext.io/build-a-zerg-bot-with-pysc2-2-0-295375d2f58e  for spawn location code
            player_y, player_x = (obs.observation.feature_minimap.player_relative ==
                                  features.PlayerRelative.SELF).nonzero()
            self.baseX = round(player_x.mean())
            self.baseY = round(player_y.mean())

            global SUPPLY_LOCATIONS, BARRACK_LOCATIONS
            if self.baseX < 30: #Spawn top left
                SUPPLY_LOCATIONS = [(60, 8),(60, 12),(60, 18),(60, 24)]
                BARRACK_LOCATIONS = [(30, 50), (40, 50), (50, 50)]
                self.baseX = 20
                self.baseY = 24
            else: #Spawn bottom right, use opposite locations
                SUPPLY_LOCATIONS = [(4, 56),(4, 52),(4, 48),(4, 44)]
                BARRACK_LOCATIONS = [(34, 14), (24, 14), (14, 14)]
                self.baseX = 40
                self.baseY = 46

            #Currently saves the first state and do no_op.
            #Reason behind this is that the learning requires info on a state and the following state
            #And because we can't know the future state before reaching it(easily anyways), might as well
            #use the last state and the current state instead.
            self.state = newState
            self.action = 0
            self.nextSupplyNr = 0
            self.nextBarrackNr = 0
            self.stepCounter = 0
            self.workSupp = getSupplyWorkers(obs)
            self.marineOld = getSupplyArmy(obs)
            self.barracks = 0
            self.supplyDepots = 0
            self.oldReward = 0
            self.oldBarracks = 0
            self.oldSupplyDepots = 0
            self.oldIdleWorkerTime = 0
            self.oldIdleProductionTime = 0
            #random.seed(1) # Use same random seed every time.
            return actions.FUNCTIONS.no_op()
        # </editor-fold>
        #<editor-fold> desc="Calculate reward"
        armySupp = getSupplyArmy(obs)
        workSupp = getSupplyWorkers(obs)
        idleWorkerTime = getIdleWorkerTime(obs)
        idleProductionTime = getIdleProductionTime(obs)
        reward = (armySupp - self.armySupp)/10 + (workSupp - self.workSupp) / 15 + (self.supplyDepots - self.oldSupplyDepots) + (self.barracks - self.oldBarracks) - min(1, (idleWorkerTime - self.oldIdleWorkerTime) / 10) - min(1, (idleProductionTime - self.oldIdleProductionTime) / 10) + self.oldReward * 0.7
        
        #print(str(idleWorkerTime - self.oldIdleWorkerTime) + ", " + str(idleProductionTime - self.oldIdleProductionTime))
        
        self.armySupp = armySupp
        self.workSupp = workSupp
        self.oldSupplyDepots = self.supplyDepots
        self.oldBarracks = self.barracks
        self.oldReward = reward
        self.oldIdleWorkerTime = idleWorkerTime
        self.oldIdleProductionTime = idleProductionTime
        print("%.4f" % (reward))
        #</editor-fold>

        newAction = dqn_solver.act(newState) #Use network to get a new action

        # <editor-fold> desc="Learning stuff"
        global loadNetworkOnlyExploit
        if not loadNetworkOnlyExploit:
        #Save last state, last action, reward on this state, this state
        #Same as state,action,reward,nextState but backwards
            dqn_solver.remember(self.state,self.action,reward,newState,False)

            if obs.last():
                #Big negative reward for losing early
                endReward = (stepCounter-GAMESTEPS+500)/2000
                print("End Reward: "+ str(endReward))
                dqn_solver.remember(self.state,self.action, endReward,None,True)

        #Save current state and action that will be taken so that it can
        #be used on the next frame.
        self.state = newState
        self.action = newAction

        #Memory playback, teach network using random previous frames.
        if not loadNetworkOnlyExploit:
            dqn_solver.experience_replay()
        # </editor-fold>
        stepCounter += 1
        # <editor-fold> desc="Action usage"
        if self.action == 12:
            return actMultiTrainMarine(obs)
        if self.action == 11:
            x = BASE_LOCATIONS_MINI[0][0]
            y = BASE_LOCATIONS_MINI[0][1]
            return actAttackMinimap(obs, x, y)
        if self.action == 10:
            x = BASE_LOCATIONS_MINI[1][0]
            y = BASE_LOCATIONS_MINI[1][1]
            return actAttackMinimap(obs, x, y)
        if self.action == 9:
            x = BASE_LOCATIONS_MINI[2][0]
            y = BASE_LOCATIONS_MINI[2][1]
            return actAttackMinimap(obs, x, y)
        if self.action == 8:
            x = BASE_LOCATIONS_MINI[3][0]
            y = BASE_LOCATIONS_MINI[3][1]
            return actAttackMinimap(obs, x, y)
        if self.action == 7: #Add select all SCVs
            return actSelectAddAllSCVs(obs)
        if self.action == 6: #Select marines
            return actSelectAllMarines(obs)
        if self.action == 5: #Build barracks
            x = BARRACK_LOCATIONS[self.nextBarrackNr][0]
            y = BARRACK_LOCATIONS[self.nextBarrackNr][1]
            self.nextBarrackNr += 1
            self.barracks += 1
            if (self.nextBarrackNr >= len(BARRACK_LOCATIONS)):
                self.nextBarrackNr = 0
            return actBuildBarracks(obs, x, y)
        if self.action == 4: # Build supply
            x = SUPPLY_LOCATIONS[self.nextSupplyNr][0]
            y = SUPPLY_LOCATIONS[self.nextSupplyNr][1]
            self.nextSupplyNr += 1
            if (self.nextSupplyNr >= len(SUPPLY_LOCATIONS)):
                self.nextSupplyNr = 0
            return actBuildSupplyDepot(obs, x, y)
        elif self.action == 3: # Order selected worker to mine
            minerals = [unit for unit in obs.observation.feature_units
                        if unit.unit_type == units.Neutral.MineralField]
            if len(minerals) < 1:
                return actions.FUNCTIONS.no_op()
            rMineral = random.choice(minerals)
            return actHarvestScreen(obs,rMineral.x,rMineral.y)
        elif self.action == 2: # Select worker
            return actSelectIdleWorker(obs)

        # Train worker
        posActions = [actMoveCamera(obs, self.baseX, self.baseY),actMultiTrainSCV(obs)]
        return posActions[self.action]
        # </editor-fold>

        return actions.FUNCTIONS.no_op() #Left here so things don't crash when changing action usage

savedNetworkScores = deque(maxlen=10)

def compareResultsAndSave(score):
    # Save network
    filePrefix="marineNetwork"
    #if(len(savedNetworkScores) == 0 or max(savedNetworkScores) < score):
    #    if len(savedNetworkScores) < savedNetworkScores.maxlen:
    #        savedNetworkScores.append(score)
    #        dqn_solver.save(filePrefix+str(score))
    #    else:
    #        poppedScore = savedNetworkScores.popleft()
    #        savedNetworkScores.append(score)

    #        os.remove(filePrefix+str(poppedScore)+'.h5')
    #        dqn_solver.save(filePrefix+str(score))
    dqn_solver.save(filePrefix+str(datetime.datetime.now().strftime("%Y-%m-%d-%H.%M.%S")))
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
                    map_name="Simple64",
                    players=[sc2_env.Agent(sc2_env.Race.terran),
                             sc2_env.Bot(sc2_env.Race.terran,
                                         sc2_env.Difficulty.very_easy)],
                    agent_interface_format=features.AgentInterfaceFormat(
                        feature_dimensions=features.Dimensions(screen=DIMENSIONS, minimap=DIMENSIONS), use_feature_units=True),
                    step_mul=16,
                    game_steps_per_episode=GAMESTEPS,
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
