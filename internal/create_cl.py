import os
from PIL import Image,ImageDraw
import pickle
import random
import time
import numpy as np
import sys
import ctypes


class Create:
    def __init__(self, image, grid_size, quality_arg, calibration, verbose = True, use_C_libs = False):
        self.image = image
        self.original_grid_size = grid_size
        self.quality_arg = quality_arg
        self.char_data = calibration["character_data"]
        self.grid_info = calibration["grid_info"]
        self.verbose = verbose
        self.use_C_libs = use_C_libs

        px_t_x = int(self.original_grid_size[0]*self.grid_info.char_size_X)
        px_t_y = int(self.original_grid_size[1]*self.grid_info.char_size_Y)
        if self.image.size[0] > self.image.size[1]:                #horizontal pic
            aspect_input = self.image.size[0]/self.image.size[1]
            aspect_terminal = px_t_x/px_t_y
            if aspect_input < aspect_terminal:
                final_px_t_y = int(px_t_y)
                final_px_t_x = int(px_t_y*aspect_input)
            else :
                final_px_t_x = int(px_t_x)
                final_px_t_y = int(px_t_x/aspect_input)
        else:                                                      #vertical pic
            aspect_input = self.image.size[1]/self.image.size[0]
            aspect_terminal = px_t_y/px_t_x
            if aspect_input < aspect_terminal:
                final_px_t_x = int(px_t_x)
                final_px_t_y = int(px_t_x*aspect_input)
            else :
                final_px_t_y = int(px_t_y)
                final_px_t_x = int(px_t_y/aspect_input)                                    

        self.grid_size = [ int(final_px_t_x/self.grid_info.char_size_X) , int(final_px_t_y/self.grid_info.char_size_Y) ]
        self.final_px_terminal = [final_px_t_x , final_px_t_y]
        self.resized_image = self.image.resize( ( final_px_t_x,final_px_t_y  ))

        self.sub_images = []
        for row in range(self.grid_size[1]):
            for col in range(self.grid_size[0]):
                left = col * self.grid_info.char_size_X
                upper = row * self.grid_info.char_size_Y
                right = (col + 1) * self.grid_info.char_size_X
                lower = (row + 1) * self.grid_info.char_size_Y
                bbox = (left, upper, right, lower)
                sub_image = self.resized_image.crop(bbox)
                self.sub_images.append(sub_image)
        if self.verbose:
            print(f"input picture         : {self.image.size[0]        :5d} x {self.image.size[1]        :5d} [px],  ratio: {(self.image.size[0]        /self.image.size[1]        ):6f}")
            print(f"input character grid  : {self.original_grid_size[0]:5d} x {self.original_grid_size[1]:5d} [ch]")
            print(f"character ref. size   : {self.grid_info.char_size_X:5d} x {self.grid_info.char_size_Y:5d} [px]")
            print(f"output character grid : {self.grid_size[0]         :5d} x {self.grid_size[1]         :5d} [ch]")
            print(f"final output ref.     : {self.final_px_terminal[0] :5d} x {self.final_px_terminal[1] :5d} [px],  ratio: {(self.final_px_terminal[0] /self.final_px_terminal[1] ):6f}")
            print()

    def start_infer(self):
        if self.verbose:
            print(f"Starting infer process... could take a while.")
            print(f"You can try with quality flag (-q)")
            print(f"Multi core function come soon :) ")
            print()

        start_time = time.time()
        self.str_out = ""
        if not self.use_C_libs:
            matcher = Matcher(self.char_data)
            matcher.verify_char_size(self.grid_info, self.sub_images[0])
            cnt = 0
            for i, sub_image in enumerate(self.sub_images):
                cnt += 1
                if self.quality_arg == "fast":
                    min_error_char = matcher.find_average_color(sub_image)
                elif self.quality_arg == "medium":
                    if self.grid_info.char_size_X > 20:
                        min_error_char = matcher.find_quar(sub_image)
                    else:
                        min_error_char = matcher.find_half(sub_image)
                else : #slow
                    min_error_char = matcher.find(sub_image)

                print(min_error_char, end='', flush=True)
                self.str_out += min_error_char
                if cnt == self.grid_size[0]:
                    cnt = 0
                    print("\033[0m")
                    self.str_out += "\033[0m\n"
        else: # C libs 
            # Load the shared library
            c_matcher = ctypes.CDLL('./c_lib_dev/c_matcher.so')  # Use 'mylib.dll' on Windows
            # Define argument types for safety
            c_matcher.infer_and_match.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_int)]
            c_matcher.infer_and_match.restype = None

            


            # Create a byte array in Python
            ttt = [pixel for img in self.sub_images for col in np.array(img).astype(np.int16) for pixel in col]
            #aux = 
            #np.array(self.sub_images[1]).astype(np.int16)
            # final_vector = [cell.info for column in main_matrix for cell in column]
            # picture_grid_r = bytearray([np.array(img).astype(np.int16) for img in self.sub_images])
            # picture_grid_g = bytearray([np.array(img).astype(np.int16) for img in self.sub_images])
            # picture_grid_b = bytearray([np.array(img).astype(np.int16) for img in self.sub_images])

            picture_grid_r = bytearray([pixel[0] for pixel in ttt])
            picture_grid_g = bytearray([pixel[1] for pixel in ttt])
            picture_grid_b = bytearray([pixel[2] for pixel in ttt])
            
            array_type_r = ctypes.c_uint8 * len(picture_grid_r)
            array_type_g = ctypes.c_uint8 * len(picture_grid_g)
            array_type_b = ctypes.c_uint8 * len(picture_grid_b)

            c_array_r = array_type_r(*picture_grid_r)
            c_array_g = array_type_g(*picture_grid_g)
            c_array_b = array_type_b(*picture_grid_b)


            print("deubug: ")
            print(f"picture_grid_r[0:5] : {[str(d) for d in picture_grid_r[0:5]]}")
            print(f"c_array_r[0:5]      : {[str(d) for d in c_array_r[0:5]]}")
            # data = bytearray([0x01, 0x02, 0xFF, 0x10, 0x20])
            # # Convert it to a ctypes array
            # array_type = ctypes.c_uint8 * len(data)
            # c_array = array_type(*data)
            # # Call the function
            #c_matcher.infer_and_match(c_array, len(data))
             
            ccc = [pixel for img in self.char_data for col in img.info_pixel_np for pixel in col]

            char_grid_r = bytearray([pixel[0] for pixel in ccc])
            char_grid_g = bytearray([pixel[1] for pixel in ccc])
            char_grid_b = bytearray([pixel[2] for pixel in ccc])
            
            array_char_r = ctypes.c_uint8 * len(char_grid_r)
            array_char_g = ctypes.c_uint8 * len(char_grid_g)
            array_char_b = ctypes.c_uint8 * len(char_grid_b)

            c_char_pixel_info_array_r = array_char_r(*char_grid_r)
            c_char_pixel_info_array_g = array_char_g(*char_grid_g)
            c_char_pixel_info_array_b = array_char_b(*char_grid_b)


            array_return_char_index = ctypes.c_int * int(self.grid_size[0]*self.grid_size[1])  # Create a ctypes array type
            return_char_index = array_return_char_index()                # Allocate the actual array
            breakpoint()
            c_matcher.infer_and_match(    
                self.grid_info.char_size_X, # char_x,         # int
                self.grid_info.char_size_Y, # char_y,         # int
                int(self.grid_size[0]*self.grid_size[1]), # n_grid,         # int 
                int(len(self.char_data)), # n_char_data,    # int 
                c_array_r, # picture_grid_r, # uint8_t*  
                c_array_g, # picture_grid_g, # uint8_t*  
                c_array_b, # picture_grid_b, # uint8_t*  
                c_char_pixel_info_array_r, # char_data_r,    # uint8_t*  
                c_char_pixel_info_array_g, # char_data_g,    # uint8_t*  
                c_char_pixel_info_array_b, # char_data_b,    # uint8_t*  
                return_char_index # return_char_index,       #   int*
            )
            print(f"returned: {[str(d) for d in return_char_index]}")

            
        if self.verbose:
            print(f"\033[0m--- final time : {time.time() - start_time} ---")

    def dump_to_file(self,filename):
        with open(filename, "w", encoding='utf-8') as file:
            file.write(self.str_out)


class Matcher:
    def __init__(self, char_data):
        self.char_data = char_data
    
    def verify_char_size(self,grid_info,img_test):
        if  grid_info.char_size_X != img_test.size[0] and grid_info.char_size_Y != img_test.size[1] :
            print("size img not match with character expected")
            exit()

    def find(self, img):
        img_array = np.array(img).astype(np.int16)
        min_error = -1
        last_char_data = ""
        for char_data in self.char_data:
            diff = np.abs(char_data.info_pixel_np - img_array)
            final_error = np.sum(diff)
            if min_error == -1:
                last_char_data = char_data.char_value
                min_error = final_error
            else:
                if final_error < min_error:
                    last_char_data = char_data.char_value
                    min_error = final_error
        return last_char_data
    
    def find_half(self, img):
        img_half = img.resize( (int(img.size[0]/2) , int(img.size[1]/2) ))
        img_array = np.array(img_half).astype(np.int16)
        min_error = -1
        last_char_data = ""
        for char_data in self.char_data:
            diff = np.abs(char_data.info_half_pixel_np - img_array)
            final_error = np.sum(diff)
            if min_error == -1:
                last_char_data = char_data.char_value
                min_error = final_error
            else:
                if final_error < min_error:
                    last_char_data = char_data.char_value
                    min_error = final_error
        return last_char_data
    
    def find_quar(self, img):
        img_half = img.resize( (int(img.size[0]/4) , int(img.size[1]/4) ))
        img_array = np.array(img_half).astype(np.int16)
        min_error = -1
        last_char_data = ""
        for char_data in self.char_data:
            diff = np.abs(char_data.info_quar_pixel_np - img_array)
            final_error = np.sum(diff)
            if min_error == -1:
                last_char_data = char_data.char_value
                min_error = final_error
            else:
                if final_error < min_error:
                    last_char_data = char_data.char_value
                    min_error = final_error
        return last_char_data
    
    
    PERCENT_OF_VALID = 10
    def find_average_color(self, img):
        img_array = np.array(img).astype(np.int16)
        average_color = np.mean(np.mean(img_array,axis=0),axis=0).astype(np.int16)
        average_color_errors = []
        for char_data in self.char_data:
            average_color_errors.append( sum(abs( average_color - char_data.average_color) ) )
        range_valid = min(average_color_errors) + (float((max(average_color_errors) - min(average_color_errors)))*self.PERCENT_OF_VALID/100)
        min_error = -1
        last_char_data = ""
        cont = 0
        for char_data in self.char_data:
            if average_color_errors[cont] <= range_valid:
                diff = np.abs(char_data.info_pixel_np - img_array)
                final_error = np.sum(diff)
                if min_error == -1:
                    last_char_data = char_data.char_value
                    min_error = final_error
                else:
                    if final_error < min_error:
                        last_char_data = char_data.char_value
                        min_error = final_error
            cont += 1
        return last_char_data
