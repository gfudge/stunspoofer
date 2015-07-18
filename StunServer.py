#!/usr/bin/python

import time, sys, SocketServer, threading, struct

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
		while(True):
			self.stunServer.handle_request()
	
	def die(self):
		self.isAlive = False

class StunHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		try:	
			print "New Request"
			request, socket = self.request
			request = request.upper()
			print request
		except:
			print "Handler Error"

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

def main():
	stunServer = StunServer(maxThreads=4)
	stunServer.run()

if __name__== "__main__":
	main()
