#!/usr/bin/python3

from __future__ import print_function
import sys
import json
import argparse
import os
import subprocess
import re
from arabic_diacritics import diacritics

if sys.version_info <= (3,0):
    print("This program only runs in python3", file=sys.stderr)
    exit(1)

def main():
    for line in sys.stdin:
        line = "".join(map(lambda x: x if x not in diacritics else "", line))
        print(line.strip())

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
            description="Reads diacritized arabic " +
            "from STDIN and pipes diacritized, undiacritized tab seperated " +
            "to STDOUT.")
    main()

