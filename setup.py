#!/usr/bin/env python3

import os
import subprocess
import sys
import platform

def main():
    venv_dir = ".venv"
    
    print(f"Creating virtual environment in ./{venv_dir}")
    subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

    if platform.system() == "Windows":
        pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        pip_path = os.path.join(venv_dir, "bin", "pip")

    print("Installing requirements...")
    subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])

    print("Setup complete.")
    print("To activate the virtual environment:")
    if platform.system() == "Windows":
        print(rf"{venv_dir}\Scripts\activate.bat")
    else:
        print(f"source {venv_dir}/bin/activate")

if __name__ == "__main__":
    main()