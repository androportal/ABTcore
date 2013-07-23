========
ABTcore
========

About
-----

This provides a remote server back-end to `ABT
<https://github.com/androportal/ABT>`_(client) and is derived from
`core_engine <www.gnukhata.org/core_engine>`_ of GNUkhata.

`PostgreSQL <http://www.postgresql.org/docs/9.1/static/tutorial.html>`_ is used as a database engine.
Refer `PostgreSQL Python tutorial <http://zetcode.com/db/postgresqlpythontutorial/>`_ for more information.

We have completely dropped an idea of ``stored procedures``, instead
we have implemented an `Object relational mapping` using `SQLAlchemy
<http://www.sqlalchemy.org/>`_ and used the psycopg2 module. 
It is a PostgreSQL database adapter for the Python programming language.

`Android-xmlrcp <http://code.google.com/p/android-xmlrpc/>`_ client
side (java)library is used to communicate with xmlrpc's of `ABTcore`.
It uses twisted module for executing rpc calls. A server reactor from
the twisted library starts a service on port ``7081`` with a published
object and listens on given port.

on x86 system
~~~~~~~~~~~~~

clone this repo by typing ::

   git clone -b postgres https://github.com/androportal/ABTcore.git

Install
------- 

Note: We highly recommend to perform this procedure on an `Ubuntu
<http://www.ubuntu.com/>`_ based system. User are free to use other
variant of GNU/Linux provided the package dependencies are met.

#. On an Ubuntu machine, dependencies can be installed using
   ``install.sh file``. Remember, this is one time effort.

#. ``cd`` to ``ABTcore`` directory and type ::
     
     sh install.sh
     
#. To run the server type ::

     sudo ./abtstart

<<<<<<< HEAD
=======
*WARNING*: This section is for advance users only! Developer who want
to contribute to this project can try this section. We are not
responsible for any damage to the device.

on x86 system
~~~~~~~~~~~~~

clone this repo by typing ::

   git clone https://github.com/androportal/ABTcore.git

Dependencies
~~~~~~~~~~~~

- libpcre3 
- libpcre3-dev
- libreadline5 
- libreadline6-dev 
- libpq5
- sqlite3     
- python-pip 
- python-sqlalchemy
- python-twisted
- python-dateutil

On an Ubuntu machine, these dependencies can be installed using
``apt-get`` ::

   sudo apt-get install libpcre3 libpcre3-dev
   sudo apt-get install libreadline5 libreadline6-dev libpq5  
   sudo apt-get install python-pip python-sqlalchemy
   sudo apt-get install python-twisted
   sudo apt-get install python-dateutil
to run the server, ``cd`` to directory ``ABTcore/`` and type ::
   
   sudo ./abtstart
>>>>>>> testing

Installing ABT frontend
~~~~~~~~~~~~~~~~~~~~~~~

<<<<<<< HEAD
Download and install ABT.apk from ``aakashlabs.org/builds/ABT.apk`` in your device.
=======
Please visit ``README`` section of `ABT
<https://github.com/androportal/ABT>`_ on installaion and relevant
changes in the source files


on Aakash (ARM-arch)
~~~~~~~~~~~~~~~~~~~~

You have to setup a ``PATH`` for ``adb`` on your system, please refer
ABT's README section "Importing ABT as an eclipse project". Once you
have downloaded the `SDK
<http://developer.android.com/sdk/index.html>`_, update it to
API-15(Icream Sandwich). and `export` adb's PATH using

SYNTAX ::

  export PATH=/home/${HOME}/<path-to-your-sdk/platform-tools:$PATH

for example, if you have downloaded Android's SDK in $HOME, then your
command should be ::

  export PATH=/home/andro/android-sdk-linux/platform-tools:$PATH

assuming ``$USER`` is **andro** in this case. 

Please remember that `adb` only supports 32-bit system, if your system
is 64-bit, you have to install ``ia32-libs-multiarch`` library to
support multi-architechture. On Ubuntu system, install
``ia32-libs-multiarch`` using ::

  sudo apt-get install ia32-libs-multiarch

Once ``adb`` is in place, attach USB data cable provided with Aakash
to your linux system and other end(USB Type-2 micro) to Aakash.

You need to push ``debug.sh`` to ``/data/local/`` to *start a server
manually*. Visit ``install`` directory within ``ABTcore`` (your cloned
repo) ::

   cd ABTcore/install/

and push ``debug.sh`` to ``/data/local/`` ::

   ./adb push debug.sh /data/local/

Once ``ABTcore`` and ``debug.sh`` is pushed inside the device, do ::

    adb shell

to get bash prompt on device. You have to enter the `chroot`
environment using ::

    cd /data/local/
    sh debug.sh

If your bash prompt says **root@localhost**, then you are inside the
chroot!. Now type ::

    cd /root/ABTcore
    ./abtstart

to start the server.

Now you can install an `APK <http://aakashlabs.org/builds/ABT.apk>`_
and start working

Updating present image
~~~~~~~~~~~~~~~~~~~~~~

If you want to work with update core, then you can ``push`` the
content of ``ABTcore/`` directory inside Aakash to PATH
``/data/local/abt/root/ABTcore`` (please refer this `link
<http://developer.android.com/tools/help/adb.html>`_ for adb usage).

to push latest content of ``ABTcore`` to ``/data/local/abt/root/``
type ::
  
  adb push ABTcore /data/local/abt/root/ABTcore

Note
~~~~

**ABTcore** was originally derived ``core_engine``.
We have `modified` the code to work with Android.
>>>>>>> testing


Help, bugs, feedback
~~~~~~~~~~~~~~~~~~~~

#. Users can mail their queries, feedback and suggestions at
   accounting-on-aakash@googlegroups.com

#. Developers/Contributor can raise issues at `github.com
   <https://github.com/androportal/ABTcore/issues>`_

#. Pull requests are most welcome

License
-------

GNU GPL Version 3, 29 June 2007.

Please refer this `link <http://www.gnu.org/licenses/gpl-3.0.txt>`_
for detailed description.

All rights belong to the National Mission on Education through ICT,
MHRD, Government of India.

