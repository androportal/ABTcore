#!/bin/bash
#installing dependencies for abt
# Check for admin rights. If user is not an admin user, exit the script
if [ $UID != 0 ]
then
   echo "You need to be root to run this script! Exiting..  In distros like Ubuntu, type sudo before this command"
   exit
fi
echo "installing dependencies "
sudo apt-get install -y --force-yes libpcre3 libpcre3-dev python-psycopg2 python-twisted
sudo apt-get install libreadline5 libreadline6-dev libpq5  
sudo apt-get install python-pip python-sqlalchemy

# if apt-get install was successful then we know we have the pre-requisites
if [ $? -eq 0 ]; then
	#let's move to the src folder and start installing from sources.
	#we will compile postgresql,nginx to /usr/gnukhata
	echo "setting up the database utilities "

	cd src
	tar zxf postgresql-9.1.2.tar.gz

	cd postgresql-9.1.2
	./configure --prefix=/usr --without-zlib >/dev/null
	sudo make >/dev/null
	sudo make install >/dev/null
	if [ $? -eq 0 ]; then
		cd .. 
		sudo useradd postgres
		sudo mkdir /var/data
		sudo chown postgres /var/data >/dev/null
		sudo su -c "initdb -D /var/data" postgres
		echo "installed database utilities and successfully created database files "
	else
		echo "installer failed to setup the database server, can not go ahead with setup"
		exit
	fi
else
	echo "Couldn't install the required  dependencies."
	exit 
fi
echo "performing basic cleanup opperations"
sudo rm -rf postgresql-9.1.2

echo "congratulations! you have successfully setup ABT"
echo "you can now start ABT by typing 'sudo ./abtstart'"

