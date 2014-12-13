from multiprocessing.managers import BaseManager
import Queue

#TODO: Add cmdline parser.

class QueueManager(BaseManager):

	def __init__(self, address, authkey):
		super(QueueManager, self).__init__(address, authkey)
		self.job_queue = Queue.Queue()
		self.result_queue = Queue.Queue()
		self.register('get_job_queue'   , self.get_job_queue)
		self.register('get_result_queue', self.get_result_queue)

	def get_job_queue(self):
		print "Job queue fetched"
		return self.job_queue

	def get_result_queue(self):
		print "Result queue fetched"
		return self.result_queue

if __name__ == "__main__":
	m = QueueManager(address=('', 50000), authkey='abracadabra')
	s = m.get_server()
	s.serve_forever()
