from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
import random
import tensorflow as tf
import numpy as np

from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

from absl import app


GAMMA = 0.95
LEARNING_RATE = 0.001

MEMORY_SIZE = 1000000
BATCH_SIZE = 20

EXPLORATION_MAX = 1.0
EXPLORATION_MIN = 0.03
EXPLORATION_DECAY = 0.995

#Code for DQNSolver from https://github.com/gsurma/cartpole
class DQNSolver:

    def __init__(self, observation_space, action_space):
        self.exploration_rate = EXPLORATION_MAX

        self.action_space = action_space
        self.memory = deque(maxlen=MEMORY_SIZE)

        self.model = Sequential()
        self.model.add(Dense(24, input_shape=(observation_space,), activation="relu"))
        self.model.add(Dense(24, activation="relu"))
        self.model.add(Dense(self.action_space, activation="linear"))
        self.model.compile(loss="mse", optimizer=Adam(lr=LEARNING_RATE))

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


obsSpace = 4
actSpace = 5
dqn_solver = DQNSolver(obsSpace, actSpace)

#<editor-fold desc="Helper functions"
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
    i = 0
    state = None
    action = None
    justSelectWorker = -1

    def step(self, obs):
        super(MarineAgent, self).step(obs)
        global dqn_solver
        #This is the code that handles actions that require multiple steps, don't touch and leave at the top
        doingMultiAction = executeMultiAction(obs)
        if doingMultiAction != False:
            return doingMultiAction
        #End of multistep action code
        newState = np.array([[getMinerals(obs), getFreeWorkers(obs), getSupplyFree(obs), self.justSelectWorker]])

        #reward = ((getSupplyWorkers(obs)-(getFreeWorkers(obs)*1.2))/50)*(1+getMinerals(obs)/1000)
        reward = self.justSelectWorker
        self.justSelectWorker = -1

        newAction = dqn_solver.act(newState)
        if obs.first():
            self.state = newState
            self.action = newAction
            return actions.FUNCTIONS.no_op()


        print(reward)

        dqn_solver.remember(self.state,self.action,reward,newState,False)
        self.state = newState
        self.action = newAction

        dqn_solver.experience_replay()

        minerals = [unit for unit in obs.observation.feature_units
                    if unit.unit_type == units.Neutral.MineralField]

        if self.action == 4:
            x = random.randrange(1,83)
            y = random.randrange(1,83)
            return actBuildSupplyDepot(obs, x, y)
        elif self.action == 3:
            rMineral = random.choice(minerals)
            return actHarvestScreen(obs,rMineral.x,rMineral.y)
        elif self.action == 2:
            self.justSelectWorker = 1
            return actSelectIdleWorker(obs)

        posActions = [actions.FUNCTIONS.no_op(),actMultiTrainSCV(obs)]
        return posActions[self.action]


        return actions.FUNCTIONS.no_op()


def main(unused_argv):
    agent = MarineAgent()

    try:
        while True:
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

                while True:
                    step_actions = [agent.step(timesteps[0])]
                    if timesteps[0].last():
                        break
                    timesteps = env.step(step_actions)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    app.run(main)