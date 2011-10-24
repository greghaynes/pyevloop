import evloop
import socket
import select

class EchoHandler(evloop.TcpSocketWatcher):
	def __init__(self, conn, addr):
		evloop.TcpSocketWatcher.__init__(self)
		self.setup_socket(conn)
		self.set_readable()

	def handle_read(self, fd):
		data = self.socket.recv(1024)
		if not data:
			self.close()
		self.send(data)

class EchoServer(evloop.TcpSocketWatcher):
	def __init__(self, host, port):
		evloop.TcpSocketWatcher.__init__(self)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((host, port))
		s.listen(3)
		self.setup_socket(s)
		self.set_readable()

	def handle_read(self, fd):
		conn, addr = self.socket.accept()
		e = EchoHandler(conn, addr)

if __name__=='__main__':
	s = EchoServer('127.0.0.1', 12345)
	evloop.EventDispatcher().loop_forever()

