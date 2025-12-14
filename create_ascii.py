#!.venv/bin/python
import argparse
import pprint
from colorama import Fore,Back,Style
from internal.create_cl import Create
from PIL import Image,ImageDraw
import os
import pickle
from pathlib import Path


parser = argparse.ArgumentParser(description="ASCII art at next level ")
parser.add_argument("picture_file",             help="the input image")                                          # positional argument
parser.add_argument("-C",     "--calibration",  help="calibration file", default="calibrations/cal_default.pkl") # optional argument
parser.add_argument("-c",     "--columns",      help="Column output number")                                     # optional argument
parser.add_argument("-r",     "--rows",         help="Rows output number")                                       # optional argument
parser.add_argument("-v",     "--verbose",      action="store_true",help="Enable verbose mode")                  # flag
parser.add_argument("-q",     "--quality",      choices=["fast", "medium", "slow"], help="Quality of the interfering", default="medium")
parser.add_argument("-video", "--video",        action="store_true",help="Video processing")                     # flag
parser.add_argument("-od",    "--output_dir",   help="Specify output directory", default=".")                                       # optional argument
parser.add_argument("-quiet", "--quiet",        action="store_true",help="No printing process")                                       # flag
args = parser.parse_args()

size_terminal = os.get_terminal_size()
if   args.columns:               grid_size = [int(args.columns)     , size_terminal.lines ]
elif args.rows:                  grid_size = [size_terminal.columns , int(args.rows)      ]
elif args.columns and args.rows: grid_size = [int(args.columns)     , int(args.rows)      ]
else :                           grid_size = [size_terminal.columns , size_terminal.lines ]
with open(args.calibration, 'rb') as file:
    calibration = pickle.load(file)


if not args.video:
    image_input = Image.open(args.picture_file)
    cr = Create(image_input, grid_size, args.quality, calibration, args.verbose, args.quiet)
    cr.start_infer()
    _name = Path(args.picture_file).name.split(".")[0]
    dump_file = f"last_run_dump_{_name}.txt"
    os.makedirs(args.output_dir, exist_ok=True)
    dump_path = os.path.join(args.output_dir,dump_file)
    cr.dump_to_file(dump_path)
else :
    from internal.video2picture import create_subprocess
    from internal.video_player import play_video
    tmp_dir = "tmp_video"
    output_dir = create_subprocess(args,tmp_dir,simultaneous_process=8)

    play_video(output_dir)

    
    



