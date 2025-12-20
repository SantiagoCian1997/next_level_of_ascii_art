

import ctypes
import subprocess
import sys
import os
from pathlib import Path


HERE = Path(__file__).parent
CSRC = HERE / "c_matcher.c"
LIB_NAME = {
    "linux": "c_matcher.so",
    "darwin": "c_matcher.dylib",
    "win32": "c_matcher.dll",
}[sys.platform]

BUILD = HERE / "build"
LIB_PATH = BUILD / LIB_NAME
BUILD.mkdir(exist_ok=True)

def needs_rebuild():
    if not LIB_PATH.exists():
        return True
    return CSRC.stat().st_mtime > LIB_PATH.stat().st_mtime

def compile_c_code():
    print(f"Compiling C library for: {sys.platform}")
    print(f"output file: {LIB_NAME}")

    if sys.platform == "win32":
        raise RuntimeError("Windows build not implemented yet")

    cmd = [
        "gcc",
        "-O3",
        "-shared",
        "-fPIC",
        str(CSRC),
        "-o",
        str(LIB_PATH),
    ]

    subprocess.check_call(cmd)

def load_c_matcher():
    if not LIB_PATH.exists() or needs_rebuild():
        compile_c_code()
    return ctypes.CDLL(str(LIB_PATH))

def c_lib_is_supported():
    p = sys.platform
    if p == "linux":
        return True
        return False
    return False

