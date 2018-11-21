from PIL import Image
import os

def main():
    
    directory = input("Choose directory of images you'd like to convert to PNG: ")
    
    try:
        os.stat(directory + '/PNGResults/')
    except:
        os.mkdir(directory + '/PNGResults/')

    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".jpeg"):
            print('Processing Image ' + filename)
            name = os.path.splitext(filename)[0]
            im = Image.open(directory + '/' + filename)
            im.save(directory + '/PNGResults/' + name + '.png')

    print('All done!')

if __name__== "__main__":
    main()
