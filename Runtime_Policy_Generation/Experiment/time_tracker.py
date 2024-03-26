

import json
from datetime import date, datetime
from collections import defaultdict



def main():

    time_log = defaultdict(lambda: defaultdict(dict))

    start_time = datetime.now()

    time_log["start_time"] = start_time

    stop = str(input("Press any char to end the program: "))

    end_time = datetime.now()
    time_log["end_time"] = end_time
    time_log["diff_time"] = end_time - start_time

    with open("/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/Experiment/time_log.json", "a") as f:
        json.dump(time_log, f, default=str)
        f.write(",")
        f.write("\n")


if __name__ == "__main__":
    main()