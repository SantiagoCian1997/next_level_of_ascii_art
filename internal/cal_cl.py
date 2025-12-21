import os
import sys
import time
from mss import mss
import platform
import numpy as np
from PIL import Image, ImageTk,ImageDraw
from colorama import Fore,Back
from internal.character_data_cl import CharacterData
import ctypes

class Cal:
    def __init__(self,args,color_dict):
        self.screen_indx = int(args.screen)
        #self.debug = args.verbose
        self.color_dict = color_dict
        self.terminal_size = os.get_terminal_size()
        self.grid_info = Grid_info()    
        self.process_all_options()
        print("os.environ['XDG_SESSION_TYPE']",os.environ['XDG_SESSION_TYPE'])
        assert self.terminal_size.columns > 10 and self.terminal_size.lines > 10, "terminal size soo small, resize it"
        if "Linux" in platform.system():
            assert "X11" in str(os.environ['XDG_SESSION_TYPE']).upper() , "sorry, mss only works with X11 graphic sessiosn, switch to it"
        

    def r_c(self):
        return f"{Fore.RESET}{Back.RESET}"
    
    def take_secreen_shot(self):
        time.sleep(0.5)
        with mss() as sct:
            sct_img = sct.grab(sct.monitors[self.screen_indx])
            screen = Image.new("RGB", sct_img.size)
            pixels = screen.load()
            for x in range(screen.size[0]):
                for y in range(screen.size[1]):
                    pixels[x, y] = sct_img.pixel(x, y)
            self.last_pixels = pixels
            self.last_screen = screen

    
    def print_next_page_and_capture(self):
        bins_Y = self.grid_info.bins_Y - 2
        bins_X = self.grid_info.bins_X - 2
        self.print_margins()
        move_cursor(0,0)
        write(f"capturing pages : {self.number_of_pages}/{self.page_index+1}")
        refresh_screen()
        options_sub_set = self.all_options[self.page_index*self.valid_square_area : (self.page_index + 1)*self.valid_square_area]
        str_list = [options_sub_set[i*bins_X:(i+1)*bins_X] for i in range(bins_Y)]
        str_list = [ "".join(line) for line in str_list]
        cnt_offset = 6
        for s in str_list:
            move_cursor(3,cnt_offset)
            write(f"{s}{self.r_c()}")
            cnt_offset += 1
        move_cursor(3,cnt_offset)
        refresh_screen()
        time.sleep(1)
        self.page_index += 1

        
        real_start_X = self.grid_info.start_X + self.grid_info.char_size_X
        real_start_Y = self.grid_info.start_Y + self.grid_info.char_size_Y
        char_X = self.grid_info.char_size_X
        char_Y = self.grid_info.char_size_Y
        self.take_secreen_shot()
        local_count = 0
        for bin_y in range(bins_Y):
            for bin_x in range(bins_X):
                if local_count < len(options_sub_set):
                    image = Image.new("RGB", [char_X,char_Y])
                    #pixels = image.load()
                    pixels = np.array(image)                            
                    for x in range(char_X):
                        for y in range(char_Y):
                            pixels[y,x] = self.last_pixels[ x + real_start_X + bin_x*char_X , y + real_start_Y + bin_y*char_Y ]
                    self.character_data.append(CharacterData(options_sub_set[local_count],pixels))
                    #image = Image.fromarray(pixels)
                    #image.show()
                    local_count += 1
        #self.last_screen_grid.show()

    def get_calibration_dict(self):
        # self.show_one_character_data(self.character_data[0])
        # self.show_one_character_data(self.character_data[int((len(self.character_data)-1)/2)])
        # self.show_one_character_data(self.character_data[len(self.character_data)-1])
        print()
        ccc = [pixel for img in self.character_data  for col in img.info_pixel_np              for pixel in col]
        char_grid_r = bytearray([pixel[0] for pixel in ccc])
        char_grid_g = bytearray([pixel[1] for pixel in ccc])
        char_grid_b = bytearray([pixel[2] for pixel in ccc])
        return {"character_data": self.character_data, "grid_info": self.grid_info, "c_type_decompose": [char_grid_r,char_grid_g,char_grid_b]}

    def show_one_character_data(self,character_data):
        print(f"character:{character_data.char_value}{self.r_c()}")
        image = Image.fromarray(character_data.info_pixel_np_raw)
        image.show()
        input("continue")

    def get_number_of_pages(self):
        self.page_index = 0
        self.valid_square_area = (self.grid_info.bins_X-2)*(self.grid_info.bins_Y-2)
        self.number_of_printeable_characters = len(self.all_options)
        self.number_of_pages = int(self.number_of_printeable_characters/self.valid_square_area) + (1 if self.number_of_printeable_characters%self.valid_square_area!=0 else 0)
        self.character_data = []
        return self.number_of_pages

    def print_margins(self):
        width =  self.terminal_size.columns
        height = self.terminal_size.lines - 3
        self.grid_info.bins_X = width - 2
        self.grid_info.bins_Y = height - 2
        for i in range(6): print(self.r_c())
        print("bins_X : ",self.grid_info.bins_X," bins_Y : ",self.grid_info.bins_Y)
        for L in range(0,height):
            str_print = ""
            for C in range(0,width):
                if C == 0 or C == width - 1:             str_print += " "
                else :
                    if L == 0 or L == height - 1 :       str_print += " "
                    else :
                        if C>=2 and C<width-2 and L>=2 and L<height-2:
                            str_print += " \033[0m"
                        else:
                            if (C+L) % 2 == 0:  str_print += f"{Back.WHITE} {self.r_c()}"#\033[0m"
                            else :              str_print += f"{Back.BLACK} {self.r_c()}"#\033[0m"
            write(str_print)
        self.first_iteration = False
        refresh_screen()
        return True

    def print_and_capture_reference_page(self):
        self.print_margins()
        self.take_secreen_shot()
        #self.last_screen.show()
        screen = self.last_screen.copy()
        self.BW_mtx = np.zeros(self.last_screen.size, dtype=int ) #save -1 , 1 values 
        for x in range(self.last_screen.size[0]):
            for y in range(self.last_screen.size[1]):
                if self.last_pixels[x, y][0]+self.last_pixels[x, y][1]+self.last_pixels[x, y][2] > 256*3/2:
                    self.BW_mtx[x,y] = 1
                else:
                    self.BW_mtx[x,y] = -1

        bins_X = self.grid_info.bins_X
        bins_Y = self.grid_info.bins_Y

        self.line_T_x_to_match = np.zeros(bins_X, dtype=int )
        self.line_B_x_to_match = np.zeros(bins_X, dtype=int )
        self.line_L_y_to_match = np.zeros(bins_Y, dtype=int )
        self.line_R_y_to_match = np.zeros(bins_Y, dtype=int )
        for x in range(bins_X):
            self.line_T_x_to_match[x] = ((x%2)*(-2))+1
            if bins_Y%2 == 1 : self.line_B_x_to_match[x] = ((x%2)*(-2))+1
            else             : self.line_B_x_to_match[x] = ((x%2)*(+2))-1
        for y in range(bins_Y):
            self.line_L_y_to_match[y] = ((y%2)*(-2))+1
            if bins_X%2 == 1 : self.line_R_y_to_match[y] = ((y%2)*(-2))+1
            else             : self.line_R_y_to_match[y] = ((y%2)*(+2))-1

        start_gap = 15
        bar = LoadBar("- finding gap ",0,start_gap,True)
        while self.find_first_match(start_gap,bar) == False:
            assert start_gap!=0, "gird didn't find. Try changing the screen argument or resize the font"
            bar.refresh(start_gap)
            start_gap -= 1
            
        assert self.found_fine_match(), "fail finding fine match grid"
            
        self.last_screen_grid =  screen.copy()
        return True
    
    def found_fine_match(self):
        start_x = self.grid_info.start_X - self.grid_info.char_size_X - 1
        start_y = self.grid_info.start_Y - self.grid_info.char_size_Y - 1
        end_x = self.grid_info.start_X
        end_y = self.grid_info.start_Y
        bar = LoadBar("- finding fine gap ",end_x-start_x)
        for x in range(start_x,end_x):
            for y in range(start_y,end_y):
                bar.refresh(end_x-x)
                self.grid_info.set(x,y,self.grid_info.char_size_X,self.grid_info.char_size_Y)
                if self.try_match(self.grid_info):
                    self.grid_info.set(x+self.grid_info.char_size_X-1,y,self.grid_info.char_size_X,self.grid_info.char_size_Y)
                    if self.try_match(self.grid_info):
                        self.grid_info.set(x,y+self.grid_info.char_size_Y-1,self.grid_info.char_size_X,self.grid_info.char_size_Y)
                        if self.try_match(self.grid_info):
                            self.grid_info.set(x+self.grid_info.char_size_X-1,y+self.grid_info.char_size_Y-1,self.grid_info.char_size_X,self.grid_info.char_size_Y)
                            if self.try_match(self.grid_info):
                                self.grid_info.set(x,y,self.grid_info.char_size_X,self.grid_info.char_size_Y) # para guardar los datos finales
                                bar.complete()
                                print("found fine match "," char_x",self.grid_info.char_size_X," char_y",self.grid_info.char_size_Y," X:",x," Y:",y)
                                print("cheking grid")
                                return True
        return False
    
    def find_first_match(self,gap_look,bar):
        max_X_char = int((self.last_screen.size[0]/(self.grid_info.bins_X-1))+1)
        max_Y_char = int((self.last_screen.size[1]/(self.grid_info.bins_Y-1))+1)
        flag = False
        for x in range(0,self.last_screen.size[0],gap_look):
            for y in range(0,self.last_screen.size[1],gap_look):
                for char_x in range(gap_look,max_X_char):
                    bar.refresh()
                    for char_y in range(gap_look,max_Y_char):
                        if x+char_x*(self.grid_info.bins_X+1) < self.last_screen.size[0] and y+char_y*(self.grid_info.bins_Y+1) < self.last_screen.size[1] :
                            self.grid_info.set(x,y,char_x,char_y)
                            if self.try_match(self.grid_info):
                                bar.complete()
                                print("found first match "," char_x",char_x," char_y",char_y," X:",x," Y:",y)
                                return True
        return False
    
    def try_match(self, grid_info):
        horizontal_T = self.BW_mtx[  grid_info.start_X::grid_info.char_size_X ,     grid_info.start_Y    ]
        horizontal_T = horizontal_T[0:grid_info.bins_X]
        if np.array_equal(horizontal_T,self.line_T_x_to_match):
            vertical_L = self.BW_mtx[  grid_info.start_X,     grid_info.start_Y::grid_info.char_size_Y    ]
            vertical_L = vertical_L[0:grid_info.bins_Y]
            if np.array_equal(vertical_L,self.line_L_y_to_match):
                horizontal_B = self.BW_mtx[  grid_info.start_X::grid_info.char_size_X ,     grid_info.start_Y  + grid_info.char_size_Y*(grid_info.bins_Y-1)  ]
                horizontal_B = horizontal_B[0:grid_info.bins_X]
                if np.array_equal(horizontal_B,self.line_B_x_to_match):
                    vertical_R = self.BW_mtx[  grid_info.start_X + grid_info.char_size_X*(grid_info.bins_X-1),     grid_info.start_Y::grid_info.char_size_Y    ]
                    vertical_R = vertical_R[0:grid_info.bins_Y]
                    if np.array_equal(vertical_R,self.line_R_y_to_match):
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False

    def process_all_options(self):
        assert self.color_dict != None, "Null color config file"
        for k,v in self.color_dict["background"].items():
            self.color_dict["background"][k] = f"\033[{v}"
        for k,v in self.color_dict["foreground"].items():
            self.color_dict["foreground"][k] = f"\033[{v}"
        self.all_options = []
        for back in self.color_dict["background"]:
            for fore in self.color_dict["foreground"]:
                for char in self.color_dict["characters"]:
                    self.all_options.append(str(self.color_dict["foreground"][fore])+str(self.color_dict["background"][back])+str(char))

def write(s):
    sys.stdout.write(s)

def move_cursor(col,row):
    sys.stdout.write(f"\033[{int(row)};{int(col)}H")

def refresh_screen():
    sys.stdout.buffer.flush()
    sys.stdout.flush()

class Grid_info:
    start_X = int(0)
    start_Y = int(0)
    char_size_X = int(1)
    char_size_Y = int(1)
    bins_X = int(1)
    bins_Y = int(1)
    def __init__(self):
        self.start_X = int(0)
        self.start_Y = int(0)
        self.char_size_X = int(1)
        self.char_size_Y = int(1)
        self.bins_X = int(1)
        self.bins_Y = int(1)

    def set(self,start_X,start_Y,char_size_X,char_size_Y):
        self.start_X = int(start_X)
        self.start_Y = int(start_Y)
        self.char_size_X = int(char_size_X)
        self.char_size_Y = int(char_size_Y)

class LoadBar:
    animation = ["\\","|","/","-"]
    animation_cnt = 0
    def __init__(self,info,end_value,start_value=0,reverse=False):
        self.terminal_size = os.get_terminal_size()
        self.info = info
        self.actual_value = start_value
        self.start_value = start_value
        self.end_value = end_value
        self.line_len = self.terminal_size.columns - 1 
        self.reverse = reverse
        self.pr()

    def refresh(self,val=None):
        if val:
            self.actual_value = val
        self.pr()

    def pr(self):
        move_cursor(0,self.terminal_size.lines)
        s = f"{self.info}:{self.actual_value}|{Fore.GREEN}"
        remaining_ch = self.line_len-len(s)-1
        if not self.reverse:
            l = int(remaining_ch*(self.actual_value/self.end_value))
        else:
            l = int(remaining_ch*(1 - self.actual_value/self.start_value))
        s += "#"*l
        s += " "*(remaining_ch-l)
        s += f"{Fore.RESET}{self.animation[self.animation_cnt]}"
        s = s + " "*(self.terminal_size.columns-len(s))
        write(s)
        refresh_screen()
        self.animation_cnt = self.animation_cnt + 1 if self.animation_cnt < len(self.animation) - 1 else 0

    def complete(self):
        move_cursor(0,self.terminal_size.lines)
        s = f"{self.info}:{self.actual_value}  {Fore.GREEN}DONE"
        s = s + " "*(self.terminal_size.columns-len(s))
        write(s)
        print()
        refresh_screen()

