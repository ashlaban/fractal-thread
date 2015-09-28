from multiprocessing.managers import BaseManager

import fracthComputeCore   as fcc

class QueueManagerClient(BaseManager):
	pass

class ComputeClient():
	def __init__(self, address, authkey):
		self.manager = QueueManagerClient(address=address, authkey=bytes(authkey, 'utf-8'))
		self.manager.register("get_job_queue")
		self.manager.register("get_result_queue")
		self.manager.connect()
		self.job_queue    = self.manager.get_job_queue()
		self.result_queue = self.manager.get_result_queue()

	def get_job(self):
		return self.job_queue.get()

	def put_job(self, job):
		self.job_queue.put(job)

	def get_result(self):
		return self.result_queue.get()

	def put_result(self, result):
		self.result_queue.put(result)

if __name__ == "__main__":
	print("Starting FRACTH compute client...", end=' ')
	computeClient = ComputeClient( address=('', 50000), authkey='abracadabra' )
	print("\t...done.")

	while (True):
		print("Waiting for job...", end=' ')
		job = computeClient.get_job()
		print("\t...done.")

		print("Rendering...", end=' ')
		result = fcc.render_region( job )
		print("\t...done.")
		
		print("Commit result...", end=' ')
		computeClient.put_result( result )
		print("\t...done.")
		# done = True