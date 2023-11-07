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
import shutil
import subprocess
import time
import re
import json
import zlib
from datetime import date
import runtimeconf as cfg
import download_release as dwn
import clean_pkg_files as cln
import create_compare_release as cc

'''
must have zstd installed. For Mac == brew install zstd
'''

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
            # for each package in the Dictionary, pull down their updated debian file
            #i = i.split('__')[0]
            path = cfg.mirror['mirror_main_path'] + updateDict[i]['Filename'].strip()
            #Package: Name
            plainPkgName = updateDict[i]['Package'].strip()
            #package's .deb file name
            name = updateDict[i]['Filename'].split("/")[-1]
            version = updateDict[i]['Version'].strip()
            #print(name)
            startDir = cfg.mainVars['tmpDir'] + "temp/"
            #package's .deb file name
            pkgname = name.replace(".deb", "")
            print()
            print(">>> Package Name: " + pkgname)
            hashDict = {}
            recordDict = {}
            recordDict[plainPkgName + '_' + version] = {}
            recordDict[plainPkgName + '_' + version]["Date"] = {}

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

            # write the dictonary filled with files and their hashes to a json file
            x = date.today()
            x = x.strftime("%m/%d/%y")
            recordDict[plainPkgName + '_' + version] = {"digests": hashDict}
            recordDict[plainPkgName + '_' + version]["Date"] = str(x)
            
            self.write_recordlist(recordDict)

            # write the dictonary filled with measurements to a file
            #self.write_allowlist(hashDict)
            # cleanup temp dir
            self.cleanup(startDir)
        return 
    
    # create a list of file paths for each file in .deb package
    def create_paths_list(self, path, name):
        # list of paths for each debian package
        r = requests.get(path)
        open(name , 'wb').write(r.content)
        time.sleep(2) ### Is this long enough??? DoSed the system

        result = subprocess.run(['dpkg-deb', '-X', name, name.replace('.deb', '')], stdout=subprocess.PIPE).stdout.decode('utf-8')

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
        name = cfg.mainVars["allowlist"]
        #name = "/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/allowlist_" + "Oct11" + ".txt"
        with open(name , "a+") as f:
            for i in hashDict:
                f.write(hashDict[i] + "  " + i + "\n")
        f.close()
        return

    #write the records to the file
    def write_recordlist (self, recordDict):

        print(">>>> Writing package to JSON File")
        name = cfg.mainVars["recordName"]
        with open(name, "a+") as f:
            json.dump(recordDict, f)
            f.write('\n')
        f.close()
        return  name
    
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

def updateRecord():

    #files with the most recent same packagename but diff versions are compared, one with most recent date stays, delete the other

    return

def generateAllowlist(name):

    recordFile = cfg.mainVars["recordName"]
    allowlist = cfg.mainVars[name]
    file = open(allowlist, "a+")
    with open(recordFile) as f:
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

def cleanUpRecord(jsonFile):

    #compressed = zlib.compress(cPickle.dumps(obj))

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
    #dwn.dowload_new_release(args.amd64, args.i386, args.version, args.update, args.generate)

    masterUniPath = '/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/TestPackageFile.txt'
    masterDict = cln.clean_package_file(masterUniPath)
    os.chdir(cfg.mainVars["tmpDir"])

    
    # clean the package files (i.e. turn them into easily readable dictionaries) -- These dictionaries will serve as the basis for my Class Objects
    #mainDict = cln.clean_package_file(cfg.mainVars["mainPath"])
    #updateDict = cln.clean_package_file(cfg.mainVars["updatePath"])
    #securityDict = cln.clean_package_file(cfg.mainVars["securityPath"])
    
    # either generate a new release update and append or update previous allowlist
    if args.generate:

        ### Purely for testing purposes ###
        master = Allowlist(masterDict, args.exec)
        master.create_allowlist_update()
        os.chdir(cfg.mainVars["tmpDir"])


        #compare update to security to see what files and their versions are the same 
        #pkgDict1 = cc.compare_sec_and_update(updateDict, securityDict)
        
        #print("\n >>> Measuring the Main Repository....\n")
        #allow1 = Allowlist(mainDict, args.exec)
        #allow1.create_allowlist_update()
        #os.chdir(cfg.mainVars["tmpDir"])


        #allow2 = Allowlist(pkgDict1, args.exec)
        #allow2.create_allowlist_update()
        #os.chdir(cfg.mainVars["tmpDir"])
        allowlistVer = "allowlistOrig"    
        generateAllowlist(allowlistVer)
        #generate my allowlist and then compress my record until it's time to use it again


        #cleanUpRecord()


        '''print("\n >>> Measuring the Security and Update Repositories....\n\n")
        create_allowlist_update(pkgDict1, args.exec)
        os.chdir(cfg.mainVars["tmpDir"])'''

    elif args.update:
       #returns the difference between the two file types old vs new
       update = cc.create_diff_release(updateDict, fileType='update')
       security = cc.create_diff_release(securityDict, fileType='security')
    
       #compare update to security to see what files and their versions are the same 
       pkgDict1 = cc.compare_sec_and_update(update, security)
       allow1 = Allowlist(pkgDict1, filter)
       allow1.create_allowlist_update()
       os.chdir(cfg.mainVars["tmpDir"])
       
       #uncompress the record first and then update stuff
       #give me the first version of the allowlist based off everything in record
       #generateAllowlist(allowlistOrig)
       #call the update record function to get rid of old stuff
       #updateRecord()
       #generate the allowlist again from the record ### pass in the name of the allowlist
       #generateAllowlist(allowlistUpdate)

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