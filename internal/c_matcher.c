#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

void infer_and_match(int char_x, int char_y, int n_grid, int n_char_data, uint8_t* picture_grid_r, uint8_t* picture_grid_g, uint8_t* picture_grid_b, uint8_t* char_data_r, uint8_t* char_data_g, uint8_t* char_data_b, int* return_char_index) {
    // char_              : character size
    // n_grid             : number of sub picutres 
    // n_char_data        : number of character data set
    // picture_grid_      : sub picture array [n_picture][char_y][char_x]
    // char_data_         : char pictures [n_char][char_y][char_x]
    // return_char_index  : array of the character indexes  
 
    uint32_t delta_pixel_per_sub_pciture = char_x * char_y ; 
    uint32_t char_error = 0;
    uint32_t min_error = 0xFFFFFFFF;
    for(int image_index = 0; image_index < n_grid; image_index++){
        min_error = 0xFFFFFFFF;
        //printf("iterating image %i/%i \n", image_index,n_grid);
        for(int char_index = 0; char_index < n_char_data; char_index++){
            //printf("iterating char %i/%i \n", char_index,n_char_data);
            char_error = 0;
            for(int p=0; p<delta_pixel_per_sub_pciture; p++){
                //printf("iterating delta_pixel_per_sub_pciture %i \n", p);
                char_error += abs(picture_grid_r[p + (delta_pixel_per_sub_pciture*image_index)] - char_data_r[p + (delta_pixel_per_sub_pciture*char_index)]);
                char_error += abs(picture_grid_g[p + (delta_pixel_per_sub_pciture*image_index)] - char_data_g[p + (delta_pixel_per_sub_pciture*char_index)]);
                char_error += abs(picture_grid_b[p + (delta_pixel_per_sub_pciture*image_index)] - char_data_b[p + (delta_pixel_per_sub_pciture*char_index)]);
            }
            if(char_error<min_error){
                min_error = char_error; 
                return_char_index[image_index] = char_index;
            }
        }
    }
}