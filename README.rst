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


Installing ABT frontend
~~~~~~~~~~~~~~~~~~~~~~~

Download and install ABT.apk from ``aakashlabs.org/builds/ABT.apk`` in your device.


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

