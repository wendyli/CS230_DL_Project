# This class contains functions for prepassing as described in the
# Yao Et. Al Paper
import tensorflow as tf
from PIL import Image

def grayscale():
    pass

def highpassFilter(batch):

    # For now, make session
    sess = tf.Session()
    
    # Thre high pass filters as described in the paper
    filters = tf.constant(# Filter 1 - Shape 5x5
                          [-1,2,-2,2,-1,
                          2,-6,8,-6,2,
                          -2,8,-12,8,-2,
                          2,-6,8,-6,2,
                          -1,2,-2,2,-1,
                            
                          # Filter 2  - Edge 3x3 with padding
                          0,0,0,0,0,
                          0,0,-1,0,0,
                          0,-1,4,-1,0,
                          0,0,-1,0,0,
                          0,0,0,0,0,
                            
                          # Filter 3  - Shape 3x3 with padding
                          0,0,0,0,0,
                          0,-1,2,-1,0,
                          0,2,-4,2,0,
                          0,-1,2,-1,0,
                          0,0,0,0,0],
                          
                          # 3 5x5 filters
                          shape = [5,5,1,3],
                          
                          # Name
                          name = 'HighpassFilters',
                          
                          #type,
                          dtype = tf.float32
                        )
                        
                        

    if batch is not None:
        output = tf.nn.conv2d(batch, filters, strides = [1,2,2,1], padding = 'SAME')
        with sess.as_default():
            print(filters.eval())




# For Testing purposes
def main():
    print("Running High Pass Filter Test!")
    
    batch = tf.constant([1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1],
                         dtype=tf.float32,
                         shape = [1,10,10,1])
    highpassFilter(batch)

if __name__== "__main__":
    main()

