# starcraft2-ai
Repository for bachelor-degree project with the goal of developing a StarCraft 2 AI using machine learning.

# Simple SC2 API
This is essentially a wrapper for PySC2 to make it immediately useable for a simple TvT agent. Has the following features:
* Easy to use functions for getting PySC2 data or using PySC2 actions. These check if they are available, otherwise returning noop, preventing PySC2 from crashing (which happens if one tries to execute an action that isn't available).
* Some abstracted actions like selecting all of a unit.
* Support for abstracting actions that require multiple game steps to execute, like selecting a barrack and building a marine. These also serve as a very simple framework to develop more actions like this. Note that this requires the code at the top of the step functions in the agents: 
```
doingMultiAction = executeMultiAction(obs)
if doingMultiAction != False:
    return doingMultiAction
```
## Multistep Action tutorial
This is the function that selects a barrack and then trains a marine:
```
def actMultiTrainMarine(obs):
    global multiActions
    multiActions = [actTrainMarine] #This should be in opposite order of execution, pop takes last element
    return actSelectAllBarracks(obs)
```
The return statement returns the first action that should be executed, in this case selecting all barracks. In order to perform more actions afterwards they are added to the multiActions list. The code that executes the remaining actions uses pop() which removes the last action in the list, thus this list has to be in reversed order (last action first, first action last).

# Agents

* DQN = Deep Q network agent
* CNN = Convolutional Network Agent
* MarineAgent = Marine Agent
* WinLoss = Win/Loss Agent

## DQN
An implementation of reinforcement learning using Deep Q-Learning, the agent plays a restricted version of the `CollectMineralsAndGas` PySC2 minigame where actions and input are greatly abstracted.

## CNN
A modified version of the DQN agent where input isn't abstracted, instead this uses PySC2's image data ('feature layers') as well as some numeric data (such as supply) as input.

## MarineAgent
This is a very basic scripted agent which builds a couple of marines and then selects all units and attacks the enemy base. Due to its simplicity it will only work on one of the two spawn points on the map. This is mostly used to look at the Win/Loss agents outputs but it's also a simple demonstration of how to use the simple API. It is possible to manually play the game while this is running if one wants to manually test the Win/Loss agent further.


## Win/Loss Agent
This agent attempts, when given a single state of the game in the form of some of PySC2's feature layers as well as some numeric data, to predict if the player will win or lose the match. Current structure is a convolutional network for the image data combined with a fully connected network for the numeric data, outputs 0 for loss and 1 for win.

### How to
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
* There is a weird bug with MongoDB which is currently being mitigated by a `time.sleep(3)` call. After ~700000 calls getting data from MongoDB or at the start of the third epoch with our database containing 124 replays MongoDB would throw the exception `pymongo.errors.OperationFailure: cursor id 37532233288 is already in use`. Presumably this was due to something like keras desyncing and ending up slightly ahead of mongoDB over time (whether this is per get call or per epoch is unknown), luckily adding a sleep call at the end of every epoch seems to fix this, but it might start crashing again if the database is bigger.
