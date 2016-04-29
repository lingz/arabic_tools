#!/usr/bin/python3

from __future__ import print_function
import argparse
from arabic_letters import letters
import string
import sys

if sys.version_info <= (3,0):
    print("This program only runs in python3", file=sys.stderr)
    exit(1)

def main():
    args = argparser.parse_args()
    field = args.field
    seperator = args.seperator
    verbose = args.verbose
    whitespace = set(string.whitespace)
    skipped = 0
    for line in sys.stdin:
        to_filter_on = ""
        if field == -1:
            to_filter_on = line
        else:
            to_filter_on = line.split(seperator)[field - 1]
        if len(to_filter_on.strip()) < 1:
            if verbose:
                skipped += 1
                print("Skipping line because it is empty", file=sys.stderr)
            continue
        include = True
        for char in to_filter_on:
            if char == ".":
                continue
            if char not in letters and char not in whitespace:
                if verbose:
                    skipped += 1
                    print("Skipping line %s because of char %s" %
                            (line.strip(), char), file=sys.stderr)
                include = False
                break
        if include:
            print(line, end="")
    if verbose:
        print("Num skipped: %d" % skipped, file=sys.stderr)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
            description="Removes terms that have non arabic characters in " +
            "them. Reads from STDIN and pipes to STDOUT. Can filter entire " +
            "line based on one column also.")
    argparser.add_argument('-f', '--field', type=int, default=-1,
        help='Which field to filter the line on (defaults to entire line). ' +
             'Index starts at 1.')
    argparser.add_argument('-s', '--seperator', type=str, default="\t",
        help='The seperator for the fields (default: tab)')
    argparser.add_argument('-v', '--verbose', action="store_true",
        help='Show the discarded characters')
    main()

