import random
import tensorflow as tf
import numpy as np
import os
import datetime
from collections import deque
import keras
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten, MaxPooling2D
from keras.optimizers import Adam

import sys
import stateHandler as reader

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
        convInput = keras.layers.Input(shape=(FRAME_WIDTH, FRAME_HEIGHT, STATE_LENGTH))
        convMod = keras.layers.Conv2D(9,(3,3),activation='relu',data_format='channels_last')(convInput)
        convMod = keras.layers.MaxPooling2D(pool_size=(2, 2))(convMod)
        convMod = keras.layers.Conv2D(18, (3,3), activation='relu')(convMod)
        convMod = keras.layers.MaxPooling2D(pool_size=(2, 2))(convMod)
        convMod = keras.layers.Conv2D(36, (3,3), activation='relu')(convMod)
        convMod = keras.layers.MaxPooling2D(pool_size=(2, 2))(convMod)
        convMod = keras.layers.Flatten()(convMod)
        convMod= keras.layers.Dense(128,activation='relu')(convMod)
        convMod= keras.layers.Dense(56,activation='relu')(convMod)
        convMod = keras.Model(inputs=convInput, outputs=convMod)

        numInput = keras.layers.Input(shape=(NUMERIC_INPUT_LENGTH,))
        numMod = keras.layers.Dense(14,activation='relu')(numInput)
        numMod = keras.layers.Dense(8,activation='relu')(numMod)
        numMod = keras.Model(inputs=numInput, outputs=numMod)

        merge = keras.layers.concatenate([convMod.output, numMod.output])

        mergeMod = keras.layers.Dense(128, activation='relu')(merge)
        mergeMod = keras.layers.Dense(64, activation='relu')(mergeMod)
        mergeMod = keras.layers.Dense(1, activation='sigmoid')(mergeMod)

        self.model = keras.Model(inputs=[numMod.input,convMod.input], outputs=mergeMod)
        self.model.compile(loss="mean_absolute_error", optimizer=Adam(lr=LEARNING_RATE))

    def save(self, name):
        self.model.save(name + '.h5')

# init of network
network = Network()




#TODO: Change this completely so that each epoch iterates over the entire dataset somehow
def createTrainingBatch(batchSize):
    batch = []
    for i in range (0,batchSize):
        temp = reader.getRandomTrainingState()
        if temp != None:
            batch.append(temp)
    return transposeBatch(batch)

def createValidationBatch(batchSize):
    batch = []
    for i in range(0, batchSize):
        temp = reader.getRandomValidationState()
        if temp != None:
            batch.append(temp)
    return transposeBatch(batch)

#Extracts each column from "splitData" function and makes them
#into rows instead. Effectively converting from [replayID][type of data]
#to [type of data][replayID]
def transposeBatch(data):
    return (np.array([row[0] for row in data]),np.array([row[1] for row in data]),np.array([row[2] for row in data]))


if __name__ == "__main__":
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
    #Train the network!
    trainingGenerator = reader.DataGenerator()

    for i in range(0,10000):
        print("EPOCH: " + str(i+1))
        history = network.model.fit_generator(generator=trainingGenerator)#, use_multiprocessing=True, workers=4, max_queue_size=10)
        network.save(str(i)+"-L"+str(history.history['loss'])) #+ "-VL"+str(history.history['val_loss']))
        #t1 = time() - trainingStartTime
        logFile = open(timestamp + "-X.log", "a+")
        logFile.write(str(i)+"-L"+str(history.history['loss']))# + "-VL"+str(history.history['val_loss'])+"\n")
        logFile.close()

