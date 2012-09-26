from twisted.web import xmlrpc, server
from twisted.internet import reactor
from time import strftime
import pydoc
import datetime, time
from time import strftime
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func
from decimal import *
from sqlalchemy import or_
import rpc_groups
import dbconnect

class account(xmlrpc.XMLRPC):
	
	"""class name is aacount which having different store procedures"""
	def __init__(self):
		xmlrpc.XMLRPC.__init__(self)
