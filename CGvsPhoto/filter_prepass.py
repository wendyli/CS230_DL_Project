# This class contains functions for prepassing as described in the
# Yao Et. Al Paper
import tensorflow as tf
from PIL import Image


# Thre high pass filters as described in the paper
square5x5 = [[-1,2,-2,2,-1], [2,-6,8,-6,2], [-2,8,-12,8,-2], [2,-6,8,-6,2],[-1,2,-2,2,-1]]
edge3x3 = [[0,0,0,0,0], [0,0,-1,0,0], [0,-1,4,-1,0], [0,0,-1,0,0], [0,0,0,0,0]]
square3x3 = [[0,0,0,0,0], [0,-1,2,-1,0], [0,2,-4,2,0], [0,-1,2,-1,0], [0,0,0,0,0]]


def grayscale():
    pass

def highpassFilter(batch):
    filters = tf.constant([0, 1, 0, 1, 2, 1, 1, 0, 3, 1, 1, 0, 4, 4, 5, 4], tf.float32)
    temp2 = tf.reshape(temp, [2, 2, 2, 2])
    
    pass

