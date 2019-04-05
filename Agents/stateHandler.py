import pymongo
import pickle
import numpy as np
import random
from google.protobuf.json_format import ParseDict
import sys
from simpleSC2API import *

client = pymongo.MongoClient()
db = client["replay_database"]
replays = db["replays"]
players = db["players"]
states = db["states"]
scores = db["scores"]


#This is the amount of frames between each saved data point in the DB
#If nothing is returned from the DB (and it is running) then this might be wrong.
framesPerStep = 12

validationCount = 12 #The amount of replays that should be used only for validation

np.set_printoptions(precision=20,threshold=sys.maxsize)   #Uncomment if you want to print entire np arrays.


replays.create_index("replay_name")
players.create_index("replay_name")
#This sorts the database I believe, so it might take some time to run these lines when running this for the first time.
states.create_index([("replay_name", pymongo.ASCENDING), ("frame_id", pymongo.ASCENDING)])
scores.create_index([("replay_name", pymongo.ASCENDING), ("frame_id", pymongo.ASCENDING)])


#Initialize trainingReplay_ids as all replay_ids.
trainingReplay_ids = []
validationReplay_ids = []
for replay_doc in replays.find():
    trainingReplay_ids.append(replay_doc["replay_name"])
#Randomize the list
random.shuffle(trainingReplay_ids)
#Move some (at random due to shuffle) to the validation set instead
for i in range (0,validationCount):
    validationReplay_ids.append(trainingReplay_ids.pop())



def queryRandomState(replayIDs):
    replayID = random.choice(replayIDs)
    frameID = randomViableFrame(replayID)
    playerID = random.choice([1,2])
    return normalizeQueryState(queryState(replayID, frameID, playerID))
def getRandomTrainingState():
    return queryRandomState(trainingReplay_ids)
def getRandomValidationState():
    return queryRandomState(validationReplay_ids)

def randomViableFrame(replayID):
    maxFrames = 0
    for replay in replays.find({"replay_name":replayID}):
        maxFrames = replay["game_duration_loops"]
        maxFrames = maxFrames-120-maxFrames*0.005 #maxFrames is sometimes larger than (amount of recorded frames)*12, causing it to access data that doesn't exist
        break;
    frameID = framesPerStep*(random.randint(0, maxFrames//framesPerStep))
    return frameID

def normalizeQueryState(data):
    #dataf = data[2].astype(float)
    #print(np.true_divide(data[2][3].astype(float),3))
    #exit()
    if data is None:
        return
    data[0] = data[0].astype(float)
    data[1] = data[1].astype(float)
    data[2] = data[2].astype(float)
    data[0][0] = np.true_divide(data[0][0],20000)
    data[0][1] = np.true_divide(data[0][1],5000)
    data[0][2] = np.true_divide(data[0][2],5000)
    data[0][3] = np.true_divide(data[0][3],200)
    data[0][4] = np.true_divide(data[0][4],200)
    data[0][5] = np.true_divide(data[0][5],200)
    data[0][6] = np.true_divide(data[0][6],200)

    data[1][0] = np.true_divide(data[1][0],4)
    data[1][1] = np.true_divide(data[1][1],2)
    data[2][0] = np.true_divide(data[2][0],3)
    data[2][1] = np.true_divide(data[2][1],2)
    data[2][3] = np.true_divide(data[2][3],3)
    data[2][4] = np.true_divide(data[2][4],2000)
    data[2][5] = np.true_divide(data[2][5],255)
    return data

def getIngameNormalisedState(obs):
    return normalizeQueryState(getIngameState(obs))

def getIngameState(obs):
    miniFactions = getFactionsMinimap(obs)
    miniVision = getVisiblityMinimap(obs)
    miniSelected = getSelectedMinimap(obs)
    # Screen data
    screenFactions = getFactionsScreen(obs)
    screenVision = getVisibilityScreen(obs)
    screenSelected = getSelectedScreen(obs)
    screenHp = getHPScreen(obs)
    screenUnits = getUnitsScreen(obs)
    screenHeight = getHeightScreen(obs)
    # Raw data
    minerals = getMinerals(obs)
    vespene = getGas(obs)
    supTotal = getSupplyMax(obs)
    supUsed = getSupply(obs)
    supArmy = getSupplyArmy(obs)
    supWorkers = getSupplyWorkers(obs)
    frameID = getTimestep(obs)[0]
    # FrameID
    concMinimap = np.array([miniFactions, miniVision, miniSelected])
    concScreen = np.array([screenFactions, screenVision, screenSelected, screenHp, screenUnits, screenHeight])
    concRaw = np.array([frameID, minerals, vespene, supTotal, supUsed, supArmy, supWorkers])

    return [concRaw, concMinimap, concScreen]


def queryState(replayID, frameID, playerID):
    state = states.find({'replay_name':replayID, 'frame_id':frameID, 'player_id':playerID})
    #Unsure how this data structure looks, but this should pick out the first (should be only)
    #data thing, if it exists.

    playerState = players.find({'replay_name':replayID, 'player_id':playerID})
    winLoss = 0
    for data in playerState:
        winLoss = data["result"]

    for data in state:
        # Minimap data
        miniFactions = pickle.loads(data["minimap"]["factions"])
        miniVision = pickle.loads(data["minimap"]["vision"])
        miniSelected = pickle.loads(data["minimap"]["selected"])
        # Screen data
        screenFactions = pickle.loads(data["screen"]["factions"])
        screenVision = pickle.loads(data["screen"]["vision"])
        screenSelected = pickle.loads(data["screen"]["selected"])
        screenHp = pickle.loads(data["screen"]["hp"])
        screenUnits = pickle.loads(data["screen"]["units"])
        screenHeight = pickle.loads(data["screen"]["height"])
        # Raw data
        minerals = data["resources"]["minerals"]
        vespene = data["resources"]["vespene"]
        supTotal = data["supply"]["total"]
        supUsed = data["supply"]["used"]
        supArmy = data["supply"]["army"]
        supWorkers = data["supply"]["workers"]
        #FrameID
        concMinimap = np.array([miniFactions,miniVision,miniSelected])
        concScreen = np.array([screenFactions, screenVision, screenSelected, screenHp, screenUnits, screenHeight])
        concRaw = np.array([frameID, minerals,vespene,supTotal,supUsed,supArmy,supWorkers])

        return [concRaw, concMinimap, concScreen, winLoss]
    print("____Failed at finding frame____")
    print(replayID)
    print(frameID)
    print(playerID)

#print(queryState(replay_ids[0],12,1))
#for replay_doc in replays.find():
#    print(pickle.loads(replay_doc["map"]["minimap"]["height"]))

#for replay_id in replay_ids:
#    cursor = states.find({'replay_id':replay_id, 'player_id': 1, 'frame_id': 12})
#    for state_doc in cursor:
#        a = pickle.loads(state_doc["screen"]["units"])
#        print(a)
        #print(pickle.loads(state_doc["screen"]["factions"]))


#states.find()