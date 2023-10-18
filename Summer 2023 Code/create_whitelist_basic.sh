#!/bin/bash

. /etc/default/keylime
#. /opt/keylimebootstrap/bin/klbutil

export KEYLIME_CHECK_RAMDISK=0
export KEYLIME_CLEANUP=0
export KEYLIME_COMPUTE_RAMDISK_CONTENTS=0
export KEYLIME_ADD_BOOT_AGGREGATE=0
export KEYLIME_ALGO=auto
export KEYLIME_UPLOAD_TO_DEPLOYER=0
export KEYLIME_USAGE="Usage: $0 [-f whitelist file name] [-a auto|b2sum|cksum|md5sum|sha1sum|sha224sum|sha256sum|sha384sum|sha512sum|shasum|sum] [-r] [-b] [-c] [-s <IP>]"


# #############################################
# Write the allowlist to the system
# #############################################

function write_image_wl {
    local img_wl_file=${1}
    echo "====> (whitelist manager) : storing whitelist ($img_wl_file) on filesystem}"
    cat ${img_wl_file} | tr -cd '\11\12\15\40-\176' | env LANG=C grep -v "["$'\x80'-$'\xff'"]" > /root/tmp2.txt 2>&1
    echo "====> (whitelist manager) :  whitelist ($img_wl_file) written to system"
}

# #############################################

# determine the image ID from os-release and motd.
# #############################################
function get_image_id {
    local _root=${1}
    touch ${_root}/etc/os-release > /dev/null 2>&1
    touch ${_root}/etc/motd  > /dev/null 2>&1
    export KEYLIME_IMG_ID=$(cat ${_root}/etc/os-release ${_root}/etc/motd | sha512sum | awk '{ print $1 }')
}
export -f get_image_id

# ###########################################
# file system measuring tool
# ###########################################

function measure_filesystem() {
    local whitelist=${1}
    local rootfs=${2}
    local extraexclude=${3}

    rm -f ${whitelist}
    touch ${whitelist}
    local excludelist="\bsys\b\|\brun\b\|\bproc\b\|\blost+found\b\|\bdev\b\|\bmedia\b\|\bmnt\b\|\bvar\b\|\btmp\b"
    echo "==> (whitelist manager): generating whitelist for ${rootfs} excluding ${extraexclude}"
    local dl=$(chroot ${rootfs} /bin/ls / | grep -v ${excludelist})
    for f in $dl
    do
        localexclude=0
        for e in ${extraexclude} ; do
            if [[ ${e} == ${f} ]] ; then localexclude=1; break ; fi
        done
        if [[ ${localexclude} == 1 ]] ; then continue ; fi
        echo "    ${rootfs}/$f"
        #chroot ${rootfs} find /${f} -fstype rootfs -o -xtype f -type l -o -type f -uid 0 -exec ${KEYLIME_ALGO}sum {} \; >> ${whitelist}
        chroot ${rootfs} find /${f} -fstype rootfs -o -xtype f -type l -o -type f -uid 0 -exec sha256sum {} \; >> ${whitelist}
    done
    echo "==> (whitelist manager): done with the generation of whitelist for ${rootfs} excluding ${extraexclude}"
}


# ###########################################
# load the boot aggregate
# ###########################################
echo "====> (whitelist manager) : storing boot aggregate ($ba) for node $KEYLIME_AGENT_UUID"
ba=$(grep ' boot_aggregate$' /sys/kernel/security/ima/ascii_runtime_measurements | awk '{ print $4 }' | sed "s/${KEYLIME_ALGO}://")
echo "${ba}  boot_aggregate" | tr -cd '\11\12\15\40-\176' | env LANG=C grep -v "["$'\x80'-$'\xff'"]" > /root/tmp2.txt 2>&1

function measure_wl() {
    local fs=${1}
    local exclude=${2}
    get_image_id ${fs}

    wlf=/tmp/${KEYLIME_IMG_ID}.txt

    echo "Measuring file system for ${KEYLIME_IMG_ID}"
    measure_filesystem ${wlf} ${fs}

    #write the white list to redis, since we have the lock.
    write_image_wl $wlf
}

# ###########################################
# we are going to measure all white lists pertaining to this node
# ###########################################

measure_wl / "target"
