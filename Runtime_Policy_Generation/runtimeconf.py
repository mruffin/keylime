import datetime

mainVars = {
    'tmpDir' : '/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/',
    'mainPath' : '/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/MainRepo',
    'updatePath' : '/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/UpdatePackage',
    'securityPath' : '/home/mruffin2/Research/Keylime/keylime/Runtime_Policy_Generation/allowlist_config/SecurityPackage',
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

