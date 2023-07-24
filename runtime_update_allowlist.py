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
import stat
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
        print(">>>> The " +  filename + " Package file was not able to be downloaded and/or extracted")
        sys.exit(1)
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

    #Local Computer
    #main_path = 'http://archive.ubuntu.com/ubuntu/dists/' + version + '/main/' + binary + '/Packages.gz'
    #regular_path = 'http://archive.ubuntu.com/ubuntu/dists/' + version + '-updates/main/' + binary + '/Packages.gz'
    #security_path = 'http://archive.ubuntu.com/ubuntu/dists/' + version + '-security/main/' + binary + '/Packages.gz'

    #Mirror Files
    main_path = 'http://100.64.0.12/apt/mirror/archive.ubuntu.com/ubuntu/dists/' + version + '/main/' + binary + '/Packages.gz'
    regular_path = 'http://100.64.0.12/apt/mirror/archive.ubuntu.com/ubuntu/dists/' + version + '-updates/main/' + binary + '/Packages.gz'
    security_path = 'http://100.64.0.12/apt/mirror/archive.ubuntu.com/ubuntu/dists/' + version + '-security/main/' + binary + '/Packages.gz'
    
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
    for i in curentFileList:
        #print(i)
        if i in oldFileList:
            if currentFileDict[i]['Version'] != oldFileDict[i]['Version']:
                finalList.append(i)
                count2 +=1 
    print(">>>> " + str(count2) + " " + fileType + " packages have been updated")
    # for each pkg in the final list add the pkgname as the key and the valueDict as the value
    for i in finalList:
        finalDict[i] = currentFileDict[i]

    return  finalDict

# compare the security pkgs file to the updates pkgs file to see if any have been repeated
def compare_sec_and_update(updateDict, securityDict):

    print(">>>> Comparing the Security to Update Package File")
    updateFileList = list(updateDict.keys())
    securityFileList = list(securityDict.keys())
    duplicateList = []
    finalDict = {}
    count = 0

    '''we need to compare the name and versions of the packages 
    if the filename is found in the 2nd list then go thru the dict and compare the two versions. If they are the same
    take the name out of (remove) both of the lists and put it in the final list,. Keep count of how many are dubplcates.
    then once all are taken out of the lists combine the security and update lists with their unique files and then add the final list to them update final dict'''

    # go through one list and compare the file names. If names and version matches, add to duplicate list and remove from other two lists.
    # we only want to see it once.
    for name in updateFileList:
        if name in securityFileList and updateDict[name]['Version'] == securityDict[name]['Version']:
            duplicateList.append(name)
            updateFileList.remove(name)
            securityFileList.remove(name)
            count += 1

    print('>>>> There are ' + str(len(updateFileList)) + ' unique Update Packages')
    print('>>>> There are ' + str(len(securityFileList)) + ' unique Security Packages')
    print('>>>> There are ' + str(count) + ' duplicate files between Security and Update Releases')
    print('>>>> Creating final list')
    print()

    #create a final dictionary to use
    for i in updateFileList:
        finalDict[i] = updateDict[i]

    for k in securityFileList:
        finalDict[k] = securityDict[k]

    for l in duplicateList:
        finalDict[l] = securityDict[l]
    
    return finalDict

# create a new file with file paths and Sha256Sum of the targeted files
def create_allowlist_update(updateDict, filter_exec):
    global hash
    if os.path.exists('temp/'):
            os.chdir('temp/')
    else:
        os.mkdir('temp/')
        os.chdir('temp/')
    
   
    for i in updateDict:
        # for each package in the list, pull down their updated debian file
        #path = 'http://archive.ubuntu.com/ubuntu/' + updateDict[i]['Filename'].strip()
        path = 'http://100.64.0.12/apt/mirror/archive.ubuntu.com/ubuntu/' + updateDict[i]['Filename'].strip()
        print(path)
        name = updateDict[i]['Filename'].split("/")[-1]
        print(name)
        startDir = "/tmp/allowlist_config/temp/"
        pkgname = name.replace(".deb", "")
        print()
        print(">>> Package Name: " + pkgname)
        hashDict = {}

        # extract the files we want to measure into a list
        updatesList = create_paths_list(path, name)
        # go into the dir of the extracted debian package
        os.chdir(pkgname)
        
        # iterate through each file in the .deb dir and take a measurement
        for k in updatesList:
            fileDir = k.split('/')
            fileDir = "/".join(fileDir[:-1])
            os.chdir(fileDir)
            file_name = k.replace("./", startDir + pkgname + "/")

            if filter_exec == True:
                # do a check to see if the file is a symlink
                if os.path.islink(file_name):
                    print("This " + file_name + " is a symlink")
                    #if it is, try to resolve it. If it isn't dangling
                    real_path = os.path.realpath(file_name)
                    check_file = os.path.isfile(real_path)
                    if check_file == True:
                        print(">>>> This file " + file_name + " is a symlink and can be resolved.... Do not Ignore")
                        # check to see if file has exec permissions for any user
                        st = os.stat(file_name) 
                        exec_perm = bool(st.st_mode & stat.S_IXUSR or st.st_mode & stat.S_IXGRP or st.st_mode & stat.S_IXOTH)
                        if exec_perm == True:
                            print(True)
                            hash = take_measurement(file_name, k)
                            os.chdir(startDir + pkgname)
                        else:
                            print(">>>> This file " + file_name + " is not an executable ... Ignore") 
                            os.chdir(startDir + pkgname)
                            continue
                    else:
                        print(">>>> This file " + file_name + " is an unresolved symlink.... Ignore")  
                        os.chdir(startDir + pkgname)
                        continue       
                else:
                    #if not a symlink still check to see if file has exec permissions for any user
                    st = os.stat(file_name) 
                    exec_perm = bool(st.st_mode & stat.S_IXUSR or st.st_mode & stat.S_IXGRP or st.st_mode & stat.S_IXOTH)
                    if exec_perm == True:
                        print(">>>> This file " + file_name + " is an executable ... Do not Ignore")
                        hash = take_measurement(file_name, k)
                        os.chdir(startDir + pkgname)
                    else:
                        print(">>>> This file " + file_name + " is not an executable ... Ignore") 
                        os.chdir(startDir + pkgname)
                        continue


            if filter_exec == False:
                # do a check to see if the file is a symlink
                if os.path.islink(file_name):
                    print("This " + file_name + " is a symlink")
                    #if it is, try to resolve it. If it isn't dangling
                    real_path = os.path.realpath(file_name)
                    #print(real_path)
                    check_file = os.path.isfile(real_path)
                    if check_file == True:
                        print(">>>> This file " + file_name + " is a symlink and can be resolved.... Do not Ignore")
                        # check to see if file has exec permissions for any user
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

# take the hash (measurement) of the individual files inside the package
def take_measurement(file_name, k):
    #hash the file 
    hash_sha256 = hashlib.sha256()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
            #global hash
        measurement = hash_sha256.hexdigest()
    print(">>>> Filename " + k + "  " + measurement)
    return measurement

# create a list of file paths for each file in .deb package
def create_paths_list(path, name):
    # list of paths for each debian package
    r = requests.get(path)
    open(name , 'wb').write(r.content)
    time.sleep(3) ### Is this long enough??? DoSed the system

    result = subprocess.run(['dpkg-deb', '-X', name, name.replace('.deb', '')], stdout=subprocess.PIPE).stdout.decode('utf-8')
    #print(result)

    pathsList = result.splitlines()
    mainList = []
    #print(pathsList)
    trash = []
    for i in pathsList:
        if '\\\\' in i:
            edited_path = i.replace('\\\\', '\\')
            mainList.append(edited_path)
        else:
            mainList.append(i)

    for k in mainList:
        if k.endswith("/"):
            trash.append(k)
        else:
            print(">>> Potential File to measure: " + k) 
        
    s = set(trash)
    cleanList = [x for x in mainList if x not in s]
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
    with open("/tmp/allowlist_config/myfile2.txt", "a+") as f:
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
        finalDict = compare_sec_and_update(updateDict, securityDict)
        create_allowlist_update(mainDict, args.exec)
        os.chdir("/tmp/allowlist_config/")

        #compare update to security to see what files and their versions are the same 
        #finalDict = compare_sec_and_update(updateDict, securityDict)

        print()
        print(">>> Measuring the Security and Update Repository....\n")
        create_allowlist_update(finalDict, args.exec)
        os.chdir("/tmp/allowlist_config/")
        print()

        # print(">>> Measuring the Update Repository....\n")
        # create_allowlist_update(updateDict, args.exec)
        # os.chdir("/tmp/allowlist_config/")
        # print()
        # print(">>> Measuring the Security Repository....\n")
        # create_allowlist_update(securityDict, args.exec)
        # os.chdir("/tmp/allowlist_config/")

    elif args.update:
       # returns the difference between the two file types old vs new
       update = create_diff_release(updateDict, fileType='update')
       security = create_diff_release(securityDict, fileType='security')
       
       #compare update to security to see what files and their versions are the same 
       finalDict = compare_sec_and_update(update, security)

       print()
       print(">>> Measuring the Security and Update Repository....\n")
       create_allowlist_update(finalDict, args.exec)
       os.chdir("/tmp/allowlist_config/")
       print()

    #    print(">>> Measuring the Update Repository....\n")
    #    create_allowlist_update(update, args.exec)
    #    os.chdir("/tmp/allowlist_config/")
    #    print()
    #    print(">>> Measuring the Security Repository....\n")
    #    create_allowlist_update(security, args.exec)
    #    os.chdir("/tmp/allowlist_config/")

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
