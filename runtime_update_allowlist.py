'''
Margie Ruffin 
IBM Summer 2023
Generate Updated Allowlist for Continious
Runtime Integrity Monitoring
'''

'''
How to run this script if you have amd64 Architecture working with Ubuuntu's Jammy

python3 runtime_update_allowlist.py -x -v jammy -g

'''

import os, shutil
import os.path
import argparse
import sys
import hashlib
import requests
import gzip
import shutil
import subprocess
import time

'''
must have zstd installed. For Mac == brew install zstd
'''

def download_new_release_files(path, filename):
    try:        
        r = requests.get(path)
        open(filename , 'wb').write(r.content)
        with gzip.open(filename, 'rb') as f_in:
            with open(filename.replace('.gz', ''), 'wb') as f_out:
                print(">>>> Opening File " + filename + "...")
                shutil.copyfileobj(f_in, f_out)
        print(">>>> Extracting file from " + filename + "...")
    except:
        print(">>>> The " +  filename + "Package file was not able to be downloaded and/or extracted")
    return

# download new ubuntu release put indide /tmp/allowlist_config folder on machine
def dowload_new_release(amd, intel, version, update, generate):

    #navigate to the /tmp/ dir and create a new dir for allowlist files
    if os.path.exists('/tmp/'):
        os.chdir('/tmp/')
    else:
        os.mkdir('/tmp/')
        os.chdir('/tmp/')

    if os.path.exists('/tmp/allowlist_config/'):
        os.chdir('/tmp/allowlist_config/')
    else:
        os.mkdir('allowlist_config/')
        os.chdir('allowlist_config/')

    if amd == True:
        binary = "binary-amd64"
    if intel == True:
        binary = "binary-i386"

    mname = 'MainRepo.gz'
    rname = 'UpdatePackage.gz'
    sname = 'SecurityPackage.gz'

    main_path = 'http://archive.ubuntu.com/ubuntu/dists/' + version + '/main/' + binary + '/Packages.gz'
    regular_path = 'http://archive.ubuntu.com/ubuntu/dists/' + version + '-updates/main/' + binary + '/Packages.gz'
    security_path = 'http://archive.ubuntu.com/ubuntu/dists/' + version + '-security/main/' + binary + '/Packages.gz'
    
    try:
        if update == True:
            print(">>>> Moving old files over")
            # check to see if the packages already exist, if so rename old ones to Name_Old.gz or Name_Old and then write down the new ones
            if os.path.isfile('/tmp/allowlist_config/SecurityPackage.gz'):
                os.rename('/tmp/allowlist_config/SecurityPackage.gz', '/tmp/allowlist_config/SecurityPackage_Old.gz')
                os.rename('/tmp/allowlist_config/SecurityPackage', '/tmp/allowlist_config/SecurityPackage_Old')
            if os.path.isfile('/tmp/allowlist_config/UpdatePackage.gz'):
                os.rename('/tmp/allowlist_config/UpdatePackage.gz', '/tmp/allowlist_config/UpdatePackage_Old.gz')
                os.rename('/tmp/allowlist_config/UpdatePackage', '/tmp/allowlist_config/UpdatePackage_Old')
            print(">>>> Downloading and files")
            download_new_release_files(regular_path, rname)
            download_new_release_files(security_path, sname)

        if generate == True:
            print(">>>> Downloading new files")
            download_new_release_files(main_path, mname)
            download_new_release_files(regular_path, rname)
            download_new_release_files(security_path, sname)

    except:
        print(">>>> Error: No files downloaded")
    return

# compare the previous release stored on your machine to the current release. Find the differneces and target those for the update
def create_diff_release(currentFileDict, fileType):
    print(">>>> Loading up Old Package Files")
    # load up old file and 
    if fileType == 'update':
        filePath = '/tmp/allowlist_config/UpdatePackage_Old'
    if fileType == 'security':
        filePath = '/tmp/allowlist_config/SecurityPackage_Old'

    finalDict = {}
    finalList = []
    # returns a dictionary
    oldFileDict = clean_package_file(filePath)
    
    print(">>>> Comparing Old to New Package File")
    oldFileList = list(oldFileDict.keys())
    curentFileList = list(currentFileDict.keys())

    count = 0 
    # see if there are pkgs in NEW that aren't in the OLD  
    for name in curentFileList:
        if name not in oldFileList:
            finalList.append(name)
            count += 1
    print(">>>> " + str(count) + " " + fileType + " packages have been add to the repo")

    count2 = 0 
    # see if the version of the pkg has changed
    for i in currentFileDict:
        if currentFileDict[i] in oldFileList:
            pkgname = currentFileDict[i] 
            if currentFileDict[i]['Version'] != oldFileDict[pkgname]['Version']:
                finalList.append(pkgname)
                count +=1 
    print(">>>> " + str(count2) + " " + fileType + " packages have been updated")
    # for each pkg in the final list add the pkgname as the key and the valueDict as the value
    for i in finalList:
        finalDict[i] = currentFileDict[i]

    return  finalDict

# create a new file with file paths and Sha256Sum of the targeted files
def create_allowlist_update(updateDict, filter_exec):
    if os.path.exists('temp/'):
            os.chdir('temp/')
    else:
        os.mkdir('temp/')
        os.chdir('temp/')

    hashDict = {}
    for i in updateDict:
        # for each package in the list, pull down their updated debian file
        path = 'http://archive.ubuntu.com/ubuntu/' + updateDict[i]['Filename'].strip()
        name = updateDict[i]['Filename'].split("/")[-1]
        startDir = "/tmp/allowlist_config/temp/"
        pkgname = name.replace(".deb", "")
        print()
        print(">>> Package Name: " + pkgname)

        # extract the files we want to measure
        updatesList = create_paths_list(path, name)
        # go into the dir of the extracted debian package
        os.chdir(pkgname)
        
        # iterate through each file in the .deb dir and take a measurement
        for k in updatesList:
            fileDir = k.split('/')
            fileDir = "/".join(fileDir[:-1])
            #fileDir = k.replace(k.split('/')[-1], "")
            #print(fileDir)
            os.chdir(fileDir)
            #path = os.getcwd()
            #print(path)
            file_name = k.replace("./", startDir + pkgname + "/")

            #somewhere in here filter out .exec files... Does it matter who can execute the file???  ################################################
            # https://stackoverflow.com/questions/1861836/checking-file-permissions-in-linux-with-python#:~:text=You%20can%20check%20file%20permissions,module%20for%20interpreting%20the%20results.&text=Use%20os.,access()%20with%20flags%20os.#


            # do a check to see if the file is a symlink
            if os.path.islink(file_name):
                print("This " + file_name + " is a symlink")
                #if it is, try to resolve it. If it isn't dangling
                real_path = os.path.realpath(file_name)
                print(real_path)
                check_file = os.path.isfile(real_path)
                if check_file == True:
                    print(">>>> This file " + file_name + " is a symlink and can be resolved.... Do not Ignore")
                    hash = take_measurement(file_name, k)
                    os.chdir(startDir + pkgname)
                else:
                    print(">>>> This file " + file_name + " is an unresolved symlink.... Ignore")  
                    os.chdir(startDir + pkgname)
                    continue       
            else:
                hash = take_measurement(file_name, k)
                os.chdir(startDir + pkgname)

            policyPath = k.replace("./", "/")
            #print(policyPath)
            hashDict[policyPath] = hash

        # write the dictonary filled with measurements to a file
        write_allowlist(hashDict)
        # cleanup temp dir
        cleanup(startDir)
    return 

def take_measurement(file_name, k):
    #hash the file        
    hash_sha256 = hashlib.sha256()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
            global hash
            hash = hash_sha256.hexdigest()
    print(">>>> Filename " + k + "  " + hash)
    return hash

# create a list of file paths for each file in .deb package
def create_paths_list(path, name):
    # list of paths for each debian package
    r = requests.get(path)
    open(name , 'wb').write(r.content)
    time.sleep(3) ### Is this long enough??? DoSed the system

    result = subprocess.run(['dpkg-deb', '-X', name, name.replace('.deb', '')], stdout=subprocess.PIPE).stdout.decode('utf-8')
    #print(result)

    pathsList = result.splitlines()
    #print(pathsList)
    trash = []
    for i in range(len(pathsList)):
        if pathsList[i].endswith("/"):
            trash.append(pathsList[i])
        else:
            print(">>> File to measure: " + pathsList[i])
        
    s = set(trash)
    cleanList = [x for x in pathsList if x not in s]
    #print(cleanList)
    #print(len(cleanList))
    return cleanList

# creates nested dictionary of all packages {package: {spec:description}}
def out_dict_add(outDict, outList):
    # take out the name of package
    pkgName = outList[0].strip().split(":", 1)
    newDict = {}
    for item in outList:
        # go through list and add to new dic
        description = list(item.strip().split(":", 1))
        newDict[description[0]] = description[1]

    outDict[pkgName[1]] = newDict
    return outDict

# setup to clean the .txt pkg file
def clean_package_file(filePath):
    # convert the .txt file into a nested dictornary
    with open(filePath) as f:
        # all lines from package file
        lines = f.readlines()

    outDict = {}
    outList = []

    for i in lines:
        # while not at a new line/space create a new list and add update package details
        if i != "\n":
            outList.append(i)
        else:
            # send empty dictionary and full list for each package
            outDict = out_dict_add(outDict, outList)
            outList = []
            continue
    # full dict of all packages
    return outDict

# write allowlist to file
def write_allowlist(hashDict):
    # if this file doesn't exisit we will create it and begin appending measurements to it.
    # if it does exisit already (have previously run this script) then simply open it and append to it
    print(">>>> Writing package to allowlist")
    with open("/tmp/allowlist_config/myfile.txt", "a+") as f:
        for i in hashDict:
            f.write(hashDict[i] + "  " + i + "\n")
    f.close()
    return

# cleanup whatever directory needs it
def cleanup(dir):
    # delete contents of /tmp/allow_config/temp/ folder to prepare memory space for the next one
    print(">>>> Cleaning up files")
    for f in os.listdir(dir):
        path = os.path.join(dir, f)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)    

    os.chdir(dir)
    return

def main():
    ## Based on the options that they give us, archtiecture & ubutntu version (name) we can navigate to the right link ##

    ## Options: ubuuntu version name | archtiecture x68 or i386 | update v new generation | *** output file name ***
    parser = Parser()
    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument("-x", "--amd64", help="Architecture Type amd64", action="store_true")
    group1.add_argument("-i", "--i386", help="Architecture Tyoe i386", action="store_true")

    parser.add_argument("-v","--version", help="Current Ubuntu Version Name (ex. jammy)", action="store")
    parser.add_argument("-e","--exec", help="Filter Only Executable Files", action="store_true")


    group2 = parser.add_mutually_exclusive_group(required=True)
    group2.add_argument("-u", "--update", help="Update exisiting main allowlist with new releases", action="store_true")
    group2.add_argument("-g", "--generate", help="Create new release allowlist to append to main Allowlist", action="store_true")

    #parser.add_argument("-o", "--output_file", help="Output file path",required = True, action="store")

    # print help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()
    dowload_new_release(args.amd64, args.i386, args.version, args.update, args.generate)
    
    # clean the package files (i.e. turn them into easily readable dictionaries)
    mainPath = '/tmp/allowlist_config/MainRepo'
    updatePath = '/tmp/allowlist_config/UpdatePackage'
    securityPath = '/tmp/allowlist_config/SecurityPackage'
    # returns a dictionary
    mainDict = clean_package_file(mainPath)
    updateDict = clean_package_file(updatePath)
    securityDict = clean_package_file(securityPath)
    
    # either generate a new release update and append or update previous allowlist
    if args.generate:
        print()
        print(">>> Measuring the Main Repository....\n")
        create_allowlist_update(mainDict, args.exec)
        print()
        print(">>> Measuring the Update Repository....\n")
        create_allowlist_update(updateDict, args.exec)
        print()
        print(">>> Measuring the Security Repository....\n")
        create_allowlist_update(securityDict, args.exec)

    elif args.update:
       # returns the difference between the two files
       update = create_diff_release(updateDict, fileType='update')
       security = create_diff_release(securityDict, fileType='security')

       create_allowlist_update(update, args.exec)
       create_allowlist_update(security, args.exec)

class Parser(argparse.ArgumentParser):
    def error(self, message: str):
        sys.stderr.write(f"error: {message}\n")
        self.print_help(sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()

'''
https://www.baeldung.com/linux/bash-check-file-executable

http://archive.ubuntu.com/ubuntu/dists/jammy-updates/main/binary-amd64/Packages.gz
http://archive.ubuntu.com/ubuntu/dists/jammy-updates/main/binary-i386/Packages.gz

http://archive.ubuntu.com/ubuntu/dists/jammy-security/main/binary-amd64/Packages.gz
http://archive.ubuntu.com/ubuntu/dists/jammy-security/main/binary-i386/Packages.gz

Use final Packages files either a fresh one or the diffed one to pull down the package one at a time
before we untar it, capture the output of dpkg -l into a list and parse out all the files
https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output

with open(file_name) as f:
    data = f.read()
    sha256hash = hashlib.sha256(data.encode('utf-8')).hexdigest()
    print (sha256hash)
'''

"""     if amd == True: 
    try: 
        update_path = 'http://archive.ubuntu.com/ubuntu/dists/' + version + '-updates/main/binary-amd64/Packages.gz'
        security_path = 'http://archive.ubuntu.com/ubuntu/dists/' + version + '-security/main/binary-amd64/Packages.gz'

        try:        
            r = requests.get(update_path)
            open(uname , 'wb').write(r.content)
            with gzip.open(uname, 'rb') as f_in:
                with open('UpdatePackage', 'wb') as f_out:
                    print(">>>>Opening File " + uname + "...")
                    shutil.copyfileobj(f_in, f_out)
            print(">>>> Extracting file from " + uname + "...")
        except:
            print(">>>> The Update Package file was not able to be downloaded and/or extracted")

        try: 
            q = requests.get(security_path)
            open(sname , 'wb').write(q.content)
            with gzip.open(sname, 'rb') as f_in:
                with open('SecurityPackage', 'wb') as f_out:
                    print(">>>> Opening File " + sname + "...")
                    shutil.copyfileobj(f_in, f_out)
            print(">>>> Extracting file from " + sname + "...")
        except:
            print(">>>> The Security Package file was not able to be downloaded and/or extracted")
    except:
        print(">>>> Error: No files downloaded") """

"""     if intel == True:
    try:
        update_path = 'http://archive.ubuntu.com/ubuntu/dists/' + version + '-updates/main/binary-i386/Packages.gz'
        security_path = 'http://archive.ubuntu.com/ubuntu/dists/' + version + '-security/main/binary-i386/Packages.gz'

        try:        
            r = requests.get(update_path)
            open(uname , 'wb').write(r.content)
            with gzip.open(uname, 'rb') as f_in:
                with open('UpdatePackage', 'wb') as f_out:
                    print(">>>> Opening File " + uname + "...")
                    shutil.copyfileobj(f_in, f_out)
            print(">>>> Extracting file from " + uname + "...")
        except:
            print(">>>> The Update Package file was not able to be downloaded and/or extracted")

        try: 
            q = requests.get(security_path)
            open(sname , 'wb').write(q.content)
            with gzip.open(sname, 'rb') as f_in:
                with open('SecurityPackage', 'wb') as f_out:
                    print(">>>> Opening File " + sname + "...")
                    shutil.copyfileobj(f_in, f_out)
            print(">>>> Extracting file from " + sname + "...")
        except:
            print(">>>> The Security Package file was not able to be downloaded and/or extracted")
    except:
        print(">>>> Error: No files downloaded") """