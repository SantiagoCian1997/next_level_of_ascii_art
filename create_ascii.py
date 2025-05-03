#!.venv/bin/python
import argparse
import pprint
from colorama import Fore,Back,Style
from internal.create_cl import Create
from PIL import Image,ImageDraw
import os
import pickle

parser = argparse.ArgumentParser(description="ASCII art at next level ")
parser.add_argument("picture_file",         help="the input image")                                          # positional argument
parser.add_argument("-C", "--calibration",  help="calibration file", default="calibrations/cal_default.pkl") # optional argument
parser.add_argument("-c", "--columns",      help="Column output number")                                     # optional argument
parser.add_argument("-r", "--rows",         help="Rows output number")                                       # optional argument
parser.add_argument("-v", "--verbose",      action="store_true",help="Enable verbose mode")                  # flag
parser.add_argument("-q", "--quality",      choices=["fast", "medium", "slow"], help="Quality of the interfering", default="medium")
args = parser.parse_args()

image_input = Image.open(args.picture_file)
size_terminal = os.get_terminal_size()
if   args.columns:               grid_size = [int(args.columns)     , size_terminal.lines ]
elif args.rows:                  grid_size = [size_terminal.columns , int(args.rows)      ]
elif args.columns and args.rows: grid_size = [int(args.columns)     , int(args.rows)      ]
else :                           grid_size = [size_terminal.columns , size_terminal.lines ]
with open(args.calibration, 'rb') as file:
    calibration = pickle.load(file)

cr = Create(image_input, grid_size, args.quality, calibration, args.verbose)
cr.start_infer()
cr.dump_to_file(f"last_run_dump_{args.picture_file.split("/")[-1].split(".")[0]}.txt")
