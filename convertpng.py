from PIL import Image
from os import listdir
from os.path import splitext

target_directory = 'PatchedEnhancedDB/Train/CGG/'
target = '.jpg'

for file in listdir(target_directory):
    filename, extension = splitext(file)
    try:
        
        number = filename.split("train", 1)[1]
        newNum = 50000 + int(number)
        
        #if extension not in ['.py', target]:
        if filename is not '.DS_Store':
            im = Image.open(target_directory + filename + extension)
            im.save('PatchedEnhancedDB/Train/CGG2/' + str(newNum) + target)
    except OSError:
        print('Cannot convert %s' % file)
