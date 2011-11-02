import evloop
import socket

class PubSubClient(evloop.UdpSocketWatcher):
	def __init__(self, host, port):
		evloop.UdpSocketWatcher.__init__(self)

		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.setup_socket(s)
		self.sendto('a', (host, port))

	def handle_read(self, socket):
		data, addr = self.socket.recvfrom(4096)
		print 'Got: %s' % data

if __name__=='__main__':
	c = PubSubClient('127.0.0.1', 8080)
	evloop.EventDispatcher().loop_forever()

