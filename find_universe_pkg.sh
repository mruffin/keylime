dpkg --list | grep "^i" | awk '{print $2}' | while read P ; do D=$(apt-cache policy ${P} | grep "universe" | head -1) ; if [[ ${#D} -gt 0 ]] ; then echo "${P}:${D}" ; fi ; done
