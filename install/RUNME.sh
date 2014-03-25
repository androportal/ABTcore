#!/bin/bash
# to update ABTcore and restart abt process
#Note: Please export 'adb' path in bashrc

export bin=/system/bin
export PATH=$bin:/usr/bin:/usr/sbin:/bin:$PATH
export MNT=/data/local/abt

function update_ABTcore() {
	echo "Do you want to update ABTcore from github? (y/n)"
  read Ans
  if [ $Ans == "y" ] || [ $Ans == "Y" ]
  then
  	cd ../
  	git pull
  	cd install
  fi

	echo "Removing /data/local/abt/root/ABTcore..."
	adb shell rm -r /data/local/abt/root/ABTcore
	echo "Do you want to remove /data/local/abt/opt/abt? (y/n)"
  read Ans
  if [ $Ans == "y" ] || [ $Ans == "Y" ]
  then
  	adb shell rm -r /data/local/abt/opt/abt
  fi
	echo "Coping /data/local/abt/root/ABTcore..."
	adb push ../../ABTcore /data/local/abt/root/ABTcore
	echo "Coping update_abtcore.sh..."
	adb push update_abtcore.sh /data/local
	echo "Starting abtserver from chroot..."
	adb shell sh /data/local/update_abtcore.sh
	exit 0
}

# __init__
update_ABTcore
#updating


 
