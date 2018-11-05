import tensorflow as tf
from PIL import Image


# Helper function to convert a batch of RGB images to grayscale
def grayscale(batch):
    return tf.image.rgb_to_grayscale(batch)

# This function functions for prepassing as described in the
# Yao Et. Al Paper
def highpassFilter(batch):
    
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

    # Yao paper says to use a stride of 2
    if batch is not None:
        return tf.nn.conv2d(batch, filters, strides = [1,2,2,1], padding = 'SAME')
    return None



# For Testing purposes
def main():
    print("Running High Pass Filter Test!")
    
    # Just create a single 10x10x3 RGB image of all 1s
    # to feed into the highpass filter step
    batch = tf.constant([1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
                         1,1,1,1,1,1,1,1,1,1,
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
                         shape = [1,10,10,3])
                         
                         
    output = highpassFilter(grayscale(batch))
    
    # For now, make session
    sess = tf.Session()
    with sess.as_default():
        print(output.eval())
    
    print(output)

if __name__== "__main__":
    main()

