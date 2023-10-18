"""Margie Ruffin 
IBM Summer 2023
File to parse through Keylime Verifier Log file. 
Will parse contents into a .csv file"""

import argparse
import sys
import csv


def parseLogErrors(log_file):
    with open(log_file, "r") as f:
        file = []
        for line in f: 
            if """'], '""" in line:
                #split at the colon and add the items to the list individually
                split = line.split(",")
                for i in split:
                    file.append(i)
            else:
                file.append(line)

        clean_file = []
        trash = []

        for line in file:
            if line.startswith(""" '/""") and line.endswith("""']""") or line.endswith("""']""") or line.startswith(""" '/"""):
                trash.append(line)
            else:
                clean_file.append(line)

    return clean_file


def parseLog(log_file):
    with open(log_file, "r") as f:
        file = []
        for line in f: 
            if """'], '""" in line:
                #split at the colon and add the items to the list individually
                split = line.split(",")
                for i in split:
                    file.append(i)
            else:
                file.append(line)

    return file

def main():
    # take log file in arg 
    parser = Parser()
    parser.add_argument("-f", "--logfile", help="Path to Verifier log file",required = True, action="store")
    parser.add_argument("-o", "--output_file", help="Output file path",required = True, action="store")
    parser.add_argument("-e","--errors", help="Errors only in Output", action="store_true")
    parser.add_argument("-a", "--all", help="Include all things in Output", action="store_true")

    # print help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    # if you don't specify that you just want the errors it will give that all output
    args = parser.parse_args()
    if args.logfile and args.errors:
        log_out = parseLogErrors(args.logfile)
    else:
        log_out = parseLog(args.logfile)


    if args.output_file.endswith(".txt"):
        with open(args.output_file, "w+") as f:
            for line in log_out:
                f.write("%s\n" % line)

    elif args.output_file.endswith(".csv"):
        with open(args.output_file, "w+") as f:
            csvwriter = csv.writer(f) 
            csvwriter.writerows(log_out)

        f.close()

class Parser(argparse.ArgumentParser):
    def error(self, message: str):
        sys.stderr.write(f"error: {message}\n")
        self.print_help(sys.stderr)
        sys.exit(2)



if __name__ == "__main__":
    main()