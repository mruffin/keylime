dpkg --list | \
grep "^i" | \
awk '{print $2}' | \
while read P ; do \
  D=$(apt-cache policy ${P} | grep "multiverse" | head -1) ; \
     echo "${P}:${D}" ; \
done
