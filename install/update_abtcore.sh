#!/system/bin/sh
# to restart abt process

export bin=/system/bin
export PATH=$bin:/usr/bin:/usr/sbin:/bin:$PATH
export MNT=/data/local/abt

# entering the chroot environment and kill the abt server
busybox chroot $MNT /usr/bin/killall -v "abtstart"
# staring abt server
busybox chroot $MNT /bin/bash -c "/root/ABTcore/abtstart"
sleep 5
#remove update_abtcore.sh
rm -r /data/local/update_abtcore.sh
echo "ABT server is running, please press CTR+c or CTR+z to exit..."


