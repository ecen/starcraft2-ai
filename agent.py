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
FRAME_WIDTH = 64
FRAME_HEIGHT = 64
STATE_LENGTH = 9

class Network:
    def __init__(self):
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
    #   (concRaw, concMinimap, concScreen, winLoss)
    return np.array([np.concatenate((data[1],data[2])),data[3]])


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
    return (np.array([row[0] for row in data]),np.array([row[1] for row in data]))

for i in range(0,1000):
    input, target = createTrainingBatch(450)
    valInput, valTarget = createValidationBatch(100)
    #Swap ordering of dimensions so that keras can accept input.
    valInput= np.moveaxis(valInput, 1, 3)
    input = np.moveaxis(input, 1, 3)

    network.model.fit(input, target, validation_data=(valInput,valTarget), epochs=1, batch_size=30)
    network.save(str(i))