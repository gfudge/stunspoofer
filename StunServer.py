#!/usr/bin/python

import time, sys, SocketServer, threading, struct, Queue
from collections import namedtuple

storeIPQueue = Queue.Queue()

class StunServerThread (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.isAlive = True
		# Default port of STUN server over UDP
		self.UDPPort = 3478
		self.handler = StunHandler
		SocketServer.UDPServer.allow_reuse_address = True
		self.stunServer = SocketServer.UDPServer(('', self.UDPPort),self.handler)

	def run(self):
		while(self.isAlive == True):
			self.stunServer.handle_request()
			#self.die()
	
	def die(self):
		self.isAlive = False

class StunHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		try:	
			StunPacket = namedtuple("StunPacket", "type length cookie id")
			request, socket = self.request
			request = request.upper()
			# IP from received packet, ignore port
			userIP = self.client_address[0]
			print "Got IP: " + str(userIP)
			storeIPQueue.put(str(userIP).strip())
			# Unpack as packet according to rfc5389
			newStunPacket = StunPacket._make(struct.unpack('>HHi%ds' %(12), request[0:20]))
			#print str(newStunPacket)
		except Exception,e:
			print "Handler Error: "
			print str(e)

class StunServer():
	def __init__(self, maxThreads):
		self.maxThreads = maxThreads
		self.Threads = []

	def run(self):
		print "Spinnin' up threads"
		while True:
			try:
				while(len(self.Threads) < self.maxThreads):
					self.addThread()
			
			except KeyboardInterrupt:
				self.killAllThreads()
				sys.exit()

	def addThread(self):
		print "Adding Thread..."
		self.Threads.append(StunServerThread())
		self.Threads[-1].start()

	def killAllThreads(self):
		for Thread in self.Threads:
			Thread.die()
		sys.exit(1)

class IPStorage(threading.Thread):
	def __init__(self, fileName):
		threading.Thread.__init__(self)
		self.fileName = str(fileName)
		self.IPList = []		

	def run(self):
		try:	
			self.storageFile = open(self.fileName, 'a+')
			while(True):
				self.IPList = self.storageFile.readlines()
				#print self.IPList
				while not storeIPQueue.empty():	
					tempIP = storeIPQueue.get()
					print "DEBUG: " + str(tempIP)
					if tempIP not in self.IPList:
						self.storageFile.write(str(tempIP) + "\n")

		except Exception,e:
			print "File Error: " + str(e)
			self.storageFile.close()		
def main():
	storage = IPStorage('caught_ips.txt')
	stunServer = StunServer(maxThreads=4)
	storage.start()
	stunServer.run()

if __name__== "__main__":
	main()
