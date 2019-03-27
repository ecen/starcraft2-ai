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

np.set_printoptions(threshold=sys.maxsize)


replays.create_index("replay_id")
players.create_index("replay_id")
states.create_index([("replay_id", pymongo.ASCENDING), ("frame_id", pymongo.ASCENDING)])
scores.create_index([("replay_id", pymongo.ASCENDING), ("frame_id", pymongo.ASCENDING)])

replay_ids = []
for replay_doc in replays.find({}, {"replay_id": 1}):
    replay_ids.append(replay_doc["replay_id"])


for replay_id in replay_ids:
    cursor = states.find({'replay_id':replay_id, 'player_id': 1, 'frame_id': 12})
    for state_doc in cursor:
        a = pickle.loads(state_doc["screen"]["units"])
        print(a)
        #print(pickle.loads(state_doc["screen"]["factions"]))


#states.find()

#print(replay_ids)
