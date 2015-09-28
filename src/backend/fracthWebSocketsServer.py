import asyncio
import websockets

@asyncio.coroutine
def handler(websocket, path):

	while True:

		# Receive
    	message = yield from websocket.recv()
    	print("< {}".format(message))
    	if message is None:
    		break
    
    	# Parse message
    	parsedJson = json.loads(message)

    	greeting = "Hello {}!".format(name)
    	yield from websocket.send(greeting)
    	print("> {}".format(greeting))
    
    return # closes connection

def parse_and_create_jobs(self):
    if (TRACE): print("%-20s :: %s" % ("ENTER", sys._getframe().f_code.co_name))

    # Get POST data
    if (TRACE): print("%-20s :: %s" % ("GET DATA", sys._getframe().f_code.co_name))
    post_content_length = int(self.headers.get('Content-Length'))
    post_query = self.rfile.read( post_content_length )
    render_settings_json = json.loads(post_query.decode('utf-8'))
    # post_data  = urlparse.parse_qs( post_query )

    # Construct a render job
    if (TRACE): print("%-20s :: %s" % ("PARSING DATA", sys._getframe().f_code.co_name))
    render_settings = fcc.RenderSettings(json_data=render_settings_json)

    # TODO: Keep track of job identifiers
    if (TRACE): print("%-20s :: %s" % ("QUEUE JOB", sys._getframe().f_code.co_name))
    job = render_settings
    computeClient.put_job( job )

    if (TRACE): print("%-20s :: %s" % ("OBTAIN RESULT", sys._getframe().f_code.co_name))
    result = computeClient.get_result()
    json_friendly_result = result.__dict__

    # Send to client
    if (TRACE): print("%-20s :: %s" % ("SEND", sys._getframe().f_code.co_name))
    self.send_response(200)
    self.send_header('Content-type','application/json')
    self.end_headers()
    self.wfile.write( bytes(json.dumps(json_friendly_result), 'utf-8') )
    
    if (TRACE): print("%-20s :: %s" % ("EXIT", sys._getframe().f_code.co_name))

SERVER_ADDRESS = 'localhost'
SERVER_PORT    = 8080

if __name__ == '__main__':
    server = None
    try:
        # Create a web server and define the handler to manage the
        # incoming request
        server = websockets.serve(handler, SERVER_ADDRESS, SERVER_PORT)
        print('Started websockets server on port ' , SERVER_PORT)

        # Create connection to the Queue Manager for render jobs.
        computeClient = fcl.ComputeClient( address=('', 50000), authkey='abracadabra' )

        # Wait forever for incoming http requests
        print('Starting server, use <Ctrl-C> to stop')
        asyncio.get_event_loop().run_until_complete(server)

    except KeyboardInterrupt:
        print ('^C received, shutting down the web server')
        server.socket.close()