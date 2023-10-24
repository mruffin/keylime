import datetime

mainVars = {
    'tmpDir' : '/tmp/allowlist_config/',
    'mainPath' : '/tmp/allowlist_config/MainRepo',
    'updatePath' : '/tmp/allowlist_config/UpdatePackage',
    'securityPath' : '/tmp/allowlist_config/SecurityPackage',
    'allowlist': "/tmp/allowlist_config/allowlist_" + str(datetime.date.today()) + ".txt"

}

mirror = {
    "mirror_file_path": "http://130.126.137.0/ubuntu/mirror/archive.ubuntu.com/ubuntu/dists/",
    "mirror_main_path" : "http://130.126.137.0/ubuntu/mirror/archive.ubuntu.com/ubuntu/"
}