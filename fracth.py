#!/usr/bin/env python

# import fracthComputeServer as fcs
# import fracthWebServer     as fws
# import fracthComputeClient as fcc
# 
# TODO: Logging to separate files!
# TODO: python fracth.py --stop c n 5 --start n 3 --restart w

import subprocess
import argparse

import json

parser = argparse.ArgumentParser(description='Commandline utility to start the fracth servers and clients.')

# Compute server
parser.add_argument('-c, --compute-server'     , dest='compute_server'     , action='store_true',           default=False,
                   help='start an instance of the comptue server.')
parser.add_argument('-s, --compute-server-port', dest='compute_server_port', action='store'     , type=int, default=50000,
                   help='port that the compute server should be running on.')

# Web server
parser.add_argument('-w, --web-server'     , dest='web_server'     , action='store_true',           default=False,
                   help='start an instance of the web server.')
parser.add_argument('-p, --web-server-port', dest='web_server_port', action='store'     , type=int, default=8080,
                   help='port that the web server should be running on.')

# Compute Client
parser.add_argument('-n, --num-workers', dest='num_workers', action='store', type=int, default=0,
                   help='start n compute clients.')

# Global commands
parser.add_argument('--start'  , dest='start', action='store_true', default=False,
                   help='start all specifed services.')
parser.add_argument('--stop'   , dest='stop' , action='store_true', default=False,
                   help='stop all specifed services.')
parser.add_argument('--kill'   , dest='kill' , action='store_true', default=False,
                   help='kill all specifed services.')
parser.add_argument('--restart', dest='restart', action='store_true', default=False,
                   help='stop all specifed services and restart them.')

args = parser.parse_args()
print args

def start_compute_server(args, config):
	if config['compute_server'] != None:
		raise Exception("Compute server already running. Stop first.")
	p = subprocess.Popen( ['python', 'fracthComputeServer.py', args])
	config['compute_server'] = p.pid
	return config

def stop_compute_server(args, config):
	pid = config['compute_server']
	config = _stop_pid(pid, 'compute_server', 'fracthComputeServer.py', config)
	return config

def start_web_server(args, config):
	if config['web_server'] != None:
		raise Exception("Web server already running. Stop first.")
	p = subprocess.Popen( ['python', 'fracthWebServer.py', args])
	config['web_server'] = p.pid
	return config

def stop_web_server(args, config):
	pid = config['web_server']
	config = _stop_pid(pid, 'web_server', 'fracthWebServer.py', config)
	return config

def start_compute_client(args, num, config):
	print "Starting " + str(num) + " compute clients"
	for i in xrange(num):
		p = subprocess.Popen( ['python', 'fracthComputeClient.py', args])
		config['workers'] += [p.pid]
	return config

def stop_compute_client(args, num, config):
	print "Stopping " + str(num) + " compute clients"
	workers = config['workers']
	print "Workers " + str(workers)
	workers_len = len(workers)
	split_index = min(num, workers_len)
	workers_to_kill = workers[:split_index]

	print "Killing processes."
	for pid in workers_to_kill:
		config = _stop_pid( pid, 'workers', 'fracthComputeClient.py', config )
	return config

def _stop_pid(pid, prop, fileName, config):
	print 'Killing ' + fileName + ' ' + str(pid)
	if (pid == None):
		print 'Invalid pid: ' + str(pid)
		if type(config[prop]) is list:
			config[prop].remove(pid)
		else:
			config[prop] = None
		return config
		
	ps_output = None
	try:
		ps_output = subprocess.check_output("ps -p " + str(pid), shell=True)
	except subprocess.CalledProcessError, e:
		pass
	
	if fileName == None:
		print 'Invalid file name: ' + fileName
		return config
	if ps_output == None:
		print ' ...not found'
		if type(config[prop]) is list:
			config[prop].remove(pid)
		else:
			config[prop] = None
		return config

	if fileName in ps_output:
		subprocess.call( ['kill', str(pid)] )
		if type(config[prop]) is list:
			config[prop].remove(pid)
		else:
			config[prop] = None
	else:
		print 'Process with PID: ' + str(pid) + ' not invoked with file argument ' + fileName

	return config

def load_config():
	print "Loading configuration"
	
	config = None
	try:
		f = open('config.json', 'r')
		config = json.load(f)
		f.close()
	except IOError, e:
		# If file not found we generate default config
		config = {}
	
	print config
	print "Configuration loaded"
	return config

def save_config(config):
	print "Saving configuration"
	print config
	f = open('config.json', 'w')
	json.dump( config, f )
	f.close()

if __name__ == "__main__":

	config = load_config()

	# TODO: Verify version and config content in general way.
	if (not 'workers' in config):
		config['compute_server'] = None
	if (not 'workers' in config):
		config['web_server'] = None
	if (not 'workers' in config):
		config['workers'] = []

	if (args.compute_server):
		
		# Start compute server
		if (args.start):
			config = start_compute_server("", config)
		
		# Stop compute server
		if (args.stop):
			config = stop_compute_server("", config)

		# Restart compute server
		if (args.restart):
			config = stop_compute_server("", config)
			config = start_compute_server("", config)

	if (args.web_server):

		# Start web server
		if (args.start):
			config = start_web_server("", config)

		# Stop web server
		if (args.stop):
			config = stop_web_server("", config)

		# Restart web server
		if (args.restart):
			config = stop_web_server("", config)
			config = start_web_server("", config)


	if (args.num_workers > 0):
		
		# Starting workers
		if (args.start):
			config = start_compute_client("", args.num_workers, config)

		# Stopping workers	
		if (args.stop):
			config = stop_compute_client("", args.num_workers, config)

		# Restart compute server
		if (args.restart):
			config = stop_compute_client("", args.num_workers, config)
			config = start_compute_client("", args.num_workers, config)
		
	# Save config
	print config
	save_config(config)
