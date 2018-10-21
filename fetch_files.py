import csv
import os
import sys
from PIL import ImageFile, Image
ImageFile.LOAD_TRUNCATED_IMAGES = True
import os, os.path
import random
import shutil
from CGvsPhoto import image_loader as il
from CGvsPhoto.construct_DB import load_images_from_dir

def makeDatabaseDirectories():
    # Outer database
    os.system('mkdir {}'.format('Database'))
    
    # Train test and validation
    os.system('mkdir {}'.format('Database/train'))
    os.system('mkdir {}'.format('Database/test'))
    os.system('mkdir {}'.format('Database/validation'))
    
    # Real photos
    os.system('mkdir {}'.format('Database/train/Real'))
    os.system('mkdir {}'.format('Database/test/Real'))
    os.system('mkdir {}'.format('Database/validation/Real'))
    
    # CG Photos
    os.system('mkdir {}'.format('Database/train/CGG'))
    os.system('mkdir {}'.format('Database/test/CGG'))
    os.system('mkdir {}'.format('Database/validation/CGG'))


# This function pulls in all the images from
# the server and converts them from .NEF raw
# format to an initial PNG format
def pullAndConvert(filename, directory):
    # copy over the files
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 15: # Change as necessary
                break
            file = row[0].split('.')[0] # get rid of .jpg
            cmd = ' wget -N -c http://193.205.194.113/RAISE/NEF/{}.NEF -P {}'.format(file, directory)
            print cmd
            os.system(cmd)
            line_count = line_count + 1
    # Convert .NEF files into 8-bit RGB images and save in "results" dir
    # Using the LibRaw API to extract the iamge data and the SFML framework
    # to save out the image as a PNG
    cmd = 'NEFConverter/NEFConverter/bin/NEFConverter' + ' ' + directory + '/'
    os.system(cmd)


# Convert the images to jpeg with the given compression ration,
# and move them to their final position in the database
def compressAndMove(directory, outputdir, jpegCompression):
    # Load up all the converted images
    result_dir = directory + '/results/'
    final_images = load_images_from_dir(directory + '/results', shuffle = True)
    numImages = len(final_images)
        
    # Compress images and save in final database location
    for i in range(numImages):
        outfile = 'Database/' + outputdir + 'Real/' + final_images[i]
        print outfile
        image = Image.open(result_dir + final_images[i])
        image.save(outfile, "JPEG", quality=jpegCompression)


# Program Entry Point
def main():
    
    # Get files
    filenames = ['data/train_file.csv', 'data/test_file.csv', 'data/validation_file.csv']
    outputdirs = ['train/', 'test/', 'validation/']
    
    # Make sure the database directory exists
    makeDatabaseDirectories()
    
    # Read in JPEG compression rate
    jpegCompression = input("Enter JPEG Compression Value: ")
    assert isinstance(jpegCompression, int)
    print 'JPEG Compression: ', jpegCompression
    
    # Determine whether or not to pull from server
    pullFromServer = input("Read from server? 1/0: ")
    assert isinstance(pullFromServer, int)
    print 'Pull From Server: ', pullFromServer
    
    index = 0
    for filename in filenames:
        # make a directory
        directory = filename.split('_')[0]
        os.system('mkdir {}'.format(directory))

        # Download RAW images from RAISE and convert to 8 bit RGB
        if pullFromServer:
            pullAndConvert(filename, directory)
        
        # Compress the RGB images and move to database
        compressAndMove(directory, outputdirs[index], jpegCompression)
        index = index+1

   
if __name__== "__main__":
    main()
