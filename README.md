# CS230_DL_Project
Final Project for CS230 


Code created by our team for CS230: 


fetch_files.py -> Used to fetch RAW images from the RAISE database, compress images and create patches and set up the final database. 

NEFConverter -> C++ program using the LibRaw and SFML libraries to convert raw .NEF files to PNG. Called by the above fetch_files script

CGvsPhoto/filter_prepass.py -> Contains functions for adding grayscale and high pass filter layers 


modelrun.py -> script for training and testing the model
