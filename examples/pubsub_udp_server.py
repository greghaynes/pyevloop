import evloop
import socket
import time

class Client(object):
	def __init__(self, hostname, port, prefix, sub_time):
		self.hostname = hostname
		self.port = port
		self.prefix = prefix

class PubSubServer(evloop.UdpSocketWatcher):
	'''This is NOT an efficient implementation.
	   If using this in production code please make use of a radix tree
	   for prefix subscription searching.'''
	def __init__(self, host, port):
		evloop.UdpSocketWatcher.__init__(self)
		self.client_timeout = 1.0
		self.clients = {}

		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.bind((host, port))
		self.setup_socket(s)

		self.check_client_timeout()

	def handle_read(self, socket):
		data, addr = self.socket.read(4096)
		cur_time = time.time()
		try:
			self.clients[addr].prefix = data
			self.clients[addr].sub_time = cur_time
		except KeyError:
			self.clients[addr] = Client(addr[0], addr[1], data, cur_time)

	def check_client_timeout(self):
		cur_time = time.time()
		for key in self.clients.keys():
			c = self.clients[key]
			if cur_time >= c.sub_time + self.client_timeout:
				del self.clients[key]

		# reinsert timer
		evloop.EventDispatcher().add_timer(1, self.check_client_timeout)

	def publish(self, msg):
		for client in self.clients.vals():
			if msg.startswith(client.prefix):
				self.sendto(msg, (client.host, client.port))

if __name__=='__main__':
	server = PubSubServer('127.0.0.1', 8080)
	evloop.EventDispatcher().loop_forever()

