import os, shutil
import os.path
import sys
import requests
import gzip
import shutil
import runtimeconf as cfg

def download_new_release_files(path, filename):
    try:        
        r = requests.get(path)
        print("Retrieved Release File")
        open(filename , 'wb').write(r.content)
        with gzip.open(filename, 'rb') as f_in:
            with open(filename.replace('.gz', ''), 'wb') as f_out:
                print(">>>> Opening File " + filename + "...")
                shutil.copyfileobj(f_in, f_out)
        print(">>>> Extracting file from " + filename + "...\n")
        
    except:
        print(">>>> The " +  filename + " Package file was not able to be downloaded and/or extracted\n")
        
        sys.exit(1)
    return

# download new ubuntu release put indide /tmp/allowlist_config folder on machine
def dowload_new_release(amd, intel, version, update, generate):

    #navigate to the /tmp/ dir and create a new dir for allowlist files
    '''if os.path.exists('/tmp/'):
        os.chdir('/tmp/')
    else:
        os.mkdir('/tmp/')
        os.chdir('/tmp/')'''

    if os.path.exists(cfg.mainVars['tmpDir']):
        os.chdir(cfg.mainVars['tmpDir'])
    else:
        os.mkdir('/scratch/allowlist_config/')
        os.chdir('/scratch/allowlist_config/')
        #os.mkdir('allowlist_config/')
        #os.chdir('allowlist_config/')

    if amd == True:
        binary = "binary-amd64"
    if intel == True:
        binary = "binary-i386"

    mName = 'MainRepo.gz'
    rName = 'UpdatePackage.gz'
    sName = 'SecurityPackage.gz'

    #Mirror Files
    main_path = cfg.mirror['mirror_file_path'] + version + '/main/' + binary + '/Packages.gz'
    regular_path = cfg.mirror['mirror_file_path'] + version + '-updates/main/' + binary + '/Packages.gz'
    security_path = cfg.mirror['mirror_file_path'] + version + '-security/main/' + binary + '/Packages.gz'

    try:
        if update == True:
            print(">>>> Moving old files over")
            # check to see if the packages already exist, if so rename old ones to Name_Old.gz or Name_Old and then write down the new ones
            if os.path.isfile(cfg.mainVars['securityPath']):
                os.rename(cfg.mainVars['securityPath']+'.gz', cfg.mainVars['securityPathOld']+'.gz')
                os.rename(cfg.mainVars['securityPath'], cfg.mainVars['securityPathOld'])

            if os.path.isfile(cfg.mainVars['updatePath']):
                os.rename(cfg.mainVars['updatePath']+'.gz', cfg.mainVars['updatePathOld']+'.gz')
                os.rename(cfg.mainVars['updatePath'], cfg.mainVars['updatePathOld'])
            
            print(">>>> Downloading and files")
            download_new_release_files(regular_path, rName)
            download_new_release_files(security_path, sName)

        if generate == True:
            print(">>>> Downloading new files")
            download_new_release_files(main_path, mName)
            download_new_release_files(regular_path, rName)
            download_new_release_files(security_path, sName)
    except:
        print(">>>> Error: No files downloaded")
    return