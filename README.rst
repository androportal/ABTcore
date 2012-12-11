============
gkAakashCore
============

About
-----

This provides a back-end to `gkAakash
<https://github.com/androportal/gkAakash>`_ and is derived from
`core_engine <www.gnukhata.org/core_engine>`_ of GNUkhata.

`Sqlite3 <http://www.sqlite.org/>`_ is used as a database engine, and
python-sqlite3 binding is done through `pysqlite2
<http://pypi.python.org/pypi/pysqlite/>`_. `Android-xmlrcp
<http://code.google.com/p/android-xmlrpc/>`_ client side (java)library
is used to communicate with xmlrpc's of `gkAakashCore`. It uses
twisted module for executing rpc calls. A server reactor from the
twisted library starts a service on port ``7081`` with a published
object and listens on given port. We have completely dropped an idea of
``stored procedures``, instead we have implemented an `Object
relational mapping` using `SQLAlchemy <http://www.sqlalchemy.org/>`_


Install
-------

Note: We highly recommend to perform this installation from an `Ubuntu
<http://www.ubuntu.com/>`_ based system. User are free to use other
variant of GNU/Linux as long as all the package dependencies are met.

#. Please remember that currently adb only supports 32-bit system, if
   your system is 64-bit, then install ``ia32-libs-multiarch`` library
   to support multi-architecture. On Ubuntu system, install
   ``ia32-libs-multiarch`` using 
   ::

     sudo apt-get install ia32-libs-multiarch

#. Download and extract `install.zip
   <https://github.com/downloads/androportal/gkAakashCore/install.zip>`_

#. Connect Aakash to your system using an USB data cable.

#. Download compressed image file from this `link
   <https://github.com/downloads/androportal/gkAakashCore/gkaakash.img.tar.bz2>`_
   or you can download an entire image from `here
   <https://github.com/downloads/androportal/gkAakashCore/gkaakash.img>`_

#. Uncompress the file using, 
   ::

      tar -xvjf gkaakash.img.tar.bz2

#. and copy ``gkaakash.img`` file to ``install`` directory
   ::
      
      cp -v gkaakash.img install

#. ``cd`` to ``install`` directory 
   ::
      
      cd install
      
#. and execute ``install.sh`` 
   ::
      
      sudo ./install.sh

Wait for the script to copy all necessary files to Aakash. After
successful installation the device will reboot for changes to take
effect.

Contribute
----------

Usage
~~~~~

WARNING: This section is for advance users only! Developer who want to
contribute to this project can try this section. We are not responsible
for any damage to the device.


clone this repo by typing

::

   git clone https://github.com/androportal/gkAakashCore.git


Dependencies
~~~~~~~~~~~~

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

On an Ubuntu machine, these dependencies can be installed using
``apt-get``

::

   sudo apt-get install libpcre3 libpcre3-dev
   sudo apt-get install libreadline5 libreadline6-dev libpq5
   sudo apt-get install sqlite3 python-pysqlite2     
   sudo apt-get install python-pip python-sqlalchemy
   sudo apt-get install python-twisted


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

for example, if you have downloaded Android's SDK in $HOME, then your command
should be

::

   export PATH=/home/andro/android-sdk-linux/platform-tools:$PATH

assuming ``$USER`` is **andro** in this case. 

Please remember that currently adb only supports 32-bit system, if
your system is 64-bit, you have to install ``ia32-libs-multiarch``
library to support multi-architechture. On Ubuntu system, install
``ia32-libs-multiarch`` using

::

     sudo apt-get install ia32-libs-multiarch

Once adb is in place, attach USB data cable provided with Aakash to
your linux system and other end(micro-socket) to Aakash. Now you can ``push``
the content of ``gkAakashCore/`` directory inside Aakash to PATH
``/data/local/gkaakash/root/gkAakashCore`` (please refer this `link
<http://developer.android.com/tools/help/adb.html>`_ for adb
usage). Please note that we have a ``chroot`` environment under
``/data/local/gkaakash`` on Aakash. Details of chroot'ing is **not**
provided here. We will soon upload an chroot image which can be
downloaded and should be kept in ``/mnt/sdcard/`` of Aakash.

Once ``gkAakashCore`` is pushed inside the device, do 

::

    adb shell

to get bash prompt on device. You have to enter chroot environment
using

::

    cd /data/local/
    sh debug.sh

Note: if ``debug.sh`` does not exit in ``/data/local/``, push it to
Aakash's ``/data/local/`` path. Visit ``install`` directory within
``gkAakashCore`` (your cloned repo)

::

   cd gkAakashCore/install/

and push ``debug.sh`` to ``/data/local/``

::

   ./adb push debug.sh /data/local/

If your bash prompt says **root@localhost**, you are inside the
chroot!. Now type

::

    cd /root/gkAakashCore
    ./gkstart

to start the server.

Now you can install an APK and start working


Note
~~~~

**gkAakashCore** is based on ``core_engine`` revision ``159``. Original
code can be obtained by typing

::

   hg clone -r 159 http://gnukhata.org/core_engine

you must have `mercurial <http://mercurial.selenic.com/>`_ installed
on your system. We have `modified` the code to suite our need.


Help, bugs, feedback
~~~~~~~~~~~~~~~~~~~~

#. Users can mail their queries, feedback and suggestions at
   accounting-on-aakash@googlegroups.com

#. Developers/Contributor can raise issues at `github.com
   <https://github.com/androportal/gkAakashCore/issues>`_

#. Pull requests are most welcome

License
-------

GNU GPL Version 3, 29 June 2007.

Please refer this `link <http://www.gnu.org/licenses/gpl-3.0.txt>`_
for detailed description.

All rights belong to the National Mission on
Education through ICT, MHRD, Government of India.

