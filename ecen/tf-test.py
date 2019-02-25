import numpy as np
import tensorflow as tf

tf.enable_eager_execution()

v = tf.Variable(3.0)
assert v.numpy() == 3.0

v.assign(tf.square(v))
print(v)
