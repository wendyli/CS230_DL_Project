import csv
import os

## EDIT INPUTS
filename = 'data/test_file.csv'

# make a directory 
directory = filename.split('_')[0]
os.system('mkdir {}'.format(directory))

# copy over the files 
#with open(filename) as csv_file:
#    csv_reader = csv.reader(csv_file, delimiter=',')
#    line_count = 0
#    for row in csv_reader:
#        file = row[0].split('.')[0] # get rid of .jpg
#        cmd = ' wget -N -c http://193.205.194.113/RAISE/NEF/{}.NEF -P {}'.format(file, directory)
#        print cmd
#        os.system(cmd)


cmd = 'NEFConverter/NEFConverter/bin/NEFConverter' + ' ' + directory + '/'
os.system(cmd)


   
