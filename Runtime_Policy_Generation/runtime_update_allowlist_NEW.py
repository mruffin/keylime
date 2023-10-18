'''
Margie Ruffin 
IBM Summer 2023
Generate Updated Allowlist for Continious
Runtime Integrity Monitoring
'''

'''
How to run this script if you have amd64 Architecture working with Ubuuntu's Jammy

python3 runtime_update_allowlist.py -x -v jammy -g -e

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
import re
import runtimeconf as cfg
import download_release as dwn
import clean_pkg_files as cln
import datetime

'''
must have zstd installed. For Mac == brew install zstd
'''

# compare the previous release stored on your machine to the current release. Find the differneces and target those for the update
def create_diff_release(currentFileDict, fileType):
    print(">>>> Loading up Old Package Files")
    # load up old file and 
    if fileType == 'update':
        filePath = '/tmp/allowlist_config/UpdatePackage_Old'
    elif fileType == 'security':
        filePath = '/tmp/allowlist_config/SecurityPackage_Old'

    finalDict = {}
    finalList = []
    # returns a dictionary
    oldFileDict = cln.clean_package_file(filePath)
    
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
    #print(len(updateFileList))
    securityFileList = list(securityDict.keys())
    #print(len(securityFileList))

    duplicateList = []
    finalDict = {}
    #count = 0

    '''we need to compare the name and versions of the packages 
    if the filename is found in the 2nd list then go thru the dict and compare the two versions. If they are the same
    take the name out of (remove) both of the lists and put it in the final list,. Keep count of how many are dubplcates.
    then once all are taken out of the lists combine the security and update lists with their unique files and then add the final list to them update final dict'''

    # go through one list and compare the file names. If names and version matches, add to duplicate list and remove from other two lists.
    # we only want to see it once.

    updateFileSet = set(updateFileList)
    securityFileSet = set(securityFileList)

    uniqueUpdatesFiles = updateFileSet.difference(securityFileSet)
    uniqueSecurityFiles = securityFileSet.difference(updateFileSet)
    potentialDuplicateFiles = updateFileSet.intersection(securityFileSet)
    print('>>>> There are ' + str(len(potentialDuplicateFiles)) + ' Packages with the same name')
    print()

    for i in list(potentialDuplicateFiles):
        if updateDict[i]['Version'] == securityDict[i]['Version']:
            duplicateList.append(i)
            potentialDuplicateFiles.remove(i)

    realDuplicateFiles = set(duplicateList)

    print('>>>> There are ' + str(len(uniqueUpdatesFiles)) + ' unique Update Packages')
    print('>>>> There are ' + str(len(uniqueSecurityFiles)) + ' unique Security Packages')
    print('>>>> There are ' + str(len(potentialDuplicateFiles)) + ' Packages with the same name')
    print('>>>> There are ' + str(len(realDuplicateFiles)) + ' real duplicate files between Security and Update Releases')
    print('>>>> Creating final list')
    print()

    #create a final dictionary to use
    for i in uniqueUpdatesFiles:
        name = str(i + '__' + updateDict[i]['Version'])
        finalDict[name] = updateDict[i]

    for k in uniqueSecurityFiles:
        name = str(k + '__' + securityDict[k]['Version'])
        finalDict[name] = securityDict[k]

    for l in potentialDuplicateFiles:
        name = str(l + '__' + updateDict[l]['Version'])
        finalDict[name] = updateDict[l]

    for j in potentialDuplicateFiles:
        name = str(j + '__' + securityDict[j]['Version'])
        finalDict[name] = securityDict[j]

    for m in realDuplicateFiles:
        name = str(m + '__' + updateDict[m]['Version'])
        finalDict[name] = updateDict[m]
    
    #for i in finalDict.keys():
    #    print(i)
    #print(len(finalDict.keys()))
    return finalDict

class Allowlist:
    def __init__(self, dict, filter_exec):
        self.dict = dict
        self.filter = bool(filter_exec)

    # create a new file with file paths and Sha256Sum of the targeted files
    def create_allowlist_update(self):
        updateDict = self.dict
        filter_exec = self.filter

        global hash
        if os.path.exists('temp/'):
                os.chdir('temp/')
        else:
            os.mkdir('temp/')
            os.chdir('temp/')

        for i in updateDict:
            # for each package in the list, pull down their updated debian file
            #i = i.split('__')[0]
            path = cfg.mirror['mirror_main_path'] + updateDict[i]['Filename'].strip()
            #print(path)
            name = updateDict[i]['Filename'].split("/")[-1]
            #print(name)
            startDir = cfg.mainVars['tmpDir'] + "temp/"
            pkgname = name.replace(".deb", "")
            print()
            print(">>> Package Name: " + pkgname)
            hashDict = {}

            # extract the files we want to measure into a list
            updatesList = self.create_paths_list(path, name)
            # go into the dir of the extracted debian package
            os.chdir(pkgname)
            
            # iterate through each file in the .deb dir and take a measurement
            for k in updatesList:
                fileDir = k.split('/')
                fileDir = "/".join(fileDir[:-1])
                os.chdir(fileDir)
                file_name = k.replace("./", startDir + pkgname + "/")
                print(file_name)

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
                            dynamic_match = re.findall("\.so(.*)$", file_name)
                            if exec_perm == True:
                                #print(True)
                                print(">>>> This file " + file_name + " is an executable ... Do not Ignore")
                                hash = self.take_measurement(file_name, k)
                                os.chdir(startDir + pkgname)
                            elif dynamic_match:
                            #elif file_name.endswith('.so'):
                                print(">>>> This file " + file_name + " is an executable ... Do not Ignore")
                                hash = self.take_measurement(file_name, k)
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
                        dynamic_match = re.findall("\.so(.*)$", file_name)
                        if exec_perm == True:
                            print(">>>> This file " + file_name + " is an executable ... Do not Ignore")
                            hash = self.take_measurement(file_name, k)
                            os.chdir(startDir + pkgname)
                        elif dynamic_match:    
                        #elif file_name.endswith('.so'):
                            print(">>>> This file " + file_name + " is an executable ... Do not Ignore")
                            hash = self.take_measurement(file_name, k)
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
                            hash = self.take_measurement(file_name, k)
                            os.chdir(startDir + pkgname)
                        else:
                            print(">>>> This file " + file_name + " is an unresolved symlink.... Ignore")  
                            os.chdir(startDir + pkgname)
                            continue       
                    else:
                        hash = self.take_measurement(file_name, k)
                        os.chdir(startDir + pkgname)

                policyPath = k.replace("./", "/")
                #print(policyPath)
                hashDict[policyPath] = hash

                #### Adding in section to address /bin/* execuatbles. Duplicate the path   ####
                #### name and  hash and  change the path to second to /usr/bin*            ####
                if policyPath.startswith('/bin/'):
                    policyPathDuplicate = policyPath.replace('/bin/', '/usr/bin/')
                    hashDict[policyPathDuplicate] = hash
            
                if policyPath.startswith('/lib/'):
                    policyPathDuplicate = policyPath.replace('/lib/', '/usr/lib/')
                    hashDict[policyPathDuplicate] = hash
                
                if policyPath.startswith('/lib32/'):
                    policyPathDuplicate = policyPath.replace('/lib32/', '/usr/lib32/')
                    hashDict[policyPathDuplicate] = hash

                if policyPath.startswith('/libx32/'):
                    policyPathDuplicate = policyPath.replace('/libx32/', '/usr/libx32/')
                    hashDict[policyPathDuplicate] = hash

                if policyPath.startswith('/lib64/'):
                    policyPathDuplicate = policyPath.replace('/lib64/', '/usr/lib64/')
                    hashDict[policyPathDuplicate] = hash

                if policyPath.startswith('/sbin/'):
                    policyPathDuplicate = policyPath.replace('/sbin/', '/usr/sbin/')
                    hashDict[policyPathDuplicate] = hash

            # write the dictonary filled with measurements to a file
            self.write_allowlist(hashDict)
            # cleanup temp dir
            self.cleanup(startDir)
        return 
    
    # create a list of file paths for each file in .deb package
    def create_paths_list(self, path, name):
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

    # take the hash (measurement) of the individual files inside the package
    def take_measurement(self, file_name, k):
        #hash the file 
        hash_sha256 = hashlib.sha256()
        with open(file_name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
                #global hash
            measurement = hash_sha256.hexdigest()
        print(">>>> Filename " + k + "  " + measurement)
        return measurement

    # write allowlist to file
    def write_allowlist(self, hashDict):
        # if this file doesn't exisit we will create it and begin appending measurements to it.
        # if it does exisit already (have previously run this script) then simply open it and append to it
        print(">>>> Writing package to allowlist")
        #x = datetime.datetime.now()
        #time = x.strftime("%x_%X")
        name = "/tmp/allowlist_config/allowlist_" + "Oct11" + ".txt"
        with open(name , "a+") as f:
            for i in hashDict:
                f.write(hashDict[i] + "  " + i + "\n")
        f.close()
        return

    # cleanup whatever directory needs it
    def cleanup(self, dir):
        # delete contents of /tmp/allow_config/temp/ folder to prepare memory space for the next one
        print(">>>> Cleaning up files")

        for f in os.listdir(dir):
            path = os.path.join(dir, f)
            #removeReadOnly(path)
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
    dwn.dowload_new_release(args.amd64, args.i386, args.version, args.update, args.generate)
    
    # clean the package files (i.e. turn them into easily readable dictionaries) -- This will serve as the basis for my Class Objects
    mainDict = cln.clean_package_file(cfg.mainVars["mainPath"])
    updateDict = cln.clean_package_file(cfg.mainVars["updatePath"])
    securityDict = cln.clean_package_file(cfg.mainVars["securityPath"])
    
    # either generate a new release update and append or update previous allowlist
    if args.generate:
        #compare update to security to see what files and their versions are the same 
        pkgDict1 = compare_sec_and_update(updateDict, securityDict)
        
        print("\n >>> Measuring the Main Repository....\n")
        allow1 = Allowlist(mainDict, args.exec)
        allow1.create_allowlist_update()
        os.chdir(cfg.mainVars["tmpDir"])

        '''print("\n >>> Measuring the Main Repository....\n")
        create_allowlist_update(mainDict, args.exec)
        os.chdir(cfg.mainVars["tmpDir"])'''

        allow2 = Allowlist(pkgDict1, args.exec)
        allow2.create_allowlist_update()
        os.chdir(cfg.mainVars["tmpDir"])

        '''print("\n >>> Measuring the Security and Update Repositories....\n\n")
        create_allowlist_update(pkgDict1, args.exec)
        os.chdir(cfg.mainVars["tmpDir"])'''

    elif args.update:
       #returns the difference between the two file types old vs new
       update = create_diff_release(updateDict, fileType='update')
       security = create_diff_release(securityDict, fileType='security')
    
       #compare update to security to see what files and their versions are the same 
       pkgDict1 = compare_sec_and_update(update, security)
       allow1 = Allowlist(pkgDict1, filter)
       allow1.create_allowlist_update()
       os.chdir(cfg.mainVars["tmpDir"])

       '''print("\n>>> Measuring the Security and Update Repositories....\n\n")
       create_allowlist_update(pkgDict1, args.exec)
       os.chdir(cfg.mainVars["tmpDir"])'''


class Parser(argparse.ArgumentParser):
    def error(self, message: str):
        sys.stderr.write(f"error: {message}\n")
        self.print_help(sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()

''' we can create a pkl of the information serialied and dignital sign it, save the hash
only unpkl if the sig/hash matches

'''