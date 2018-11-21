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
#include <stdio.h>
#include <stdint.h>
#include <array>
#include <vector>
#include <math.h>

#define CLAMP(v, min, max) if (v < min) { v = min; } else if (v > max) { v = max; }

std::string removeExtension(const std::string &filename)
{
    std::string::size_type idx = filename.rfind('.');
    if(idx != std::string::npos)
    {
        return filename.substr(0, idx);
    }
    return filename;
}

float cubicHermite(float A, float B, float C, float D, float t)
{
    float a = -A / 2.0f + (3.0f*B) / 2.0f - (3.0f*C) / 2.0f + D / 2.0f;
    float b = A - (5.0f*B) / 2.0f + 2.0f*C - D / 2.0f;
    float c = -A / 2.0f + C / 2.0f;
    float d = B;
    
    return a*t*t*t + b*t*t + c*t + d;
}

const sf::Uint8 *getPixelClamped (const sf::Image &image, int x, int y)
{
    CLAMP(x, 0, image.getSize().x - 1);
    CLAMP(y, 0, image.getSize().y - 1);
    sf::Color pixel = image.getPixel(x, y);
    sf::Uint8 *res = new sf::Uint8[3];
    res[0] = pixel.r;
    res[1] = pixel.g;
    res[2] = pixel.b;
    return res;
}

sf::Color sampleBicubic(const sf::Image &image, float u, float v)
{
    int width = image.getSize().x;
    int height = image.getSize().y;
    
    float x = (u * width) - 0.5;
    int xint = int(x);
    float xfract = x - floor(x);
    
    float y = (v * height) - 0.5;
    int yint = int(y);
    float yfract = y - floor(y);
    
    // 1st row
    auto p00 = getPixelClamped(image, xint - 1, yint - 1);
    auto p10 = getPixelClamped(image, xint + 0, yint - 1);
    auto p20 = getPixelClamped(image, xint + 1, yint - 1);
    auto p30 = getPixelClamped(image, xint + 2, yint - 1);
    
    // 2nd row
    auto p01 = getPixelClamped(image, xint - 1, yint + 0);
    auto p11 = getPixelClamped(image, xint + 0, yint + 0);
    auto p21 = getPixelClamped(image, xint + 1, yint + 0);
    auto p31 = getPixelClamped(image, xint + 2, yint + 0);
    
    // 3rd row
    auto p02 = getPixelClamped(image, xint - 1, yint + 1);
    auto p12 = getPixelClamped(image, xint + 0, yint + 1);
    auto p22 = getPixelClamped(image, xint + 1, yint + 1);
    auto p32 = getPixelClamped(image, xint + 2, yint + 1);
    
    // 4th row
    auto p03 = getPixelClamped(image, xint - 1, yint + 2);
    auto p13 = getPixelClamped(image, xint + 0, yint + 2);
    auto p23 = getPixelClamped(image, xint + 1, yint + 2);
    auto p33 = getPixelClamped(image, xint + 2, yint + 2);
    

    
    // interpolate bi-cubically!
    // Clamp the values since the curve can put the value below 0 or above 255
    sf::Uint8 ret[3];
    for (int i = 0; i < 3; ++i)
    {
        float col0 = cubicHermite(p00[i], p10[i], p20[i], p30[i], xfract);
        float col1 = cubicHermite(p01[i], p11[i], p21[i], p31[i], xfract);
        float col2 = cubicHermite(p02[i], p12[i], p22[i], p32[i], xfract);
        float col3 = cubicHermite(p03[i], p13[i], p23[i], p33[i], xfract);
        float value = cubicHermite(col0, col1, col2, col3, yfract);
        CLAMP(value, 0.0f, 255.0f);
        ret[i] = sf::Uint8(value);
    }
    return sf::Color(ret[0], ret[1], ret[2]);
}


int process_image(std::string path, std::string file)
{
    printf("Process image: %s\n", file.c_str());
    
    int width = 256;
    int height = 256;
    
    sf::Image srcImage, dstImage;
    if (!srcImage.loadFromFile(path + "/" + file)) {
        printf("Could not load image %s\n", file.c_str());
        return 0;
    }
    
    dstImage.create(width, height);
    
    
    for (int y = 0; y < height; y ++)
    {
        float v = float(y) / float(height - 1);
        for (int x = 0; x < width; x++)
        {
            float u = float(x) / float(width - 1);
            sf::Color sample = sampleBicubic(srcImage, u, v);
            
            dstImage.setPixel(x, y, sample);
        }
    }
    
    
    dstImage.saveToFile(path + "/Results/" + file);
    
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

    mkdir((path + "/Results").c_str(), 0777);
    
    while ((entry = readdir(dp)))
    {
        if (strlen(entry->d_name) > 2
            && strcmp(entry->d_name, "Results") != 0
            && strcmp(entry->d_name, ".DS_Store") != 0) {
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
