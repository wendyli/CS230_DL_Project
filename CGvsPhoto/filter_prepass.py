import tensorflow as tf
from PIL import Image


# Helper function to convert a batch of RGB images to grayscale
def grayscale(batch):
    return tf.image.rgb_to_grayscale(batch)

# This function creates the three highpass filters for the input
# layer of the neural net as described in the Yao Et. Al Paper.
# It convolves the input mini batch with all 3 filters with
# a stride of 2
def highpassFilter(batch):
    
    # If the batch is of RGB images, convert
    # it to grayscale before applying the filters
    if batch.shape[3] == 3:
        batch = grayscale(batch)
    
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



# For Testing purposes, to see if the above two functions
# are working properly
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
                         
                         
    # Make grayscale
    grayBatch = grayscale(batch)
    print("GrayBatch shape: ", grayBatch.shape)
    
    # Apply highpass filters
    output = highpassFilter(grayBatch)
    
    # Evaluate
    sess = tf.Session()
    with sess.as_default():
        print(output.eval())
    
    # Print results
    print(output)

if __name__== "__main__":
    main()

