import random
import tensorflow as tf
import numpy as np
import os

from collections import deque
import keras
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten, MaxPooling2D
from keras.optimizers import Adam
import reaperReader as reader

LEARNING_RATE = 0.00001

# Size of minibatches used during learning
BATCH_SIZE = 20
# Chance to take random action instead of using the network's output
# Max = starting chance, is multiplied by decay after each experience replay
# until it reaches min chance
FRAME_WIDTH = 84
FRAME_HEIGHT = 84
STATE_LENGTH = 1

class Network:
    def __init__(self):
        # Creation of network, topology stuff goes here
        asd = keras.initializers.VarianceScaling(
                scale=2)  # https://towardsdatascience.com/tutorial-double-deep-q-learning-with-dueling-network-architectures-4c1b3fb7f756
        # Creation of network, topology stuff goes here
        self.model = Sequential()
        self.model.add(
                Conv2D(64, 4, activation="relu",
                       input_shape=(FRAME_WIDTH, FRAME_HEIGHT, STATE_LENGTH), data_format='channels_last'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Conv2D(32, 2, activation="relu"))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Conv2D(32, 2, activation="relu"))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Flatten())
        self.model.add(Dense(512, activation="relu"))
        self.model.add(Dense(1, activation="tanh")) #1=win, 0=lose, not sure if it's a direct correlation to % win/loss

        self.model.compile(loss="mean_squared_error", optimizer=Adam(lr=LEARNING_RATE))


    def save(self, name):
        self.model.save(name + '.h5')

# init of network
network = Network()


def splitData(data): #TODO: Only does screen data right now. Rename to format when taking care of it all?
    #   concMinimap = np.array([miniFactions,miniVision,miniSelected])
    #   concScreen = np.array([screenFactions, screenVision, screenSelected, screenHp, screenUnits, screenHeight])
    #   concRaw = np.array([frameID, minerals,vespene,supTotal,supUsed,supArmy,supWorkers])
    #   return (concRaw, concMinimap, concScreen, winLoss)
    return np.array([data[2],data[3]])


def createTrainingBatch(batchSize):
    batch = []
    for i in range (0,batchSize):
        batch.append(splitData(reader.getRandomTrainingState()))
    return fromSplitDataToVectors(batch)

def createValidationBatch(batchSize):
    batch = []
    for i in range(0, batchSize):
        batch.append(splitData(reader.getRandomValidationState()))
    return fromSplitDataToVectors(batch)

def fromSplitDataToVectors(data):
    return ([row[0] for row in data],[row[1] for row in data])

input, target = createTrainingBatch(5)
print(input)