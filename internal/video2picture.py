import cv2
import os
from pathlib import Path
import subprocess
import sys
from tqdm import tqdm

def v2p(video_path, output_dir="tmp_video"):
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    frame_number = 0
    frames_files = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        filename = f"frame_{frame_number:012d}.png"
        filepath = os.path.join(output_dir, filename)

        cv2.imwrite(filepath, frame)
        frame_number += 1
        frames_files.append(filepath)


    cap.release()

    return frames_files


def _rmdir(directory):
    if os.path.exists(directory):
        directory = Path(directory)
        for item in directory.iterdir():
            if item.is_dir():
                _rmdir(item)
            else:
                item.unlink()
        directory.rmdir()



class CreateProcess():
    def __init__(self, picture : str, args,output_dumps_path,started_bar,finished_bar):
        self.picture = picture
        self.args = args
        self.started = False
        self.is_running = False
        self.finish = False
        self.output_dumps_path = output_dumps_path
        self.started_bar = started_bar
        self.finished_bar = finished_bar
        self.create_command()

    def create_command(self):
        init_command = [sys.executable, "create_ascii.py"]
        args_command = []
        for ar, value in vars(self.args).items():
            if ar == "picture_file" :
                init_command.append(f"{self.picture}")
            elif ar == "output_dir" : 
                args_command.append(f"--{ar}")
                args_command.append(f"{self.output_dumps_path}")
            elif ar in ["video", "quiet", "verbose"]: 
                pass
            else:
                if value != None:
                    if isinstance(value, bool):
                        if value:
                            args_command.append(f"--{ar}")
                    else:
                        args_command.append(f"--{ar}")
                        args_command.append(f"{value}")
        self.command = init_command + args_command + ["--quiet"]
        self.dump_file = os.path.join(self.output_dumps_path,f"last_run_dump_{Path(self.picture).name.split('.')[0]}.txt")
        if Path.exists(Path(self.dump_file)):
            os.remove(self.dump_file)
        #print(self.command)

    def launch(self):
        self.process = subprocess.Popen(self.command)
        #print(f"running: {' '.join(self.command)}")
        self.started = True
        self.is_running = True
        self.started_bar.update(1)

    def finished(self):
        if self.finish:
            return True
        if self.is_running:
            if Path.exists(Path(self.dump_file)):
                self.finish = True
                self.finished_bar.update(1)
                self.is_running = False
                #print(f"process: {self.dump_file} END")
                return True
        return False

def create_subprocess(args, tmp_dir, simultaneous_process = 18):
    _rmdir(tmp_dir)
    frames_files = v2p(args.picture_file,tmp_dir)
    print(f"total process: {len(frames_files)}")

    n_process = len(frames_files)
    started_bar  = tqdm(total=n_process, position=0, desc="started  ", leave=True)
    finished_bar = tqdm(total=n_process, position=1, desc="finished ", leave=True)
    
    output_dumps_path = f"video_dumps_{Path(args.picture_file).name.split(".")[0]}"
    _rmdir(output_dumps_path)

    process = [CreateProcess(p,args,output_dumps_path,started_bar,finished_bar) for p in frames_files]

    import time
    while True:
        finished_process = [p.finished() for p in process]
        if all(finished_process):
            break

        n_running_process = len([None for p in process if p.is_running])
        while n_running_process < simultaneous_process and not all(finished_process):
            for p in process:
                if not p.started:
                    p.launch()
                    break
            n_running_process = len([None for p in process if p.is_running])
            finished_process = [p.finished() for p in process]
        
        # n_running_process = len([None for p in process if p.is_running])
        # n_finished_process = len([None for p in process if p.finish])
        # n_started_process = len([None for p in process if p.started])
        # print(f"N: {len(process)}, started: {n_started_process}, running: {n_running_process}, finished: {n_finished_process}")
        
        time.sleep(0.8)

    started_bar.close()
    finished_bar.close()

    _rmdir(tmp_dir)

    print(f"the results are stored in the directory: {output_dumps_path}")
    print(f"to play it use:")
    print(f" python internal/video_player.py {output_dumps_path}")
    
    return output_dumps_path


