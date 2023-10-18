import runtimeconf as cfg
import download_release as dwn



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