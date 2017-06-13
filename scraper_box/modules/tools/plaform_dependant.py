import os
import platform

osys = platform.system()


def clear_screen():
    if "Windows" in osys:
        _ = os.system('cls')
    if "Linux" in osys:
        _ = os.system('clear')
