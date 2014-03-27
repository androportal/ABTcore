#!/bin/bash
# Update ABTcore and restart abt process.
# Note: Please export 'adb' path in '~/.bashrc' file

export bin=/system/bin
export PATH=$bin:/usr/bin:/usr/sbin:/bin:$PATH
export MNT=/data/local/abt


function update_ABTcore() {

    # Not used variables
    local GITHUB_URL=""
    local GITHUB_BRANCH=""

    read -p "Do you want to update ABTcore from GitHub? (y/n): " ans
    if [ $ans == "y" ] || [ $ans == "Y" ]
    then
  	pushd ../		# Go to previous directory to update repo
  	git pull 
  	popd			# Come back to install/ directory
	unset ans			# Unset variable 'ans'
    fi

    # Remove previous core files from device
    echo "Removing /data/local/abt/root/ABTcore..."
    adb shell rm -r /data/local/abt/root/ABTcore
    
    read -p "Do you want to remove /data/local/abt/opt/abt? (y/n): " ans
    if [ $ans == "y" ] || [ $ans == "Y" ]
    then
	echo "Removing /data/local/abt/opt/abt..."
  	adb shell rm -r /data/local/abt/opt/abt
    fi
    unset ans
    
    # Copy new core files to device
    echo "Coping /data/local/abt/root/ABTcore..."
    adb push ../../ABTcore /data/local/abt/root/ABTcore
    
    echo "Coping restart_server.sh..."
    adb push restart_server.sh /data/local
    
    # Restart ABT server
    echo "Starting abtserver from chroot..."
    adb shell sh /data/local/restart_server.sh
}

# __init__
update_ABTcore
# updating


 
