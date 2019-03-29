import pymongo
import pickle
import numpy as np
from google.protobuf.json_format import ParseDict
import sys

client = pymongo.MongoClient()
db = client["replay_database"]
replays = db["replays"]
players = db["players"]
states = db["states"]
scores = db["scores"]


#This is the amount of frames between each saved data point in the DB
#If nothing is returned from the DB (and it is running) then this might be wrong.
framesPerStep = 12


#np.set_printoptions(threshold=sys.maxsize)


replays.create_index("replay_id")
players.create_index("replay_id")
states.create_index([("replay_id", pymongo.ASCENDING), ("frame_id", pymongo.ASCENDING)])
scores.create_index([("replay_id", pymongo.ASCENDING), ("frame_id", pymongo.ASCENDING)])

replay_ids = []
for replay_doc in replays.find({}, {"replay_id": 1}):
    replay_ids.append(replay_doc["replay_id"])
    print(replay_doc["replay_id"])

def queryState(replayID, frameID, playerID):
    state = states.find({'replay_id':replayID, 'frame_id':frameID, 'player_id':playerID})
    #Unsure how this data structure looks, but this should pick out the first (should be only)
    #data thing, if it exists.
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

        return (concRaw, concMinimap, concScreen)

print(queryState(replay_ids[0],12,1))
#for replay_doc in replays.find():
#    print(pickle.loads(replay_doc["map"]["minimap"]["height"]))

#for replay_id in replay_ids:
#    cursor = states.find({'replay_id':replay_id, 'player_id': 1, 'frame_id': 12})
#    for state_doc in cursor:
#        a = pickle.loads(state_doc["screen"]["units"])
#        print(a)
        #print(pickle.loads(state_doc["screen"]["factions"]))


#states.find()

#print(replay_ids)
