#!/bin/bash
# installation script for gkAakash

chmod +x ./adb

function connect_device() {
    local ADB_DEVICES=""
    # try to connect to device, loop till the device gets connected
    while [ "$ADB_DEVICES" == "" ]
    do
        killall adb
	./adb kill-server
        ./adb start-server
        echo "trying to connect to device ..."
        ADB_DEVICES=$(./adb devices | awk '{print $2}' | grep "device")
	if [ "${ADB_DEVICES}" == "device" ];
	then
	    echo "installing ..."
	    installing
	fi
    done
}

function installing() {

    echo "Sending aakash.sh..."
    ./adb push aakash.sh /data/local/
    
    echo "Sending preinstall.sh..."
    ./adb push preinstall.sh /system/bin/
    
    echo "Sending debug.sh...."
    ./adb push debug.sh  /data/local/
    
    echo "Sending gkaakash.img, this will take around 5 minutes "
    #./adb push gkaakash.img /mnt/sdcard/
    
    ./adb shell sync
    
    echo "Installing APK... "
    ./adb install gkaakash.apk
    
    echo "Device will reboot in 5 seconds..press cntrl + c  to abort auto rebooot.."
    sleep 5
    ./adb reboot
}

# __init__

connect_device