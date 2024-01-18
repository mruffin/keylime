'''
Margie Ruffin
This script will take an already complied Record List (JSON) and convert it into a Keylime Allowlist

python3 generate_allowlist_basic.py -f /path/to/recordlist -o /path/to/dir/of/choice/

'''


import os
import os.path
import argparse
import sys
import json
#from datetime import datetime, date
import datetime


def generateAllowlist(recordFilename, allowlistFilename):

    file = open(allowlistFilename, "w")
    with open(recordFilename) as f:
        for i in f:
            data = json.loads(i.strip())
            print(">>>> Adding Package to Allowlist")
            for x, y in data.items():
                #print(x, y)
                for k, v in data[x]["digests"].items():
                    print(k, v)
                    file.write(v + "  " + k + "\n" )
    file.close()
    return


def main():

    parser = Parser()
    parser.add_argument("-f", "--file", help="allowlistRecord JSON File", action="store")
    parser.add_argument("-o", "--output", help="Output Directory for File", action="store")

     # print help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()
    args = parser.parse_args()

    #record file name
    recordFilename = args.file

    #allowlist file name
    allowlistFiledir = args.output
    allowlistFilename = os.path.join(allowlistFiledir, "allowlist_basic_" + str(datetime.date.today()) + ".txt")

    generateAllowlist(recordFilename, allowlistFilename)


class Parser(argparse.ArgumentParser):
    def error(self, message: str):
        sys.stderr.write(f"error: {message}\n")
        self.print_help(sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()