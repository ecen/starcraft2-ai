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
NUMERIC_INPUT_LENGTH = 7

class Network:
    def __init__(self):
        # Creation of network, topology stuff goes here
        #self.model = Sequential()
        #self.model.add(
        #        Conv2D(64, 4, activation="relu",
        #               input_shape=(FRAME_WIDTH, FRAME_HEIGHT, STATE_LENGTH), data_format='channels_last'))
        #self.model.add(MaxPooling2D(pool_size=(2, 2)))
        #self.model.add(Conv2D(32, 2, activation="relu"))
        #self.model.add(MaxPooling2D(pool_size=(2, 2)))
        #self.model.add(Conv2D(32, 2, activation="relu"))
        #self.model.add(MaxPooling2D(pool_size=(2, 2)))
        #self.model.add(Flatten())
        #self.model.add(Dense(512, activation="relu"))
        #self.model.add(Dense(1, activation="tanh")) #1=win, 0=lose, not sure if it's a direct correlation to % win/loss
        #self.model.compile(loss="mean_squared_error", optimizer=Adam(lr=LEARNING_RATE))

        convInput = keras.layers.Input(shape=(FRAME_WIDTH, FRAME_HEIGHT, STATE_LENGTH))
        convMod = keras.layers.Conv2D(64,4,activation='relu',data_format='channels_last')(convInput)
        convMod = keras.layers.MaxPooling2D(pool_size=(2, 2))(convMod)
        convMod = keras.layers.Conv2D(32, 2, activation='relu')(convMod)
        convMod = keras.layers.MaxPooling2D(pool_size=(2, 2))(convMod)
        convMod = keras.layers.Conv2D(32, 2, activation='relu')(convMod)
        convMod = keras.layers.MaxPooling2D(pool_size=(2, 2))(convMod)
        convMod = keras.layers.Flatten()(convMod)
        convMod= keras.layers.Dense(512,activation='relu')(convMod)
        convMod = keras.Model(inputs=convInput, outputs=convMod)

        numInput = keras.layers.Input(shape=(NUMERIC_INPUT_LENGTH,))
        numMod = keras.layers.Dense(14,activation='relu')(numInput)
        numMod = keras.layers.Dense(8,activation='relu')(numMod)
        numMod = keras.Model(inputs=numInput, outputs=numMod)

        merge = keras.layers.concatenate([convMod.output, numMod.output])

        mergeMod = keras.layers.Dense(256, activation='relu')(merge)
        mergeMod = keras.layers.Dense(128, activation='relu')(mergeMod)
        mergeMod = keras.layers.Dense(1, activation='sigmoid')(mergeMod)

        self.model = keras.Model(inputs=[numMod.input,convMod.input], outputs=mergeMod)
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
    return (data[0], data[3], np.concatenate((data[1],data[2])))


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
    return (np.array([row[0] for row in data]),np.array([row[1] for row in data]),np.array([row[2] for row in data]))

for i in range(0,1000):
    numInput, target,input = createTrainingBatch(4500)
    valNumInput, valTarget, valInput = createValidationBatch(1000)
    #Swap ordering of dimensions so that keras can accept input.
    valInput= np.moveaxis(valInput, 1, 3)
    input = np.moveaxis(input, 1, 3)

    network.model.fit([numInput, input], target, validation_data=([valNumInput, valInput],valTarget), epochs=1, batch_size=30)
    network.save(str(i))