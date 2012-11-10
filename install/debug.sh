#!/system/bin/sh
# /data/local/debug.sh
# to debug chroot of 'gkAakash'

export bin=/system/bin
export PATH=$bin:/usr/bin:/usr/sbin:/bin:$PATH
export TERM=linux
export HOME=/root
export MNT=/data/local/gkaakash

if [ ! -d $MNT ]
then
mkdir -p $MNT
fi

busybox mount -t proc proc $MNT/proc
busybox mount -t sysfs sysfs $MNT/sys 
busybox mount -o bind /dev $MNT/dev
# setting proxy (!!!! for internal use only !!!!)
busybox chroot $MNT /bin/bash -c "source /root/.bashrc"
# starting 'gkstart'
# busybox chroot /data/local/linux /bin/bash -c "python /root/gkAakashCore/gkstart &>'/dev/null'&"
# entering the chroot environment - for debugging (uncomment line below)
busybox chroot $MNT /bin/bash
