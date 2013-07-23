.. Aakash Business Tool documentation master file, created by
   sphinx-quickstart on Thu Jan 31 17:44:34 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Aakash Business Tool's documentation!
================================================
	**Aakash Business Tool core(ABTcore)** provides a Back-end to ABT java client
	
	This provides all the accounting functionality completely written in `Python
	<http://docs.python.org/2/tutorial/>`_ language.
	and used twisted liabrary to implement xmlrpc server and to access xmlrpc functions and
	android-xmlrpc client access liabrary at client side and used Sqlite3
	database server to maintain data.
	
	We have completely dropped an idea of ``stored procedures``, 
	instead we have implemented an ``Object Relational Mapping`` using SQLAlchemy.
  
  	**ABTcore** includes three parts:
  		#. abtstart
  		#. abtserver
  		#. modules
  		#. src  
  		
.. toctree::
   :maxdepth: 2
   
abtstart
--------
	+ It is an executable file, it will responsible to run entire ``ABTcore``
 		- this is an executable file.
		- this is calling function calls runabt() from ``rpc_main.py`` and start the ``ABTcore``. 
		
	+ In ``abtstart`` you are able to see system command's , it's basically written to maintain databse files loacally.
		- import rpc_main
		- provided ``places.db`` database file in ``ABTcore/src`` which maintains data about ``state`` and ``cities``.
		- copy ``places.db`` database file in /opt/abt/.
		- create folder ``abt`` to maintain all files need to work ABT.
		- create ``db`` directory to host all the database files , to keep all record of organisation.
		
	+ All the database files of organisations will be there at ``/opt/abt/db``.


abtserver
---------
main
++++
.. automodule:: abtserver.rpc_main
   :members:

Account
+++++++
.. automodule:: abtserver.rpc_account
   :members:
   
Groups
+++++++

.. automodule:: abtserver.rpc_groups
   :members:

dbconnect
+++++++++
.. automodule:: abtserver.dbconnect
   :members:

getaccountsbyrule
+++++++++++++++++
.. automodule:: abtserver.rpc_getaccountsbyrule
   :members:

Transaction
+++++++++++ 
.. automodule:: abtserver.rpc_transaction
   :members:
   
Reports
+++++++ 
.. automodule:: abtserver.rpc_reports
   :members:
  
Organisation
++++++++++++
.. automodule:: abtserver.rpc_organisation
   :members:
   
   
User
++++
.. automodule:: abtserver.rpc_user
   :members:
   

Data
++++
.. automodule:: abtserver.rpc_data
   :members:

modules
-------
blankspace
++++++++++

.. automodule:: modules.blankspace
   :members:  
   
src
---
	* This is useful for only devloper's
	* It will have dependencies like ``places.db`` file.
	* also have some dummy databases for devloper's

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

