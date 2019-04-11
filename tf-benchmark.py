# Code from https://medium.freecodecamp.org/how-a-badly-configured-tensorflow-in-docker-can-be-10x-slower-than-expected-3ac89f33d625

from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
from time import perf_counter

model = ResNet50(weights='imagenet')

img_path = 'scv.png'
img = image.load_img(img_path, target_size=(224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)

# Warm up
for i in range(0, 100):
   model.predict(x)

# Measure performance
start = perf_counter()
for i in range(0, 1000):
   model.predict(x)

print((perf_counter() - start) / 1000)
