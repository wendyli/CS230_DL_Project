import csv
import os
from PIL import ImageFile, Image
ImageFile.LOAD_TRUNCATED_IMAGES = True
import os, os.path
import random
import shutil
from CGvsPhoto import image_loader as il

def load_images_from_dir(dir_name, shuffle = False) :
    
    # file extension accepted as image data
    valid_image_extension = [".jpg", ".jpeg",".gif",".png",".tga",".tif", ".JPG"]
    
    file_list = []
    nb_image = 0
    for filename in os.listdir(dir_name):
        # check if the file is an image
        extension = os.path.splitext(filename)[1]
        if extension.lower() in valid_image_extension:
            file_list.append(filename)
            nb_image += 1

    print('    ',nb_image,'images loaded')

    if shuffle:
        random.seed(42)
        random.shuffle(file_list)
        return file_list


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


def main():
    filenames = ['data/train_file.csv', 'data/test_file.csv', 'data/validation_file.csv']
    outputdirs = ['train/', 'test/', 'validation/']
    makeDatabaseDirectories()

    index = 0
    for filename in filenames:

        # make a directory
        directory = filename.split('_')[0]
        os.system('mkdir {}'.format(directory))

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

        # Load up all the converted images
        result_dir = directory + '/results/'
        final_images = load_images_from_dir(directory + '/results', shuffle = True)
        numImages = len(final_images)

        # Compress images and save in final database location
        for i in range(numImages):
            outfile = 'Database/' + outputdirs[index] + 'Real/' + final_images[i]
            print outfile
            image = Image.open(result_dir + final_images[i])
            image.save(outfile, "JPEG", quality=15)

        index = index+1

   
if __name__== "__main__":
    main()
