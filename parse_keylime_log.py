import os
import sys
import datetime

#Turned logging to a file on in local Keylime version, however all components go to the same file
#this script will take the log file and parse it into individual files based on component

#Future work: make logs go to diff files according to componenet type, name files based on date 

#to run this scrpit python3 parse_keylime_log.py /path/to/log/file.log
# python3 ~/Desktop/Keylime/parse_keylime_log.py ~/Desktop/Keylime/logs/keylime_log.log

def parse(line, logFilePath):

    registrar = os.path.join(logFilePath, 'registrar_log_' + str(datetime.date.today()) + '.txt')
    verifier = os.path.join(logFilePath, 'verifier_log_' + str(datetime.date.today()) + '.txt')
    tenant = os.path.join(logFilePath, 'tenant_log_' + str(datetime.date.today()) + '.txt')

    if 'keylime.registrar' in line:
        with open(registrar, 'a+') as f:
            f.write(line)

    elif 'keylime.verifier' in line or 'keylime.ima' in line or 'keylime.tpm' in line:
        with open(verifier, 'a+') as f:
            f.write(line)


    elif 'keylime.tenant' in line:
        with open(tenant, 'a+') as f:
            f.write(line)



def main():
    logFile = sys.argv[1]
    print(logFile)
    logFilePath = logFile.split('/')
    logFilePath = "/".join(logFilePath[:-1])
    print(logFilePath)

    with open(logFile, 'r') as f:
        for line in f:
            #print(line)
            parse(line, logFilePath)


if __name__ == "__main__":
    main()