'''
Margie Ruffin 
IBM Summer 2023
Generate Updated Allowlist for Continious
Runtime Integrity Monitoring
'''

'''
How to run this script if you have amd64 Architecture working with Ubuuntu's Jammy

python3 runtime_update_allowlist.py -x -v jammy -g -e (If you want to generate a new record)

python3 runtime_update_allowlist.py -x -v jammy -u -e (If you want to update the record)

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
import zipfile
from datetime import date, datetime
from pathlib import Path
import runtimeconf as cfg
import download_release as dwn
import clean_pkg_files as cln
import create_compare_release as cc
from collections import defaultdict

'''
must have zstd installed. For Mac == brew install zstd
'''

class Allowlist:
    def __init__(self, dict, filter_exec):
        self.dict = dict
        self.filter = bool(filter_exec)

    # create a new file with file paths and Sha256Sum of the targeted files
    def create_allowlist_update(self, status):
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
            recordDict[plainPkgName + '___' + version] = {}
            recordDict[plainPkgName + '___' + version]["Date"] = {}

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
                            #kernal_match = re.findall("\.ko(.*)$", file_name)
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
                            # elif kernal_match:
                            # #elif file_name.endswith('.ko'):
                            #     print(">>>> This file " + file_name + " is an kernal library ... Do not Ignore")
                            #     hash = self.take_measurement(file_name, k)
                            #     os.chdir(startDir + pkgname)
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
                        #kernal_match = re.findall("\.ko(.*)$", file_name)
                        if exec_perm == True:
                            print(">>>> This file " + file_name + " is an executable ... Do not Ignore")
                            hash = self.take_measurement(file_name, k)
                            os.chdir(startDir + pkgname)
                        elif dynamic_match:    
                        #elif file_name.endswith('.so'):
                            print(">>>> This file " + file_name + " is an executable ... Do not Ignore")
                            hash = self.take_measurement(file_name, k)
                            os.chdir(startDir + pkgname)
                        # elif kernal_match:    
                        # #elif file_name.endswith('.ko'):
                        #     print(">>>> This file " + file_name + " is an kernal library ... Do not Ignore")
                        #     hash = self.take_measurement(file_name, k)
                        #     os.chdir(startDir + pkgname)
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
            recordDict[plainPkgName + '___' + version] = {"digests": hashDict}
            recordDict[plainPkgName + '___' + version]["Date"] = str(x)
            
            self.write_recordlist(recordDict, status)

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
        time.sleep(1) ### Is this long enough??? DoSed the system

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
    """ def write_allowlist(self, hashDict):
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
        return """

    #write the records to the file
    def write_recordlist (self, recordDict, status):

        print(">>>> Writing package to JSON File")
        if status == "g":
            name = cfg.mainVars["recordName"]
        elif status == "u":
            name = cfg.mainVars["recordNameTemp"]

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

            if os.path.isfile(path):
                os.remove(path)
            else:
                #make_writeable_recursive(path, 0o777)
                shutil.rmtree(path, onerror=on_rm_error) #, ignore_errors=True, onerror=on_rm_error 
        os.chdir(dir)
        return
    
""" def make_writeable_recursive(path, mode):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in [os.path.join(root, d) for d in dirs]:
            os.chmod(dir, mode)
        for file in [os.path.join(root, f) for f in files]:
            if os.path.islink(file):
                os.unlink(file)
            else:
                os.chmod(file, mode)  """       

def on_rm_error(func, path, exc_info):
    os.chmod(path, 0o777) #stat.S_IRUSR |
    func(path)

def generateAllowlist(name):

    recordFile = cfg.mainVars["recordName"]
    allowlist = cfg.mainVars[name]
    file = open(allowlist, "w")
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

def updateRecord():
    #files with the most recent same packagename but diff versions are compared, one with most recent date stays, delete the other
    recordFile = cfg.mainVars["recordName"]   
    print(">>>> This the path to the record file", recordFile)
    recordFileTemp = cfg.mainVars["recordNameTemp"]
    print(">>>> This the path to the Temp record file", recordFileTemp)
    addedpkg = [] #packages we have added to the Original Record
    oldPkgs = []
    seenpkg = [] #all the original packages we've seen thus far

    #Step #1: Compare the records and add to the Original Record
    
    orgRecord = open(recordFile, "r+", encoding='utf-8')
    tempRecord = open(recordFileTemp, "r")

    #make a list of all packages that are in the orignal record
    for k in orgRecord:
        line = json.loads(k)
        name = list(line.keys())[0]
        seenpkg.append(name)
    #print("These are the packages that existed before the update", seenpkg)

    orgRecord.seek(0)
    #s = orgRecord.read()
    for i in tempRecord:
        #print("This is the temp json record >>>>>> " + i)
        newData = json.loads(i) #load each record and grab its key -- pkgname_version
        ans = list(newData.keys())[0]
        newpkg_name = ans.split("___")[0] #we just want the pkgname
        newpkg_version = ans.split("___")[1]
        
        #s = orgRecord.read()
        #print("This is the record file", s)
        for j in orgRecord: 
            #print("This is the orig json record >>>>>> " + j)
            oldData = json.loads(j) #load each record and grab its key pkgname_version
            res = list(oldData.keys())[0]
            oldpkg_name = res.split("___")[0] #we just want the pkgname
            oldpkg_version = res.split("___")[1]
            #make a list of everything you've seen before and if at the end of loop package isn't in list add it to record
            #seenpkg.append(res)

            #The package name and version is same, it has not been updated
            if newpkg_name == oldpkg_name and newpkg_version == oldpkg_version:
                print(">>>> This package has the same name and version as another, move on")
                seenpkg.append(res)
                continue
            
            #The package name is the same but version is different, it has been updated
            elif newpkg_name == oldpkg_name and newpkg_version != oldpkg_version:
                print(">>>> Found pakages with same name and different versions, comparing dates")
                seenpkg.append(res)
                #if names are the same, compare the dates. This will pull the most recent package
                if datetime.strptime(newData[ans]["Date"] , "%m/%d/%y") > datetime.strptime(oldData[res]["Date"] , "%m/%d/%y"):
                    print(">>>> Adding appropriate Package to Record")
                    s = orgRecord.read()
                    json.dump(newData, orgRecord)
                    orgRecord.write('\n')
                    #put the new into a list to be tracked
                    addedpkg.append(ans)
                    #put the old into a list to be taken out later
                    oldPkgs.append(res)
                    #orgRecord.seek(0)
                continue
            else:
                continue

        #print("These are the packages that existed before the update", seenpkg)
        #print("These are the old packages to replace: ", oldPkgs)
        #if you never find the same package name in the record file add the json record to old record
        if ans not in seenpkg and ans not in addedpkg:
            print(">>>> This is a new Pacakge " + ans + " Adding it to the Record")
            s = orgRecord.read()
            json.dump(newData, orgRecord)
            orgRecord.write('\n')
            addedpkg.append(ans)
        
        orgRecord.seek(0)

    tempRecord.close()
    orgRecord.close()
    #Step 2 call the function to create the policies with all the new additions
    print(">>>> Making the Allowlist with the New Additions")
    allowlistVer = "allowlistOrig"    
    generateAllowlist(allowlistVer)

    os.remove(recordFileTemp)

    return  #placed here until Keylime Issue is solved

"""     #Step 3 remove the old from the record list
    #Clear out contents of temp file because we want to replace them for now. 
    open(recordFileTemp, 'w').close()

    #Temporarily write the record to temp with removals and then rename it as the main AllowlistRecord 
    print(">>>> Writing lines to Temp")
    with open(recordFile, "r") as orgRecord:
        with open(recordFileTemp, "w") as tempRecord:
            for line in orgRecord:
                lineData = json.loads(line)
                name = list(lineData.keys())[0]
                print(name)

                #write all packages that are not in oldpkg List
                if name not in oldPkgs:
                    json.dump(lineData, tempRecord)
                    tempRecord.write('\n')

    #os.rename(recordFileTemp, recordFile)
    print(">>>> Moving files from temp to main")
    shutil.copy(recordFileTemp, recordFile)

    #Step 4 call the function to create the polices with removals
    print(">>>> Making the Allowlist with the old stuff removed")    
    allowlistVer = "allowlistUpdate" 
    generateAllowlist(allowlistVer) 

    #After it is all said and done, delete the temp record
    #os.remove(recordFileTemp)
    return"""

# alternate state of the record based on whether a zip file or .json file is present
def changeRecordState():

    #check to see if the zip of this file exsists
    if os.path.isfile(cfg.mainVars["recordNameZip"]):
        
        print(">>>> Uncompressing the Record File")
        #the file exisits uncompress it
        with zipfile(cfg.mainVars["recordNameZip"], "r") as zobject:
            zobject.extractall()
        #delete the zip file
        os.remove(cfg.mainVars["recordNameZip"])

    # Zip file didn't exsist
    else:
        compression = zipfile.ZIP_DEFLATED
        print(">>>> Compressing the record file")
        #compress the record file 
        zf = zipfile.ZipFile(cfg.mainVars["recordNameZip"], mode="w")
        try:
            zf.write(cfg.mainVars["recordName"], compress_type=compression)
        except FileNotFoundError as e:
            print(f' *** Exception occurred during zip process - {e}')
        finally:
            zf.close()

        #delete the plain record file
        os.remove(cfg.mainVars["recordName"])

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

    # print help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    #### Experiment Paramaters ####
    start_time = datetime.now()
    cfg.updateLog["start_time"] = start_time

    args = parser.parse_args()
    dwn.dowload_new_release(args.amd64, args.i386, args.version, args.update, args.generate)

    ### Purely for testing purposes ###
    '''masterUniPath = '/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/TestPackageFileUpdate.txt'
    masterDict = cln.clean_package_file(masterUniPath)
    os.chdir(cfg.mainVars["tmpDir"])'''

    
    # clean the package files (i.e. turn them into easily readable dictionaries) -- These dictionaries will serve as the basis for my Class Objects
    mainDict = cln.clean_package_file(cfg.mainVars["mainPath"])
    updateDict = cln.clean_package_file(cfg.mainVars["updatePath"])
    securityDict = cln.clean_package_file(cfg.mainVars["securityPath"])
    
    # either generate a new release update and append or update previous allowlist
    if args.generate:

        status = "g"
        ### Purely for testing purposes ###
        '''master = Allowlist(masterDict, args.exec)
        master.create_allowlist_update(status)
        os.chdir(cfg.mainVars["tmpDir"])'''

        #compare update to security to see what files and their versions are the same 
        pkgDict1 = cc.compare_sec_and_update(updateDict, securityDict)
        print('>>>> There are ' + str(len(mainDict.keys())) + ' Main Repo Packages')
        cfg.updateLog["mainrepository_packages"] = len(mainDict.keys())

        print("\n >>> Measuring the Main Repository....\n")
        allow1 = Allowlist(mainDict, args.exec)
        allow1.create_allowlist_update(status)
        os.chdir(cfg.mainVars["tmpDir"])

        allow2 = Allowlist(pkgDict1, args.exec)
        allow2.create_allowlist_update(status)
        os.chdir(cfg.mainVars["tmpDir"])

        #generate my allowlist and then compress my record until it's time to use it again
        allowlistVer = "allowlistOrig"    
        generateAllowlist(allowlistVer)
        #changeRecordState()



        #### Experiment Paramaters ####
        end_time = datetime.now()
        cfg.updateLog["end_time"] = end_time
        cfg.updateLog["diff_time"] = end_time - start_time

        with open(cfg.experiment["update_log"], "a") as f:
            json.dump(cfg.updateLog, f, default=str)
            f.write(",")
            f.write("\n")

    elif args.update:
       
       #uncompress the record first and then update it ... adding stuff to the record
       #changeRecordState()

       status = "u"
       ### Purely for testing purposes ###
       '''master = Allowlist(masterDict, args.exec)
       master.create_allowlist_update(status)
       os.chdir(cfg.mainVars["tmpDir"])'''

       #returns the difference between the two file types old vs new
       update = cc.create_diff_release(updateDict, fileType='update')
       security = cc.create_diff_release(securityDict, fileType='security')
       
       #compare update to security to see what files and their versions are the same 
       pkgDict1 = cc.compare_sec_and_update(update, security)

       allow1 = Allowlist(pkgDict1, args.update)
       allow1.create_allowlist_update(status)
       os.chdir(cfg.mainVars["tmpDir"])
       
       #call the update record function to get rid of old stuff
       updateRecord()
       


       #### Experiment Paramaters ####
       end_time = datetime.now()
       cfg.updateLog["end_time"] = end_time
       cfg.updateLog["diff_time"] = end_time - start_time
       
       with open(cfg.experiment["update_log"], "a") as f:
            json.dump(cfg.updateLog, f, default=str)
            f.write(",")
            f.write("\n")

       #record state
       #changeRecordState()


class Parser(argparse.ArgumentParser):
    def error(self, message: str):
        sys.stderr.write(f"error: {message}\n")
        self.print_help(sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
