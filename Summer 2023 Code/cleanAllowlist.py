"""
Margie Ruffin 
IBM Summer 2023
Script to go thrugh allowlist and remove the prefix '/snap/core20/' 
from the files. May solve the hash not matching and file not found errors
"""

import argparse
import sys

def cleanAllowlist(allowlist):
    with open(allowlist, "r") as f:
        file = []
        for line in f: 
            file.append(line)

    newlist = []
    #appeand each line to the new list, if it has the snap core path change string and append to the new file
    for i in file:
        if "/snap/core20/1623" in i: 
            new_line = i.replace('/snap/core20/1623', '') 
            newlist.append(new_line)

        elif "/snap/core20/1891" in i:
            new_line = i.replace('/snap/core20/1891', '')
            newlist.append(new_line)
        else:
            newlist.append(i)
 
    return newlist



def main():
    # take log file in arg 
    parser = Parser()
    parser.add_argument("-a", "--allowlist", help="Path to allowlist",required = True, action="store")
    parser.add_argument("-o", "--output_file", help="Output file path",required = True, action="store")

    # print help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()


    if args.allowlist:
        new_allow = cleanAllowlist(args.allowlist)
    # print help if no the main arg isn't provided    
    else:
        parser.print_help()
        parser.exit()


    if args.output_file.endswith(".txt"):
        with open(args.output_file, "w+") as f:
            for line in new_allow:
                f.write(line)
        f.close()

class Parser(argparse.ArgumentParser):
    def error(self, message: str):
        sys.stderr.write(f"error: {message}\n")
        self.print_help(sys.stderr)
        sys.exit(2)



if __name__ == "__main__":
    main()
