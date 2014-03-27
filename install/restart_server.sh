#!/system/bin/sh
# to restart abt process

export bin=/system/bin
export PATH=$bin:/usr/bin:/usr/sbin:/bin:$PATH
export MNT=/data/local/abt

# Enter chroot and kill the ABT server
busybox chroot $MNT /usr/bin/killall -v "abtstart"

# Start ABT server
busybox chroot $MNT /bin/bash -c "/root/ABTcore/abtstart"
# Sleep for 5 seconds so that ABT server can start efficiently
sleep 5

echo "ABT server is running, type Ctrl+c to exit."


