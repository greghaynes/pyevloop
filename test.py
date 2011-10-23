import evloop
import time

def print_time():
	print time.time()

if __name__=='__main__':
	print 'Testing timers.'
	print 'You should see the time printed once per second for 10 seconds.'
	print ''

	dispatcher = evloop.EventDispatcher()
	for delay in range(10):
		dispatcher.add_timer(delay, print_time)
	while True:
		dispatcher.loop_forever()
