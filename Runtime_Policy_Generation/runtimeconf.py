import datetime
from collections import defaultdict

mainVars = {
    'tmpDir' : '/scratch/allowlist_config/',
    #'tmpDir' : '/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/',
    'mainPath' : '/scratch/allowlist_config/MainRepo',
    #'mainPath' : '/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/MainRepo',
    'updatePath' : '/scratch/allowlist_config/UpdatePackage',
    #'updatePath' : '/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/UpdatePackage',
    'securityPath' : '/scratch/allowlist_config/SecurityPackage',
    #'securityPath' : '/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/SecurityPackage',
    'mainPathOld' : '/scratch/allowlist_config/MainRepo_Old',
    #'mainPathOld' : '/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/MainRepo_Old',
    'updatePathOld' : '/scratch/allowlist_config/UpdatePackage_Old',
    #'updatePathOld' : '/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/UpdatePackage_Old',
    'securityPathOld' : '/scratch/allowlist_config/SecurityPackage_Old',
    #'securityPathOld' : '/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/SecurityPackage_Old',
    'allowlistOrig': "/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/Allowlists/allowlist_orig_" + str(datetime.date.today()) + ".txt",
    'allowlistUpdate': "/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/Allowlists/allowlist_updated_" + str(datetime.date.today()) + ".txt",
    'recordName' : "/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/allowlistRecord.json",
    'recordNameTemp' : "/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/allowlistRecordTemp.json",
    'recordNameZip' : "/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/allowlistRecord.zip"

}

mirror = {
    "mirror_file_path": "http://130.126.137.0/ubuntu/mirror/archive.ubuntu.com/ubuntu/dists/",
    "mirror_main_path" : "http://130.126.137.0/ubuntu/mirror/archive.ubuntu.com/ubuntu/"
}

experiment = {
    "update_log" : "/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/Experiment/update_log.json"
}

updateLog = defaultdict(lambda: defaultdict(dict))
#updateLog = {}
#updateLog["added_files"] = {}
