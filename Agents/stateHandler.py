import pymongo
import pickle
import numpy as np
import random
from google.protobuf.json_format import ParseDict
import sys
from simpleSC2API import *
import keras
import time

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
statesCursor = states.find()
scores.create_index([("replay_name", pymongo.ASCENDING), ("frame_id", pymongo.ASCENDING)])
statesLength = states.find().count()


class DataGenerator(keras.utils.Sequence):
    def __init__(self, stateCount = statesLength, batchSize = 30):
        self.stateCount = stateCount
        self.batchSize = batchSize

        self.indexes = np.arange(self.stateCount)
        np.random.shuffle(self.indexes)

    def __len__(self):
        return self.stateCount//self.batchSize

    def on_epoch_end(self):
        self.indexes = np.arange(self.stateCount)
        np.random.shuffle(self.indexes)

    def transposeBatch(self, data):
        return (np.array([row[0] for row in data]), np.array([row[1] for row in data]), np.array([row[2] for row in data]))


    def data_generation(self, indexes):
        batch = []
        for i in indexes:
            temp = concatQueriedState(normalizeQueryState(queryStateByIndex(i)))
            if temp != None:
                batch.append(temp)

        numInput, target, input = self.transposeBatch(batch)
        input = np.moveaxis(input, 1, 3)

        return [numInput, input], target


    def __getitem__(self, batchNumber):
        indexes = self.indexes[batchNumber*self.batchSize:(batchNumber+1)*self.batchSize]
        x,y = self.data_generation(indexes)
        return x,y





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


#Given a list of replayIDs, returns a random state.
def queryRandomState(replayIDs):
    replayID = random.choice(replayIDs)
    frameID = randomViableFrame(replayID)
    playerID = random.choice([1,2])
    return concatQueriedState(normalizeQueryState(queryState(replayID, frameID, playerID)))

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

#Changes values so that they are between the range [0,1], with the exception of things like minerals
#which can go past 1.
def normalizeQueryState(data):
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

#Returns (numericData, imageData)
def getIngameNormalisedState(obs):
    return concatIngameState(normalizeQueryState(readIngameState(obs)))

#Reads the same data from given observation that is read from mongodb
#with queryState.
def readIngameState(obs):
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
    frameID = getFrame(obs)[0]

    concMinimap = np.array([miniFactions, miniVision, miniSelected])
    concScreen = np.array([screenFactions, screenVision, screenSelected, screenHp, screenUnits, screenHeight])
    concRaw = np.array([frameID, minerals, vespene, supTotal, supUsed, supArmy, supWorkers])

    return [concRaw, concMinimap, concScreen]

#Packages data from mongodb in a way that makes it easier to use with keras
#Returns (numericData, winLoss, imageData)
def concatQueriedState(data):
    #   concMinimap = np.array([miniFactions,miniVision,miniSelected])
    #   concScreen = np.array([screenFactions, screenVision, screenSelected, screenHp, screenUnits, screenHeight])
    #   concRaw = np.array([frameID, minerals,vespene,supTotal,supUsed,supArmy,supWorkers])
    #   (concRaw, concMinimap, concScreen, winLoss)
    if data != None:
        return (data[0], data[3], np.concatenate((data[1],data[2])))

#Given [numeric, minimap, screen] data, returns
#(numeric, minimap&screen), concatenates minimap and screen
def concatIngameState(data):
    return (data[0], np.concatenate((data[1],data[2])))

#Queries mongoDB for the given state.
def queryStateByIndex(index):

    startTime = time.time()
    print("S: "+str(startTime))

    state = states.find()[index.item()]

    print(time.time()-startTime)

    replayID = state["replay_name"]
    playerID = state["player_id"]
    frameID = state["frame_id"]

    playerState = players.find({'replay_name': replayID, 'player_id': playerID})
    winLoss = 0
    for playerdata in playerState:
        winLoss = playerdata["result"]
    # Minimap data
    miniFactions = pickle.loads(state["minimap"]["factions"])
    miniVision = pickle.loads(state["minimap"]["vision"])
    miniSelected = pickle.loads(state["minimap"]["selected"])
    # Screen data
    screenFactions = pickle.loads(state["screen"]["factions"])
    screenVision = pickle.loads(state["screen"]["vision"])
    screenSelected = pickle.loads(state["screen"]["selected"])
    screenHp = pickle.loads(state["screen"]["hp"])
    screenUnits = pickle.loads(state["screen"]["units"])
    screenHeight = pickle.loads(state["screen"]["height"])
    # Raw data
    minerals = state["resources"]["minerals"]
    vespene = state["resources"]["vespene"]
    supTotal = state["supply"]["total"]
    supUsed = state["supply"]["used"]
    supArmy = state["supply"]["army"]
    supWorkers = state["supply"]["workers"]
    # FrameID
    concMinimap = np.array([miniFactions, miniVision, miniSelected])
    concScreen = np.array([screenFactions, screenVision, screenSelected, screenHp, screenUnits, screenHeight])
    concRaw = np.array([frameID, minerals, vespene, supTotal, supUsed, supArmy, supWorkers])

    return [concRaw, concMinimap, concScreen, winLoss]

def queryState(replayID, frameID, playerID):
    state = states.find({'replay_name':replayID, 'frame_id':frameID, 'player_id':playerID})

    playerState = players.find({'replay_name':replayID, 'player_id':playerID})
    winLoss = 0
    for data in playerState:
        winLoss = data["result"]

    #Returns first point of data (should only be one anyways), if it exists.
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
    #This is reached if there is no data for the given replay, player and frame.
    #This occurs at times due to sc2reaper not having saved frames all the way
    #up to the "game_duration_loops" amount.
    print("____Failed at finding frame____")
    print(replayID)
    print(frameID)
    print(playerID)

# print((db.states.find().count()))
# print(queryStateByIndex(100))
# exit()
