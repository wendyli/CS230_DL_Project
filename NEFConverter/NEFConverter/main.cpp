//
//  main.cpp
//  NEFConverter
//
//  Created by FontasChristopher on 10/20/18.
//  Copyright © 2018 SicStudios. All rights reserved.
//

#include <iostream>
#include "libraw/libraw.h"
#include <SFML/Window.hpp>
#include <SFML/Graphics.hpp>
#include <SFML/System.hpp>
#include <string>
#include <stdio.h>
#include <dirent.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/dir.h>
#include <pwd.h>

std::string removeExtension(const std::string &filename)
{
    std::string::size_type idx = filename.rfind('.');
    if(idx != std::string::npos)
    {
        return filename.substr(0, idx);
    }
    return filename;
}


int process_image(std::string path, std::string file)
{
    printf("Process image: %s\n", file.c_str());
    
    // Let us create an image processor
    LibRaw iProcessor;
    
    // Open the file and read the metadata
    iProcessor.open_file((path + file).c_str());
    
    // Let us unpack the image
    iProcessor.unpack();

    // Internally convert image from raw to bitmap
    iProcessor.dcraw_process();
    
    // Extract bitmap image
    int err = 0;
    libraw_processed_image_t *image = iProcessor.dcraw_make_mem_image(&err);
    
    // Make sure all the data is correct
    assert(err == 0);
    assert(image->data_size == image->width * image->height * image->colors);
    assert(image->type == LIBRAW_IMAGE_BITMAP);
    
    // Create an sf image to write out the final png
    sf::Image sf_image;
    sf::Uint8 *buff = new sf::Uint8[image->width * image->height * 4];
    
    // Loop over the data and convert to sf::Image pixels
    // .NEF data only stores 3 channels per pixe but sf::Image expects
    // four channels (alpha) so we can't just do a straight memcpy.
    int index = 0;
    for (int i = 0; i < image->data_size; i+=3)
    {
        buff[index] = image->data[i];
        buff[index+1] = image->data[i+1];
        buff[index+2] = image->data[i+2];
        buff[index+3] = 255;
        index+=4;
    }
    
    // Write out data to disk
    path += "results/";
    sf_image.create(image->width, image->height, buff);
    sf_image.saveToFile(path + removeExtension(file) + ".png");

    // Cleanup
    iProcessor.recycle();
    return 0;
}

int loopImages(std::string path)
{
    struct dirent *entry;
    DIR *dp;
    
    dp = opendir(path.c_str());
    if (dp == NULL) {
        perror("opendir: Path does not exist or could not be read.");
        return -1;
    }

    mkdir((path + "results").c_str(), 0777);
    
    while ((entry = readdir(dp)))
    {
        if (strlen(entry->d_name) > 2) {
            process_image(path, entry->d_name);
        }
    }
    
    closedir(dp);
    return 0;
}



int main(int argc, const char * argv[])
{
    std::string path(argv[1]); 
    loopImages(path.c_str());
    return 0;
}
