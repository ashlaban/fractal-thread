from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import socket
import sys
import urlparse
import json


import random

import fracthComputeCore   as fcc
import fracthComputeClient as fcl

TRACE = True
PORT_NUMBER = 8080

# This class will handle any incoming request from
# a browser 
class myHandler(BaseHTTPRequestHandler):

	compute_servers = [ "localhost:1234", "localhost:2345" ]

	def get_file(self, path):
		print   ('Get request received')
		self.send_response(200)
		if path.endswith('.html'):
			self.send_header('Content-type','text/html')
		if path.endswith('.js'):
			self.send_header('Content-type','application/javascript')
		self.end_headers()
		f = open("."+path)
		self.wfile.write(f.read())
		f.close()
		return

	def register_compute_server():
		# TODO: security check?
		
		# This takes a post argument and adds a compute server to the self.compute_servers variable.
		pass
		

	def get_compute_server(self):
		# If there is at least one compute server available, a random one will be retured to the client.
		if (self.path.endswith("/new")):
			pass
		elif (self.path.endswith("/whatever")):
			pass
		else:
			random_server = random.choice(compute_servers)
			self.wfile.write(random_server)


	# Handler for the GET requests
	def do_GET(self):
		print self.path
		print self.request

		if (self.path == "/"):
			self.get_file('/index.html')

		if (self.path.startswith("/computeserver")):
			self.get_compute_server()

		if (   self.path.endswith(".html") \
		or     self.path.endswith(".js"  ) ):
			if (".." in self.path): return
			self.get_file(self.path)
	# End GET handler
	
	def do_POST(self):
		if (TRACE): print "ENTER::myHandler::do_POST"
		print "POST received."

		# Get POST data
		print "Getting POST data."
		post_content_length = int(self.headers.getheader('Content-Length'))
		post_query = self.rfile.read( post_content_length )
		post_data  = urlparse.parse_qs( post_query )

		# Construct a render job
		print "Parsing POST data and building job."
		render_settings = fcc.RenderSettings()
		render_settings.x      = float(post_data["x"][0])
		render_settings.y      = float(post_data["y"][0])
		render_settings.width  = float(post_data["width"][0])
		render_settings.height = float(post_data["height"][0])

		render_settings.pixel_x      = int(post_data["pixel_x"][0])
		render_settings.pixel_y      = int(post_data["pixel_y"][0])
		render_settings.pixel_width  = int(post_data["pixel_width"][0])
		render_settings.pixel_height = int(post_data["pixel_height"][0])

		render_settings.zoom     = float(post_data["zoom"][0])
		render_settings.max_iter = int(post_data["max_iter"][0])
		# render_settings.c        = float(post_data["c"][0])

		render_settings.num_sample_points = int(post_data["num_sample_points"][0])
		render_settings.data = None

		# TODO: Keep track of job identifiers
		print "Sending job to compute farm."
		job = render_settings
		computeClient.put_job( job )

		print "Obtaining result."
		result = computeClient.get_result()
		json_friendly_result = result.__dict__

		# Format output
		# output = {}
		# output["pixel_x"] = str(render_settings.pixel_x)
		# output["pixel_y"] = str(render_settings.pixel_y)
		# output["pixel_width"]  = str(render_settings.pixel_width)
		# output["pixel_height"] = str(render_settings.pixel_height)
		# output["data"] = result

		# Send to client
		print "Writing to client."
		self.send_response(200)
		self.send_header('Content-type','application/json')
		self.end_headers()
		self.wfile.write( json.dumps(json_friendly_result) )
		
		if (TRACE): print "EXIT::myHandler::do_POST"

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
	server = None
	try:
		# Create a web server and define the handler to manage the
		# incoming request
		server = ThreadedHTTPServer(('', PORT_NUMBER), myHandler)
		print 'Started httpserver on port ' , PORT_NUMBER

		# Create connection to the Queue Manager for render jobs.
		computeClient = fcl.ComputeClient( address=('', 50000), authkey='abracadabra' )

		# Wait forever for incoming http requests
		print 'Starting server, use <Ctrl-C> to stop'
		server.serve_forever()

	except KeyboardInterrupt:
		print ('^C received, shutting down the web server')
		server.socket.close()