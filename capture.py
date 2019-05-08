######TODO

import os
import screen
from pathlib import Path
from InputListener import InputListener


def file_manager(path, cwd = Path.home() / "pynee"):
    new_path = cwd / path
    if(new_path.is_dir()):
        return new_path / unique_file(new_path, path)
    else:
        os.mkdir(new_path)
        return new_path / unique_file(new_path, path)


def unique_file(directory, script):
    counter = 0
    while True:
        counter += 1
        path = directory / "{0}{1}.macro".format(script, counter)
        if not path.exists():
            return path

if __name__ == "__main__":
    file = file_manager(input("script: "))
    print(file)
    offset = None
    try:
        offset = screen.findOSRS()
    except:
        print("couldn't find OSRS instance...")

    if(offset is None):
        offset = [0,0]
    l = InputListener(file, offset)
    l.start()
    keep = input("keep file? ")
    if not keep.strip():
        print("deleting file", file)
        os.remove(file) #clear file

