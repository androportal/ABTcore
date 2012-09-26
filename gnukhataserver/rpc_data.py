
from pysqlite2 import dbapi2 as sqlite #import the database connector 
from twisted.web import xmlrpc, server #import the twisted modules for executing rpc calls and also to implement the server
from twisted.internet import reactor #reactor from the twisted library starts the server with a published object and listens on a given port.

#note that all the functions to be accessed by the client must have the xmlrpc_ prefix.
#the client however will not use the prefix to call the functions. 

class data(xmlrpc.XMLRPC):#inherit the class from XMLRPC to make it publishable as an rpc service.

	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)

 	
	def xmlrpc_getStateNames(self):
		'''
		def xmlrpc_getStateNames : purpose
			It will return list of all the distinct states present in the state_city table
		'''
		try:
			conn = sqlite.connect("/opt/places.db")
			cur = conn.cursor()
			result = cur.execute("select distinct state from state_city")
			rows =result.fetchall()
			states = []
			for row in rows:
				states.append(list(row))
			conn.close()
			return states
		except:
			return False

	def xmlrpc_getCityNames(self,queryParams):
		'''
		def xmlrpc_getCityNames : purpose
			Takes one parameters statename
			It will return list of all the cities for 
		'''
		try:
			conn = sqlite.connect("/opt/places.db")
			cur = conn.cursor()
			result =  cur.execute("select city from state_city where state = '%s'"%str(queryParams[0]))
			rows = result.fetchall()
			cities = []
			for row in rows:
				cities.append(row[0])
			return cities
		except:
			return False

