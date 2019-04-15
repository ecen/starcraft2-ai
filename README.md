# starcraft2-ai
Repository for bachelor-degree project with the goal of developing a StarCraft 2 AI using machine learning.



# Agents

* CNN = Convolutional Network Agent
* DQN = Deep Q network agent
* MarineAgent = Marine Agent
* WinLoss = Win/Loss Agent
## CNN

## DQN

## MarineAgent
This is a very basic scripted agent which builds a couple of marines and then selects all units and attacks the enemy base. Due to its simplicity it will only work on one of the two spawn points on the map. This is mostly used to look at the Win/Loss agents outputs but it's also a simple demonstration of how to use the simple API. It is possible to manually play the game while this is running if one wants to manually test the Win/Loss agent further.


## Win/Loss Agent

> 
1. Build a replay database, see sc2reaper branch
2. Make sure MonogDB is running, then run WinLoss.py to start training. This will save a network as a \*.h5 file in the same directory at the end of every epoch.
3. Change MarineAgent.py's `WR = keras.models.load_model` line to load one of the new networks, then run it. Predicted win chance will be printed to the console.

### Customization
If one wants to change something about the network it can be done in WinLoss.py.
Changes to what data is fed through the network requires changing WinLoss.py, StateHandler.py as well as the data base (see sc2reaper branch).

### Issues
* There is no validation set due to SC2 updating and breaking all our replays (see issues in sc2reaper branch), making it unviable to rebuild our database with some new data as well as splitting it into a training and validation set. Thus work on this has been put on hold for the moment.
* Current network structure might not reach a good generalization level, whether this is due to hyperparameters, replay amount or due to what data is fed into it is unknown.
* There is a weird bug with MongoDB which is currently being mitigated by a `time.sleep(3)` call. After ~750000 calls getting data from MongoDB or at the start of the third epoch with our database containing 124 replays MongoDB would throw the exception `pymongo.errors.OperationFailure: cursor id 37532233288 is already in use`. Presumably this was due to something like keras desyncing and ending up slightly ahead of mongoDB over time (whether this is per get call or per epoch is unknown), luckily adding a sleep call at the end of every epoch seems to fix this, but it might start crashing again if the database is bigger.
