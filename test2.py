from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
import random
import tensorflow as tf
import numpy as np
import os

from collections import deque
import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

from absl import app



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
EXPLORATION_MIN = 0.05
EXPLORATION_DECAY = 0.9999

loadNetworkOnlyExploit = False #TODO-----------------------------------------------------------Change this if you want to load a network that has already been trained.
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
            self.model.add(Dense(32, input_shape=(observation_space,), activation="relu", kernel_initializer=asd))
            self.model.add(Dense(16, activation="relu", kernel_initializer=asd))
            self.model.add(Dense(self.action_space, activation="linear", kernel_initializer=asd))
            self.model.compile(loss="logcosh", optimizer=Adam(lr=LEARNING_RATE))
        else:
            self.exploration_rate = 0
            self.model = keras.models.load_model("testNetwork4695.h5")          #TODO-----------------------------------------------------------Change this if you want to load another network that has already been trained.


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
obsSpace = 4
#Size of output /availble actions
actSpace = 5
#init of network
dqn_solver = DQNSolver(obsSpace, actSpace)

#</editor-fold>
#<editor-fold> desc="Helper functions"
# -------------------------------------Action Space-------------------------------------------------------------
# -------------------------------------Combined Actions---------------------------------------------------------
multiActions = []
def executeMultiAction(obs):
    if len(multiActions) > 0:
        return multiActions.pop()(obs) #pop returns the remove element, that's why this looks so weird
    else:
        return False

def actMultiTrainMarine(obs):
    #TODO: Add if statement that checks if barracks are already selected, if so: only do the training?
    global multiActions #Python bs to access outer scope
    multiActions = [actTrainMarine] #This should be in opposite order of execution, pop takes last element?
    return actSelectAllBarracks(obs)

def actMultiTrainSCV(obs):
    global multiActions
    multiActions = [actTrainSCV]
    return actSelectAllCommandCenters(obs)

#TODO: Test, requires vespene
def actMultiBuildBarrackReactor(obs):
    global multiActions
    multiActions = [actBuildReactor(obs)]
    return actSelectAllBarracks(obs)


#--------------------------------------"Smart" Actions---------------------------------------------------------
def smartSelectAllUnit(obs, unitType):
    #units.Terran.SCV
    allUnits = [unit for unit in obs.observation.feature_units if unit.unit_type == unitType]
    if len(allUnits) > 0:
        return actSelectPoint_selectAllType(obs, allUnits[0].x, allUnits[0].y)
    return actions.FUNCTIONS.no_op()

def smartSelectAddAllUnit(obs, unitType):
    #units.Terran.SCV
    allUnits = [unit for unit in obs.observation.feature_units if unit.unit_type == unitType]
    if len(allUnits) > 0:
        return actSelectPoint_addAllType(obs, allUnits[0].x, allUnits[0].y)
    return actions.FUNCTIONS.no_op()

def actSelectAllBarracks(obs):
    return smartSelectAllUnit(obs, units.Terran.Barracks)
def actSelectAllMarines(obs):
    return smartSelectAllUnit(obs, units.Terran.Marine)
def actSelectAllSCVs(obs):
    return smartSelectAllUnit(obs, units.Terran.SCV)
def actSelectAllCommandCenters(obs):
    return smartSelectAllUnit(obs, units.Terran.CommandCenter)

def actSelectAddAllBarracks(obs):
    return smartSelectAddAllUnit(obs, units.Terran.Barracks)
def actSelectAddAllMarines(obs):
    return smartSelectAddAllUnit(obs, units.Terran.Marine)
def actSelectAddAllSCVs(obs):
    return smartSelectAddAllUnit(obs, units.Terran.SCV)
def actSelectAddAllCommandCenters(obs):
    return smartSelectAddAllUnit(obs, units.Terran.CommandCenter)


# -------------------------------------Raw Actions-------------------------------------------------------------
def actBuildTechlab(obs): #TODO: Untested
    if actIsAvailable(obs, actions.FUNCTIONS.Build_Techlab_quick.id):
        return actions.FUNCTIONS.Build_Techlab_quick("now", [x,y])
    else:
        return actions.FUNCTIONS.no_op()

def actBuildReactor(obs): #TODO: Untested
    if actIsAvailable(obs, actions.FUNCTIONS.Build_Reactor_quick.id):
        return actions.FUNCTIONS.Build_Reactor_quick("now", [x,y])
    else:
        return actions.FUNCTIONS.no_op()

def actBuildNuke(obs): #TODO: Untested
    if actIsAvailable(obs, actions.FUNCTIONS.Build_Nuke_quick.id):
        return actions.FUNCTIONS.Build_Nuke_quick("now", [x,y])
    else:
        return actions.FUNCTIONS.no_op()

def actTrainWidowMine(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_WidowMine_quick.id):
        return actions.FUNCTIONS.Train_WidowMine_quick("now")
    else:
        return actions.FUNCTIONS.no_op()

def actTrainVikingFighter(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_VikingFighter_quick.id):
        return actions.FUNCTIONS.Train_VikingFighter_quick("now")
    else:
        return actions.FUNCTIONS.no_op()

def actTrainThor(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_Thor_quick.id):
        return actions.FUNCTIONS.Train_Thor_quick("now")
    else:
        return actions.FUNCTIONS.no_op()

def actTrainSiegeTank(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_SiegeTank_quick.id):
        return actions.FUNCTIONS.Train_SiegeTank_quick("now")
    else:
        return actions.FUNCTIONS.no_op()

def actTrainSCV(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_SCV_quick.id):
        return actions.FUNCTIONS.Train_SCV_quick("now")
    else:
        return actions.FUNCTIONS.no_op()


def actTrainReaper(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_Reaper_quick.id):
        return actions.FUNCTIONS.Train_Reaper_quick("now")
    else:
        return actions.FUNCTIONS.no_op()

def actTrainRaven(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_Raven_quick.id):
        return actions.FUNCTIONS.Train_Raven_quick("now")
    else:
        return actions.FUNCTIONS.no_op()

def actTrainMedivac(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_Medivac_quick.id):
        return actions.FUNCTIONS.Train_Medivac_quick("now")
    else:
        return actions.FUNCTIONS.no_op()

def actTrainMarauder(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_Marauder_quick.id):
        return actions.FUNCTIONS.Train_Marauder_quick("now")
    else:
        return actions.FUNCTIONS.no_op()

def actTrainLiberator(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_Liberator_quick.id):
        return actions.FUNCTIONS.Train_Liberator_quick("now")
    else:
        return actions.FUNCTIONS.no_op()

def actTrainHellion(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_Hellion_quick.id):
        return actions.FUNCTIONS.Train_Hellion_quick("now")
    else:
        return actions.FUNCTIONS.no_op()


def actTrainHellbat(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_Hellbat_quick.id):
        return actions.FUNCTIONS.Train_Hellbat_quick("now")
    else:
        return actions.FUNCTIONS.no_op()

def actTrainGhost(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_Ghost_quick.id):
        return actions.FUNCTIONS.Train_Ghost_quick("now")
    else:
        return actions.FUNCTIONS.no_op()

def actTrainCyclone(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_Cyclone_quick.id):
        return actions.FUNCTIONS.Train_Cyclone_quick("now")
    else:
        return actions.FUNCTIONS.no_op()

def actTrainBattlecruiser(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_Battlecruiser_quick.id):
        return actions.FUNCTIONS.Train_Battlecruiser_quick("now")
    else:
        return actions.FUNCTIONS.no_op()

def actTrainBanshee(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_Banshee_quick.id):
        return actions.FUNCTIONS.Train_Banshee_quick("now")
    else:
        return actions.FUNCTIONS.no_op()



def actTrainMarine(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Train_Marine_quick.id):
        return actions.FUNCTIONS.Train_Marine_quick("now")
    else:
        return actions.FUNCTIONS.no_op()


def actBuildStarport(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Build_Starport_screen.id):
        return actions.FUNCTIONS.Build_Starport_screen("now", [x, y])
    else:
        return actions.FUNCTIONS.no_op()


def actBuildSensorTower(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Build_SensorTower_screen.id):
        return actions.FUNCTIONS.Build_SensorTower_screen("now", [x, y])
    else:
        return actions.FUNCTIONS.no_op()


def actBuildMissileTurret(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Build_MissileTurret_screen.id):
        return actions.FUNCTIONS.Build_MissileTurret_screen("now", [x, y])
    else:
        return actions.FUNCTIONS.no_op()


def actBuildGhostAcademy(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Build_GhostAcademy_screen.id):
        return actions.FUNCTIONS.Build_GhostAcademy_screen("now", [x, y])
    else:
        return actions.FUNCTIONS.no_op()


def actBuildFusionCore(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Build_FusionCore_screen.id):
        return actions.FUNCTIONS.Build_FusionCore_screen("now", [x,y])
    else:
        return actions.FUNCTIONS.no_op()

def actBuildFactory(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Build_Factory_screen.id):
        return actions.FUNCTIONS.Build_Factory_screen("now", [x,y])
    else:
        return actions.FUNCTIONS.no_op()

def actBuildCyberneticsCore(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Build_CyberneticsCore_screen.id):
        return actions.FUNCTIONS.Build_CyberneticsCore_screen("now", [x,y])
    else:
        return actions.FUNCTIONS.no_op()

def actBuildArmory(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Build_Armory_screen.id):
        return actions.FUNCTIONS.Build_Armory_screen("now", [x,y])
    else:
        return actions.FUNCTIONS.no_op()


def actBuildBunker(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Build_Bunker_screen.id):
        return actions.FUNCTIONS.Build_Bunker_screen("now", [x,y])
    else:
        return actions.FUNCTIONS.no_op()

def actBuildCommandCenter(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Build_CommandCenter_screen.id):
        return actions.FUNCTIONS.Build_CommandCenter_screen("now", [x,y])
    else:
        return actions.FUNCTIONS.no_op()

def actBuildEngineeringBay(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Build_EngineeringBay_screen.id):
        return actions.FUNCTIONS.Build_EngineeringBay_screen("now", [x,y])
    else:
        return actions.FUNCTIONS.no_op()

def actBuildRefinery(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Build_Refinery_screen.id):
        return actions.FUNCTIONS.Build_Refinery_screen("now", [x,y])
    else:
        return actions.FUNCTIONS.no_op()


def actBuildBarracks(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Build_Barracks_screen.id):
        return actions.FUNCTIONS.Build_Barracks_screen("now", [x,y])
    else:
        return actions.FUNCTIONS.no_op()

def actBuildSupplyDepot(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Build_SupplyDepot_screen.id):
        return actions.FUNCTIONS.Build_SupplyDepot_screen("now", [x,y])
    else:
        return actions.FUNCTIONS.no_op()

#TODO: Untested
def actCancel(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Cancel_quick.id):
        return actions.FUNCTIONS.Cancel_quick()
    else:
        return actions.FUNCTIONS.no_op()

#I have no idea what this does, nor when it is available.
#def actSmartScreen(obs, x, y):
#    if actIsAvailable(obs, actions.FUNCTIONS.Smart_screen.id):
#        return actions.FUNCTIONS.smart_screen([x,y])
#    else:
#        return actions.FUNCTIONS.no_op()


def actSelectPoint(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.select_point.id):
        return actions.FUNCTIONS.select_point("select", [x,y])
    else:
        return actions.FUNCTIONS.no_op()

#TODO: 'Sub' functions of actSelectPoint haven't been tested.
def actSelectPoint_toggle(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.select_point.id):
        return actions.FUNCTIONS.select_point("toggle", [x,y])
    else:
        return actions.FUNCTIONS.no_op()
def actSelectPoint_selectAllType(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.select_point.id):
        return actions.FUNCTIONS.select_point("select_all_type", [x, y])
    else:
        return actions.FUNCTIONS.no_op()
def actSelectPoint_addAllType(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.select_point.id):
        return actions.FUNCTIONS.select_point("add_all_type", [x, y])
    else:
        return actions.FUNCTIONS.no_op()


def actHarvestScreen(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Harvest_Gather_screen.id):
        return actions.FUNCTIONS.Harvest_Gather_screen("now",(x,y))
    else:
        return actions.FUNCTIONS.no_op()

def actStopQuick(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.Stop_quick.id):
        return actions.FUNCTIONS.Stop_quick("now")
    else:
        return actions.FUNCTIONS.no_op()

def actMoveCamera(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.move_camera.id):
        return actions.FUNCTIONS.move_camera([x,y])
    else:
        return actions.FUNCTIONS.no_op()

def actMoveMinimap(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Move_minimap.id):
        return actions.FUNCTIONS.Move_minimap("now", (x, y))
    else:
        return actions.FUNCTIONS.no_op()

def actMoveScreen(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Move_screen.id):
        return actions.FUNCTIONS.Move_screen("now", (x, y))
    else:
        return actions.FUNCTIONS.no_op()

def actAttackScreen(obs, x, y):
    if actIsAvailable(obs, actions.FUNCTIONS.Attack_screen.id):
        return actions.FUNCTIONS.Attack_screen("now", (x, y))
    else:
        return actions.FUNCTIONS.no_op()

def actAttackMinimap(obs,x,y):
    if actIsAvailable(obs, actions.FUNCTIONS.Attack_minimap.id):
        # This only works if there is ground (for ground units at least), otherwise seems to noop?
        return actions.FUNCTIONS.Attack_minimap("now", (x,y))
    else:
        return actions.FUNCTIONS.no_op()


# -------------------------------------Helper Functions---------------------------------------------------------
# Returns True if the action is currently available, use this to avoid activating
# actions that aren't allowed and crashing the agent.
def actIsAvailable(obs, action):
    if action in obs.observation.available_actions:
        return True
    return False


def executeMultistepAction():
    return False  # TODO: Implement, put all logic for


def numberToPoint(number, numberRepresentingOrigin, areaWidth, areaHeight):
    shiftedNumber = (number - numberRepresentingOrigin)
    height = shiftedNumber // areaHeight  # // Is apparently integer division
    width = shiftedNumber % areaWidth
    return width, height  # TODO: Handle heights that are out of bounds


# -------------------------------------Input Space--------------------------------------------------------------
# -------------------------------------SCREEN DATA GET FUNCTIONS------------------------------------------------
# These return a 2d array of bytes, where the bytes represent different things
# Getters for creep(zerg only), power(protoss only), shields(protoss only)
def getHeightMinimap(obs):
    return obs.observation.feature_minimap.height_map


def getVisiblityMinimap(obs):
    return obs.observation.feature_minimap.visibility_map


def getCameraMinimap(obs):
    return obs.observation.feature_minimap.camera


# Returns relative faction to player, 1 = player unit, 2 = hostile?, 3 = neutral, 0 = no unit
def getFactionsMinimap(obs):
    return obs.observation.feature_minimap.player_relative


# Returns true player numbers, compared to the relative version above.
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


# Anti-aliased version of density
def getDensityAAScreen(obs):
    return obs.observation.feature_screen.unit_density_aa


# This is probably aoes, anyways
def getAOEsScreen(obs):
    return obs.observation.feature_screen.effects


# --------------------------------------END SCREEN GETS-------------------------------
# --------------------------------------Numeric Value Inputs--------------------------
def getMinerals(obs):
    return obs.observation.player.minerals


def getGas(obs):
    return obs.observation.player.vespene


def getSupply(obs):
    return obs.observation.player.food_used


def getSupplyMax(obs):
    return obs.observation.player.food_cap


# Returns difference between current and max, maybe used
def getSupplyFree(obs):
    return getSupplyMax(obs) - getSupply(obs)


def getSupplyWorkers(obs):
    return obs.observation.player.food_workers


def getSupplyArmy(obs):
    return obs.observation.player.food_army


def getPlayerID(obs):
    return obs.observation.player.player_id


# -----------------------------------END NUMERIC INPUTS-------------------------------
# -----------------------------------END INPUT SPACE----------------------------------
#</editor-fold>
def getFreeWorkers(obs):
    return obs.observation.player.idle_worker_count

def actSelectIdleWorker(obs):
    if actIsAvailable(obs, actions.FUNCTIONS.select_idle_worker.id):
        return actions.FUNCTIONS.select_idle_worker("select")
    else:
        return actions.FUNCTIONS.no_op()

class MarineAgent(base_agent.BaseAgent):
    state = None
    action = None
    justSelectWorker = -1
    freeWorkersOld = 12

    def step(self, obs):
        super(MarineAgent, self).step(obs)
        global dqn_solver #Let python access the global variable dqn_solver
        if obs.last():
            print(dqn_solver.exploration_rate)
            if dqn_solver.exploration_rate < 0.06:
                score = obs.observation.score_cumulative.collected_minerals
                compareResultsAndSave(score)

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
            return actions.FUNCTIONS.no_op()
        # </editor-fold>
        #<editor-fold> desc="Calculate reward"

        #reward = ((getSupplyWorkers(obs)-(getFreeWorkers(obs)*2))/50)#*(1)+getMinerals(obs)/5000)
        reward = (abs(self.freeWorkersOld - getFreeWorkers(obs)))*(0.5+getSupplyWorkers(obs)/50)
        self.freeWorkersOld = getFreeWorkers(obs)
        #print (reward)
        #reward = self.justSelectWorker


        #</editor-fold>


        newAction = dqn_solver.act(newState) #Use network to get a new action

        # <editor-fold> desc="Learning stuff"
        global loadNetworkOnlyExploit
        if not loadNetworkOnlyExploit:
        #Save last state, last action, reward on this state, this state
        #Same as state,action,reward,nextState but backwards
            dqn_solver.remember(self.state,self.action,reward,newState,False)

        #Save current state and action that will be taken so that it can
        #be used on the next frame.
        self.state = newState
        self.action = newAction

        #Memory playback, teach network using random previous frames.
        if not loadNetworkOnlyExploit:
            dqn_solver.experience_replay()
        # </editor-fold>



        # <editor-fold> desc="Action usage"
        if self.action == 4:
            x = random.randrange(30,50)
            y = random.randrange(8,25)
            return actBuildSupplyDepot(obs, x, y)
        elif self.action == 3:
            minerals = [unit for unit in obs.observation.feature_units
                        if unit.unit_type == units.Neutral.MineralField]
            rMineral = random.choice(minerals)
            return actHarvestScreen(obs,rMineral.x,rMineral.y)
        elif self.action == 2:
            self.justSelectWorker = 1
            return actSelectIdleWorker(obs)

        posActions = [actions.FUNCTIONS.no_op(),actMultiTrainSCV(obs)]
        return posActions[self.action]
        # </editor-fold>

        return actions.FUNCTIONS.no_op() #Left here so things don't crash when changing action usage

savedNetworkScores = deque(maxlen=10)

def compareResultsAndSave(score):
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

        print("\n------- Network Scores -------")
        print(savedNetworkScores)
        print("------------------------------\n")

def main(unused_argv):
    agent = MarineAgent()
    i = 0
    try:
        # <editor-fold> desc="Loop running game sessions"
        while True:
            i = i+1
            print("Iteration " + str(i))
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


if __name__ == "__main__":
    app.run(main)