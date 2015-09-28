from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import socket
import sys
import urllib.parse
import json


import random

import fracthComputeCore   as fcc
import fracthComputeClient as fcl

TRACE = True
PORT_NUMBER = 8080

# This class will handle any incoming request from
# a browser 
class Handler(BaseHTTPRequestHandler):

	def get_file(self, path):
		print   ('Get request received')
		self.send_response(200)
		if path.endswith('.html'):
			self.send_header('Content-type','text/html')
		if path.endswith('.js'):
			self.send_header('Content-type','application/javascript')
		if path.endswith('.css'):
			self.send_header('Content-type','text/css')
		self.end_headers()
		f = open("."+path)
		self.wfile.write( bytes(f.read(), 'utf-8') )
		f.close()
		return

	def register_compute_server():
		# TODO: security check?
		
		# This takes a post argument and adds a compute server to the self.compute_servers variable.
		pass
		

	def get_compute_server(self):
		self.compute_servers = [ "localhost:10000" ]
		# If there is at least one compute server available, a random one will be retured to the client.
		if (self.path.endswith("/new")):
			pass
		elif (self.path.endswith("/whatever")):
			pass
		else:
			random_server = random.choice(self.compute_servers)
			self.wfile.write( bytes(random_server, 'utf-8') )


	# Handler for the GET requests
	def do_GET(self):
		print(self.path)
		print(self.request)

		if (self.path == "/"):
			self.get_file('/index.html')
			return

		if (self.path.startswith("/computeserver")):
			self.get_compute_server()
			return

		if (   self.path.endswith(".html") \
		or     self.path.endswith(".js"  ) \
		or     self.path.endswith(".css" ) ):
			if (".." in self.path): return
			self.get_file(self.path)
			return
	# End GET handler

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
	server = None
	try:
		# Create a web server and define the handler to manage the
		# incoming request
		server = ThreadedHTTPServer(('', PORT_NUMBER), Handler)
		print('Started httpserver on port ' , PORT_NUMBER)

		# Create connection to the Queue Manager for render jobs.
		computeClient = fcl.ComputeClient( address=('', 50000), authkey='abracadabra' )

		# Wait forever for incoming http requests
		print('Starting server, use <Ctrl-C> to stop')
		server.serve_forever()

	except KeyboardInterrupt:
		print ('^C received, shutting down the web server')
		server.socket.close()
