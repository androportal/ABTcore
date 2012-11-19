# this file is only specific for GNUkhata,[it solved larger db problem]
export bin=/system/bin
export PATH=$bin:/usr/bin:/usr/sbin:/bin:$PATH
export TERM=linux
export HOME=/root
export GKMNT=/data/local/gkaakash
export GKIMG=/mnt/sdcard/gkaakash.img
export SD=0

function start-ac() {
    echo "mounting" >> /sdcard/mounting.txt
    busybox mkdir -p ${GKMNT}
    # mounting essential file systems to chroot for gkaakash
    busybox mount -o loop ${GKIMG} ${GKMNT}
    busybox mount -t proc proc ${GKMNT}/proc
    busybox mount -o bind /dev ${GKMNT}/dev
    busybox mount -t sysfs sysfs ${GKMNT}/sys
    busybox chroot ${GKMNT} /bin/bash -c "mount /dev/pts" 
    busybox chroot ${GKMNT} /bin/bash -c "source /root/.bashrc"
    # busybox chroot ${GKMNT} /bin/bash -c "python /root/gkAakashCore/gkstart &> '/dev/null' &"
    busybox chroot ${GKMNT} /bin/bash -c "/root/gkAakashCore/gkstart"
    
    # kill n restart again
    #busybox chroot /data/local/gkaakash /bin/bash -c "/root/gkAakashCore/gkstart"
    #busybox chroot /data/local/gkaakash /bin/bash -c "killall gkstart"
    #busybox chroot /data/local/gkaakash /bin/bash -c "killall python"
    #busybox chroot /data/local/gkaakash /bin/bash -c "/root/gkAakashCore/gkstart"
}

while [ $SD -eq 0 ]
do
    if [ -f ${GKIMG} ]
    then
	SD=1
	start-ac
    fi
sleep 1 
done



# busybox chroot /data/local/gkaakash /bin/bash -c "/root/gkAakashCore/gkstart"
# #sh debug.sh
# busybox chroot /data/local/gkaakash /bin/bash -c "killall gkstart"
# busybox chroot /data/local/gkaakash /bin/bash -c "killall python"
# busybox chroot /data/local/gkaakash /bin/bash -c "/root/gkAakashCore/gkstart"


