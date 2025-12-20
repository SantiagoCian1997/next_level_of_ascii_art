

import ctypes
import subprocess
import sys
import shutil
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
VERBOSE = False

def needs_rebuild():
    if not LIB_PATH.exists():
        return True
    return CSRC.stat().st_mtime > LIB_PATH.stat().st_mtime


PLATFORM_CONFIG = {
    "linux": {
        "lib": "c_matcher.so",
        "compiler": "gcc",
        "cflags": ["-O3", "-shared", "-fPIC"],
    },
    "darwin": {
        "lib": "c_matcher.dylib",
        "compiler": "clang",
        "cflags": ["-O3", "-shared", "-fPIC"],
    },
    "win32": {
        "lib": "c_matcher.dll",
        "compiler": "gcc",  # MinGW / MSYS2
        "cflags": ["-O3", "-shared"],
    },
}

def set_loader_verbose(verbose = False):
    global VERBOSE
    VERBOSE = verbose

def get_platform_config():
    return PLATFORM_CONFIG[sys.platform]

def compile_c_code():
    cfg = get_platform_config()

    compiler = shutil.which(cfg["compiler"])
    if compiler is None:
        raise RuntimeError(f"Compiler '{cfg['compiler']}' not found in PATH")

    if VERBOSE:
        print(f"Compiling C library for: {sys.platform}")
        print(f"Compiler: {compiler}")
        print(f"Output: {LIB_PATH}")

    cmd = [
        compiler,
        *cfg["cflags"],
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
    return sys.platform in PLATFORM_CONFIG.keys()

