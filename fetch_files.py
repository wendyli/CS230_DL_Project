import csv
import os
import sys
from PIL import ImageFile, Image
ImageFile.LOAD_TRUNCATED_IMAGES = True
import os, os.path
import random
import shutil
from CGvsPhoto import image_loader as il
from CGvsPhoto.construct_DB import make_dirs
from CGvsPhoto.construct_DB import load_images_from_dir

def deleteFiles(dir):
    fileList = os.listdir(dir)
    for fileName in fileList:
        os.remove(dir+'/'+fileName)


# Convert the images to jpeg with the given compression ration,
# and move them to their final position in the database
def compressAndMove(database, directory, outputdir, jpegCompression):
    # Load up all the converted images
    result_dir = directory + '/results/'
    final_images = load_images_from_dir(directory + '/results', shuffle = True)
    numImages = len(final_images)
    
    # Compress images and save in final database location
    for i in range(numImages):
        outfile = database + outputdir + 'Real/' + final_images[i]
        print outfile
        image = Image.open(result_dir + final_images[i])
        image.save(outfile, "JPEG", quality=jpegCompression)


# This function pulls in all the images from
# the server and converts them from .NEF raw
# format to an initial PNG format
def pullAndConvert(database, filename, directory, outputdir, jpegCompression):
    # copy over the files
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            file = row[0].split('.')[0] # get rid of .jpg
            cmd = ' wget -N -c http://193.205.194.113/RAISE/NEF/{}.NEF -P {}'.format(file, directory)
            print cmd
            os.system(cmd)
            line_count = line_count + 1
            
            # Convert in batches. Every fifteen images, convert, compress, and move to database,
            # and then clean up the raw that have already been downloaded. That way the harddrive
            # is not overwhelmed
            if line_count > 5:
                # Convert .NEF files into 8-bit RGB images and save in "results" dir
                # Using the LibRaw API to extract the iamge data and the SFML framework
                # to save out the image as a PNG
                cmd = 'NEFConverter/NEFConverter/bin/NEFConverter' + ' ' + directory + '/'
                os.system(cmd)
                
                # Compress the RGB images and move to database
                compressAndMove(database, directory, outputdir, jpegCompression)
                
                # Cleanup
                deleteFiles(directory + '/results')
                deleteFiles(directory)
                line_count = 0



# This function takes all the CGI images, shuffles them, and allocates them
# based on the specified proportions to the train, test and validation directories
def construct_CGI(source_CG, target_dir, nb_per_class = 1800, validation_proportion = 0.1, test_proportion = 0.2):

    train_dir = target_dir + 'train/'
    test_dir = target_dir + 'test/'
    validation_dir = target_dir + 'validation/'
    
    # Clear out directories
    deleteFiles(train_dir + 'CGG')
    deleteFiles(test_dir + 'CGG')
    deleteFiles(validation_dir + 'CGG')

    image_CG = load_images_from_dir(source_CG, shuffle = True)
    
    nb_train = int(nb_per_class*(1 - validation_proportion - test_proportion))
    nb_test = int(nb_per_class*test_proportion)
    nb_validation = int(nb_per_class*validation_proportion)
    
    for i in range(nb_train):
        shutil.copyfile(source_CG + image_CG[i], train_dir + 'CGG/' + image_CG[i])
    print(str(nb_train) + ' training CG images imported for each class')

    for i in range(nb_train, nb_train + nb_validation):
        shutil.copyfile(source_CG + image_CG[i], validation_dir + 'CGG/' + image_CG[i])
    print(str(nb_validation) + ' validation CG images imported for each class')

    for i in range(nb_train + nb_validation, nb_train + nb_validation + nb_test):
        shutil.copyfile(source_CG + image_CG[i], test_dir + 'CGG/' + image_CG[i])
    print(str(nb_test) + ' testing CG images imported for each class')

    print("CG Images all moved")


# Program Entry Point
def main():
    
    # Choose a name for your database
    database = input("Choose a name for your database (Don't forget to add quotes ;-): ")
    assert isinstance(database, str)
    print 'Database: ', database
    database = database + '/'
    
    # Read in JPEG compression rate
    jpegCompression = input("Enter JPEG Compression Value: ")
    assert isinstance(jpegCompression, int)
    print 'JPEG Compression: ', jpegCompression
    
    # Determine whether or not to pull from server
    pullFromServer = input("Read from server? 1/0: ")
    assert isinstance(pullFromServer, int)
    print 'Pull From Server: ', pullFromServer
    
    # Make sure the database directory exists
    make_dirs(database)
    
    # Add database to gitignore so we don't accidentally
    # upload large textures to git
    with open('.gitignore', 'a') as gitignore:
        gitignore.write('\n' + database)
    
    # Get files
    filenames = ['data/train_file.csv', 'data/test_file.csv', 'data/validation_file.csv']
    outputdirs = ['train/', 'test/', 'validation/']

    # Write out CGI Images first, get them out of the way
    construct_CGI('SourceCG/', database, nb_per_class = 1800, validation_proportion = 0.1, test_proportion = 0.2)
    
    index = 0
    for filename in filenames:
        # make a directory
        directory = filename.split('_')[0]
        os.system('mkdir {}'.format(directory))

        # Download RAW images from RAISE and convert to 8 bit RGB
        # if pullFromServer:
        pullAndConvert(database, filename, directory, outputdirs[index], jpegCompression)
        index = index+1

if __name__== "__main__":
    main()
