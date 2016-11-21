#!/usr/bin/python3

from __future__ import print_function
import sys
import json
import argparse
import os
import subprocess
import re
import itertools
from arabic_diacritics import diacritics

if sys.version_info <= (3,0):
    print("This program only runs in python3", file=sys.stderr)
    exit(1)

def is_subseq(x, y):
    it = iter(y)
    return all(any(c == ch for c in it) for ch in x)

def main():
    args = argparser.parse_args()
    mode = args.mode
    single_word_mode = args.single
    first_mode = args.first
    if mode not in ["one2one", "one2many"]:
        print("Invalid mode: can only accept one2one and one2many",
                file=sys.stderr)
        exit(1)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    words = []
    vowels = set(["", "", "", "", ""])
    for line in sys.stdin:
        line = line.strip()
        line = re.sub("\s", " ", line)
        line = "".join(map(
            lambda x: x if x.isalpha() or x in diacritics else "", line))
        words.append(line.strip())
    with open(os.path.join(script_dir, "scratch.in"), "w") as f:
        f.writelines(map(lambda x: x + "\n", words))
    process = subprocess.Popen([
        "java",
        "-cp",
        "%s:%s" % (os.path.join(script_dir, "ArabicAnalyzer.jar"),
                   os.path.join(script_dir, "commons-collections.jar")),
        "gpl.pierrick.brihaye.aramorph.AraMorph",
	"scratch.in",
        "UTF-8",
        "scratch.out",
        "UTF-8",
        "-v"], stdout=subprocess.PIPE, cwd=script_dir)
    for line in process.stdout:
        print(line.decode("utf-8"), end="", file=sys.stderr)
    output = ""
    with open(os.path.join(script_dir, "scratch.out")) as f:
        output = f.read()
    matches = []
    # Question marks are to correctly handle null matches
    for match in re.finditer(r"Processing token : \t(.*)\n", output):
        matches.append({
            "word": match.group(1),
            "start": match.start(0),
            "diacritizations": set()
        })
    # window in which we can search for solutions for the query
    word_index = 0
    for match in re.finditer(r"Vocalized as : \t(.+?)(?:\(.*\))?\n(?:.|\n)+?prefix : (.+?)\n",
            output):
        match_pos = match.start(0)
        prefix = match.group(2)
        if prefix != "Pref-0":
            continue
        # Increment the word index until we are at
        # the end, or the next start index is greater than the
        # current match_pos
        while (not (word_index == (len(matches) -1) or \
                matches[word_index + 1]["start"] > match_pos)):
            word_index += 1
        diacritization = match.group(1)
        if is_subseq(matches[word_index]["word"], diacritization):
            matches[word_index]["diacritizations"].add(diacritization)

    if single_word_mode:
        for word in matches:
            num_diacritizations = len(word["diacritizations"])
            if mode == "one2one" and (num_diacritizations == 1 or \
                    (first_mode and num_diacritizations > 1)):
                print("%s\t%s" % (word["word"], list(word["diacritizations"])[0]))
            elif mode == "one2many" and num_diacritizations > 0:
                for diacritization in word["diacritizations"]:
                    print("%s\t%s" % (word["word"], diacritization))
            else:
                print("%s\t%s" % (word["word"], word["word"]))
    else:
        words = list(map(lambda x: x.split() or [""], words))
        match_index = 0
        for original_word in words:
            out = []
            num_to_print = len(original_word) or 1
            for i in range(num_to_print):
                current = []
                word = matches[match_index]
                if (word["word"] != original_word[i]):
                    print("GOT A PROBLEM", file=sys.stderr)
                    print("%s : %s" % (word["word"], original_word[i]), file=sys.stderr)
                    exit(1)
                num_diacritizations = len(word["diacritizations"])
                if mode == "one2one" and (num_diacritizations == 1 or \
                        (first_mode and num_diacritizations > 1)):
                    current.append(list(word["diacritizations"])[0])
                elif mode == "one2many" and num_diacritizations > 0:
                    for diacritization in word["diacritizations"]:
                        current.append(diacritization)
                else:
                    current.append(original_word[i])
                match_index += 1
                out.append(current)
            if len(out) != len(original_word):
                # Some parsing error, who knows how java splits it
                print("%s\t%s" % (" ".join(original_word), " ".join(original_word)))
            else:
                possible_outs = list(itertools.product(*out))
                for possible_out in possible_outs:
                    print("%s\t%s" % (" ".join(original_word), " ".join(possible_out)))
    
    # Stats for one2one mode
    if mode == "one2one":
        single_word_matches = 0
        for word in matches:
            if len(word["diacritizations"]) == 1:
                single_word_matches += 1
        print("Single Matches: %d / %d (%f%%)" % (single_word_matches, len(matches),
            single_word_matches / len(matches)),
                file=sys.stderr)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
            description="Reads undiacritized/partially diacritized arabic " +
            "from STDIN and pipes undiacritized, diacritized tab seperated " +
            "to STDOUT. Note this won't print to STDOUT until EOF is reached.")
    argparser.add_argument('-m', '--mode', type=str, default="one2one",
        help='[one2one | one2many] (default one2many). For one2one only a ' +
        'single certain match will cause diacritization. one2many will list' +
        'all diacritizations')
    argparser.add_argument('-s', '--single', action="store_true",
        help='Splits multi word phrases into single words')
    argparser.add_argument('-f', '--first', action="store_true",
        help='Always gives the first match (in one2one mode)')
    main()
