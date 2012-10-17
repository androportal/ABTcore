============
gkAakashCore
============

About
-----

This provides a backend to `gkAakash
<https://github.com/androportal/gkAakash>`_ and is based on
`core_engine <www.gnukhata.org/core_engine>`_ of GNUkhata. 

`Sqlite3 <http://www.sqlite.org/>`_ is used as a database engine, and
python-sqlite3 binding is done through `pysqlite2
<http://pypi.python.org/pypi/pysqlite/>`_. `Android-xmlrcp
<http://code.google.com/p/android-xmlrpc/>`_ client side (java)library
is used to communicate with xmlrpc's of `gkAakashCore`. It uses
twisted module for executing rpc calls and a service is running at
port ``7081``. A server reactor from the twisted library start this
service with a published object and listens on given port. We have
completly dropped an idea of ``stored procedures``, instead we have
implemented an `Object relational mapping` using `SQLAlchemy
<http://www.sqlalchemy.org/>`_


Dependencies
------------

- libpcre3 
- libpcre3-dev
- libreadline5 
- libreadline6-dev 
- libpq5
- sqlite3     
- python-pysqlite2 
- python-pip 
- python-sqlalchemy
- python-twisted


On an ubuntu machine, these dependencies can be installed using
``apt-get``

::

   sudo apt-get install libpcre3 libpcre3-dev
   sudo apt-get install libreadline5 libreadline6-dev libpq5
   sudo apt-get install sqlite3 python-pysqlite2     
   sudo apt-get install python-pip python-sqlalchemy
   sudo apt-get install python-twisted

Usage
-----

clone this repo by typing

::

   git clone https://github.com/androportal/gkAakashCore.git

on x86 system
~~~~~~~~~~~~~

to run the server, ``cd`` to directory ``gkAakashCore/`` and type

::
   
   sudo ./gkstart

on Aakash (ARM-arch)
~~~~~~~~~~~~~~~~~~~~

You have to setup a ``PATH`` for ``adb`` on your system, please refer
gkAakash's README section "Importing gkAakash as an eclipse
project". Once you have downloaded the `SDK
<http://developer.android.com/sdk/index.html>`_, update it to
API-15(Icream Sandwich). and `export` adb's PATH using

SYNTAX

::

    export PATH=/home/${HOME}/<path-to-your-sdk/platform-tools:$PATH

for example, if you have downloaded sdk in $HOME, then your command
should be

::

   export PATH=/home/andro/android-sdk-linux/platform-tools:$PATH

assuming ``$USER`` is **andro** in this case. Please remember that
currently adb only supports 32-bit system, if your system is 64-bit,
you have to install ``ia32-libs`` library to support
multi-architechture.

On ubuntu system, install ia32-libs using

::

     sudo apt-get install ia32-libs

Once adb is in place, you can ``push`` entire ``gkAakashCore``
directory inside Aakash in PATH
``/data/local/linux/root/gkAakashCore`` (please refer this `link
<http://developer.android.com/tools/help/adb.html>`_ for adb
usage). Please note that we have a ``chroot`` environment under
``/data/local/linux`` on Aakash. Details of chroot'ing is **not**
provided here. We will soon upload an chroot image which can be
downloaded and should be kept in ``/mnt/sdcard`` of Aakash.

Once ``gkAakashCore`` is pushed inside the device, do 

::

    adb shell

to get bash prompt on device. You have to enter chroot environment
using,

::

    cd /data/local/
    sh debug.sh

If your bash prompt says **root@localhost**, you are inside the
chroot!. Now type

::

    cd /root/gkAakashCore
    ./gkstart

to start the server

Note
----

**gkAakashCore** is based on ``core_engine`` revision ``159``. Original
code can be obtained by typing

::

   hg clone -r 159 http://gnukhata.org/core_engine

you must have `mercurial <http://mercurial.selenic.com/>`_ installed
on your system. We have `modified` the code to suite our need.


License
-------

GNU GPL Version 3, 29 June 2007.

Please refer this `link <http://www.gnu.org/licenses/gpl-3.0.txt>`_
for detailed description.

All rights belong to the National Mission on
Education through ICT, MHRD, Government of India.

