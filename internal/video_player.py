import os
import time
from pathlib import Path


def clear_screen():
    print("\033[J", end="",flush=True)  # move cursor home + clear screen

def start_position():
    print("\033[H", end="")  # move cursor home + clear screen

DELAY = 1/30  # seconds
def play_video(path):
    files = sorted(Path(path).iterdir())

    clear_screen()
    for file in files:
        start_position()
        with open(file, "r", encoding="utf-8") as f:
            print(f.read(), end="")

        time.sleep(DELAY)

