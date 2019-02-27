from __future__ import absolute_import, division, print_function

# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras

# Helper libraries
import numpy as np
import matplotlib.pyplot as plt

import os

print(tf.__version__)


def plot_image(i, predictions_array, true_label, img):
   predictions_array, true_label, img = predictions_array[i], true_label[i], img[i]
   plt.grid(False)
   plt.xticks([])
   plt.yticks([])

   plt.imshow(img, cmap=plt.cm.binary)

   predicted_label = np.argmax(predictions_array)
   if predicted_label == true_label:
      color = 'blue'
   else:
      color = 'red'

   plt.xlabel("{} {:2.0f}% ({})".format(class_names[predicted_label],
                                        100 * np.max(predictions_array),
                                        class_names[true_label]),
              color=color)


def plot_value_array(i, predictions_array, true_label):
   predictions_array, true_label = predictions_array[i], true_label[i]
   plt.grid(False)
   plt.xticks([])
   plt.yticks([])
   thisplot = plt.bar(range(10), predictions_array, color="#777777")
   plt.ylim([0, 1])
   predicted_label = np.argmax(predictions_array)

   thisplot[predicted_label].set_color('red')
   thisplot[true_label].set_color('blue')


class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

fashion_mnist = keras.datasets.fashion_mnist

(train_images, train_labels), (test_images,
                               test_labels) = fashion_mnist.load_data()

print(train_images.shape)
print(test_images.shape)

# Inspect image in dataset
# plt.figure()
# plt.imshow(train_images[0])
# plt.colorbar()
# plt.grid(False)
# plt.show()

# Scale colorvalue into range [0, 1].
train_images = train_images / 255.0
test_images = test_images / 255.0

# Display first 25 images
# plt.figure(figsize=(10, 10))
# for i in range(25):
#   plt.subplot(5, 5, i + 1)
#   plt.xticks([])
#   plt.yticks([])
#   plt.grid(False)
#   plt.imshow(train_images[i], cmap=plt.cm.binary)
#   plt.xlabel(class_names[train_labels[i]])
# plt.show()

if (os.path.isfile("./model.hdf5")):
   print("Model already exists. Loading...")
   model = tf.keras.models.load_model(
       "./model.hdf5",
       custom_objects=None,
       compile=True
   )
else:
   print("Model does not exist. Training...")
   # Define the layers of our neural network
   model = keras.Sequential([
       keras.layers.Flatten(input_shape=(28, 28)),
       keras.layers.Dense(128, activation=tf.nn.relu),
       keras.layers.Dense(10, activation=tf.nn.softmax)
   ])

   # Define optimizer, loss function and performance metrics
   model.compile(optimizer='adam',
                 loss='sparse_categorical_crossentropy',
                 metrics=['accuracy'])

   # Train the network
   model.fit(train_images, train_labels, epochs=5)

# Test network on test data
test_loss, test_acc = model.evaluate(test_images, test_labels)

print('Test accuracy:', test_acc)

predictions = model.predict(test_images)

# Plot the first X test images, their predicted label, and the true label
# Color correct predictions in blue, incorrect predictions in red
num_rows = 5
num_cols = 3
num_images = num_rows * num_cols
plt.figure(figsize=(2 * 2 * num_cols, 2 * num_rows))
for i in range(num_images):
   plt.subplot(num_rows, 2 * num_cols, 2 * i + 1)
   plot_image(i, predictions, test_labels, test_images)
   plt.subplot(num_rows, 2 * num_cols, 2 * i + 2)
   plot_value_array(i, predictions, test_labels)
plt.show()

# Predict a single image
# Add the image to a batch where it's the only member.
img = test_images[0]
img_expanded = (np.expand_dims(img, 0))
predictions_single = model.predict(img_expanded)
print(class_names[np.argmax(predictions_single[0])])
plt.figure()
plt.imshow(img)
plt.colorbar()
plt.grid(False)
plt.show()

# Save model
tf.keras.models.save_model(
    model,
    "./model.hdf5",
    overwrite=True,
    include_optimizer=True
)
