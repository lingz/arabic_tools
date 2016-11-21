#!/usr/bin/python3
## Helper to make mappings

from __future__ import print_function
import sys
import json


if sys.version_info <= (3,0):
    print("This program only runs in python3", file=sys.stderr)
    exit(1)

def main():
    if len(sys.argv) != 2:
        print("pass in file name")
        exit(1)
    mapping = {}
    print("Arabic: ", end="")
    sys.stdout.flush()
    arabic_line = True
    lastKey = None
    for line in sys.stdin:
        line = line.strip().replace("\u200e", "")
        if not line:
            print("Nothing detected")
            continue
        elif arabic_line and len(line) > 1:
            print("Line len:", len(line))
            continue
        if arabic_line:
            lastKey = line
            print("English: ", end="")
            sys.stdout.flush()
        else:
            mapping[lastKey] = line.strip()
            print("Arabic: ", end="")
            sys.stdout.flush()
        arabic_line = not arabic_line
    with open(sys.argv[1], "wb") as f:
        f.write(json.dumps(mapping, indent=2, ensure_ascii=False).encode("utf-8"))

if __name__ == "__main__":
    main()
