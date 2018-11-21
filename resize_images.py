import os

def main():

    directory = input("Choose directory of images you'd like to scale: ")
    image_size = input("Choose the new image size you'd like: ")

    cmd = 'ImageResizer/ImageResizer/bin/ImageResizer' + ' ' + directory + ' ' + str(image_size)
    os.system(cmd)

    print('All done!')

if __name__== "__main__":
    main()

