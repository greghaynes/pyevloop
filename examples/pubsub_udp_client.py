import evloop
import socket

class PubSubClient(evloop.UdpSocketWatcher):
	def __init__(self, host, port):
		evloop.UdpSocketWatcher.__init__(self)
		self.host = host
		self.port = port

		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.setup_socket(s)

		self.send_sub()

	def handle_read(self, socket):
		data, addr = self.socket.recvfrom(4096)
		print 'Got: %s' % data

	def send_sub(self):
		self.sendto('a', (self.host, self.port))
		evloop.EventDispatcher().add_timer(1, self.send_sub)

if __name__=='__main__':
	c = PubSubClient('127.0.0.1', 8080)
	evloop.EventDispatcher().loop_forever()

