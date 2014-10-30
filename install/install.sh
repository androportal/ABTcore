#!/bin/bash
# installation script for Aakash Business Tool

ABT_TARBALL_SRC="http://www.it.iitb.ac.in/AakashApps/repo/abt.tar.gz"

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
# ---------algo-----------
# if image,
#   push image 
# elif tar
#   extract tar
#   push image
# else
#   download tar
#   extract tar
#   push image
# fi
# --------------------
# BUG: check for an image size b4 pushing
    
    if [ -f abt.img ]; then
    	echo "Sending abt.img, this will take around 5 minutes"
    	./adb push abt.img /mnt/sdcard/
    elif [ -f abt.tar.gz ]; then
    	echo "extracting image..."
    	tar -xvzf abt.tar.gz
    	if [ -f abt.img ]; then
    	    echo "Sending abt.img, this will take around 5 minutes"
    	    ./adb push abt.img /mnt/sdcard/
    	else
    	    echo "file: abt.img not found!"
    	    exit 1
    	fi	
    else
    	echo "downloading image, please wait..."
    	wget -c ${ABT_TARBALL_SRC}
    	if [ -f abt.tar.gz ]; then
    	    echo "extracting image..."
    	    tar -xvzf abt.tar.gz
    	    if [ -f abt.img ]; then
    		echo "Sending abt.img, this will take around 5 minutes"
    		./adb push abt.img /mnt/sdcard/
    	    else
    		echo "file: abt.img not found!"
    	    exit 1
    	    fi	
    	fi
    fi

    if [ -f debug.sh ]; then
	echo "Sending debug.sh...."
	./adb push debug.sh  /data/local/
    else
	echo "file: debug.sh not found!"
	exit 1
    fi
    
    ./adb shell sync
    
    if [ -f ABT.apk ]; then
	echo "Installing APK... "
	./adb install -r ABT.apk
    else
	echo "Downloading APK...."
	wget -c http://aakashlabs.org/builds/ABT.apk
	if [ -f ABT.apk ]; then
	    echo "Installing APK... "
	    ./adb install -r ABT.apk
	fi
    fi

    echo "Device will reboot in 5 seconds..press cntrl + c  to abort auto rebooot.."
    sleep 5
    ./adb reboot
}

# __init__
connect_device
#installing

