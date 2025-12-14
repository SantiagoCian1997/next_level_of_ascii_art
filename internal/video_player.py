import os
import argparse
import time
from pathlib import Path
import sys 


def move_cursor(row: int, col: int):
    sys.stdout.write(f"\033[{row};{col}H")
    sys.stdout.flush()

def clear_screen():
    print("\033[J", end="",flush=True)  # move cursor home + clear screen

def start_position():
    print("\033[H", end="")  # move cursor home + clear screen

def play_video(path, frame_rate = 30, loop = False):
    files = sorted(Path(path).iterdir())

    size_terminal = os.get_terminal_size()
    with open(files[0], "r", encoding="utf-8") as f:
        frame_height = len(f.read().split('\n'))
    for i in range(frame_height):
        print()

    start_line = size_terminal.lines - frame_height
    move_cursor(start_line,0)

    while True:
        for file in files:
            move_cursor(start_line,0)
            with open(file, "r", encoding="utf-8") as f:
                print(f.read(), end="")

            time.sleep(1/float(frame_rate))
        if not loop:
            break

def main(argv=None):
    parser = argparse.ArgumentParser(description="to play your ASCII art videos ")
    parser.add_argument("directory_to_use",         help="Dumped directory")
    parser.add_argument("-fr",     "--frame_rate",  help="To set the delay time", default = 30)
    parser.add_argument("-loop",   "--loop",        help="Loop", action="store_true")
    args = parser.parse_args(argv)

    play_video(args.directory_to_use,args.frame_rate,args.loop)


if __name__ == "__main__":
    main()