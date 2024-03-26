import runtimeconf as cfg
import clean_pkg_files as cln
import sys
from datetime import date, datetime
from collections import defaultdict
import json

# compare the previous release stored on your machine to the current release. Find the differneces and target those for the update
def create_diff_release(currentFileDict, fileType):
    print(">>>> Loading up Old Package Files")
    # load up old file and 
    if fileType == 'update':
        filePath = cfg.mainVars['tmpDir'] + 'UpdatePackage_Old'
    elif fileType == 'security':
        filePath = cfg.mainVars['tmpDir'] + 'SecurityPackage_Old'

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

    #### Experiment Paramaters ####
    cfg.updateLog["added_files"][fileType] = count

    count2 = 0 
    # see if the version of the pkg has changed
    for i in curentFileList:
        #print(i)
        if i in oldFileList:
            if currentFileDict[i]['Version'] != oldFileDict[i]['Version']:
                finalList.append(i)
                count2 +=1 
    print(">>>> " + str(count2) + " " + fileType + " packages have been updated")

    #### Experiment Paramaters ####
    cfg.updateLog["updated_files"][fileType] = count2

    # for each pkg in the final list add the pkgname as the key and the valueDict as the value
    for i in finalList:
        finalDict[i] = currentFileDict[i]


    # Package Priority Types: Essential, Required, Important, Standard, Optional, or Extra
    essential = 0
    required = 0
    important = 0
    standard = 0 
    optional = 0
    extra = 0

    for i in finalList:
        #print(finalDict[i]["Priority"])

        if finalDict[i]["Priority"] == " essential":
            essential += 1

        elif finalDict[i]["Priority"] == " required":
            required += 1

        elif finalDict[i]["Priority"] == " important":
            important += 1

        elif finalDict[i]["Priority"] == " standard":
            standard += 1

        elif finalDict[i]["Priority"] == " optional":
            optional += 1

        elif finalDict[i]["Priority"] == " extra":
            extra += 1

    cfg.updateLog["priority"][fileType]["essential"] = essential
    cfg.updateLog["priority"][fileType]["required"] = required
    cfg.updateLog["priority"][fileType]["important"] = important
    cfg.updateLog["priority"][fileType]["standard"] = standard
    cfg.updateLog["priority"][fileType]["optional"] = optional
    cfg.updateLog["priority"][fileType]["extra"] = extra

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
    print('>>>> There are ' + str(len(potentialDuplicateFiles)) + ' Packages with the same name and diff version')
    print('>>>> There are ' + str(len(realDuplicateFiles)) + ' real duplicate files between Security and Update Releases')


    #### Experiment Paramaters ####
    cfg.updateLog["uniqueName_update_packages"] = len(uniqueUpdatesFiles)
    cfg.updateLog["uniqueName_security_packages"] = len(uniqueSecurityFiles)
    cfg.updateLog["sameName_diffVersion_packages"] = len(potentialDuplicateFiles)
    cfg.updateLog["sameName_sameVersion_packages"] = len(realDuplicateFiles)

    #put a clause here that if all of these values are 0, no additions and no changes, we do not need to preform an update
    #sys.exit the program
    if len(uniqueUpdatesFiles) == 0 and len(uniqueSecurityFiles) == 0 and len(potentialDuplicateFiles) == 0 and len(realDuplicateFiles) == 0:
        print(">>>> There are no packages to be updated, program will exit") 
        cfg.updateLog["update_status"] = "No Modifications made today"
        end_time = datetime.now()
        cfg.updateLog["end_time"] = end_time

        with open(cfg.experiment["update_log"], "a") as f:
            json.dump(cfg.updateLog, f, default=str)
            f.write(",")
            f.write("\n")

        sys.exit("Program Completed")
    
    print('>>>> Creating final list')
    print()

    #create a final dictionary to use
    for i in uniqueUpdatesFiles:
        name = str(i + '__' + updateDict[i]['Version'])
        finalDict[name] = updateDict[i]
    #print("unique update ", len(uniqueUpdatesFiles))

    for k in uniqueSecurityFiles:
        name = str(k + '__' + securityDict[k]['Version'])
        finalDict[name] = securityDict[k]
    #print("unique sec ", len(uniqueSecurityFiles))

    for l in potentialDuplicateFiles:
        name = str(l + '__' + updateDict[l]['Version'])
        finalDict[name] = updateDict[l]
    #print("potential duplicates ", len(potentialDuplicateFiles))

    for j in potentialDuplicateFiles:
        name = str(j + '__' + securityDict[j]['Version'])
        finalDict[name] = securityDict[j]
    #print("potential duplicates ", len(potentialDuplicateFiles))

    for m in realDuplicateFiles:
        name = str(m + '__' + updateDict[m]['Version'])
        finalDict[name] = updateDict[m]
    #print("real duplicates ", len(realDuplicateFiles))

    cfg.updateLog["NumberOfPkgs"] = len(finalDict.keys())
    
    return finalDict
