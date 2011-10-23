# Copyright 2011 Gregory Haynes <greg@greghaynes.net>
# Licensed under the MIT license. See LICENSE for more information.

import select
import heapq
import logging
import time
import collections

class TimerQueue(object):
	def __init__(self):
		self._p_queue = []

	def insert(self, delay, handler):
		exec_time = time.time() + delay
		heapq.heappush(self._p_queue, (exec_time, handler))

	def update(self):
		tasks = self.pop_up_to(time.time())
		for t in tasks:
			t[1]()

	def pop_up_to(self, time):
		ret = collections.deque()
		d = self.pop_next_up_to(time)
		while d != None:
			ret.append(d)
			d = self.pop_next_up_to(time)
		return ret

	def pop_next_up_to(self, time):
		try:
			d = heapq.heappop(self._p_queue)
		except IndexError:
			return None
		if d[0] <= time:
			return d
		else:
			try:
				heapq.heappush(self._p_queue, d)
			except IndexError:
				pass
			return None

class EventDispatcher(object):
	'''Singleton wrapper class for poll loop.
	   Take care if subclassing this! Although new will always return the same instance
	   __init__ will be called each time new is used.'''
	_instance = None
	_fd_handlers = {}
	_poll = None
	_timer_q = None
	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._timer_q = TimerQueue()
			cls._poll = select.poll()
			cls._instance = super(EventDispatcher, cls).__new__(
				cls, *args, **kwargs)
		return cls._instance

	def remove_fd(self, fd):
		self._poll.unregister(fd)
		del self._fd_handlers[fd]

	def add_fd(self, fd, eventmask, handler):
		self._poll.register(fd, eventmask)
		self._fd_handlers[fd] = handler

	def modify_fd_events(self, fd, eventmask):
		self._poll.modify(fd, eventmask)

	def add_timer(self, delay_secs, handler):
		self._timer_q.insert(delay_secs, handler)

	def loop_forever(self):
		while True:
			self.loop()

	def loop(self, timeout=10):
		events = self._poll.poll(timeout)
		for event in events:
			try:
				handler = self._fd_handlers[event[0]]
			except KeyError:
				logging.error('No handler found for fd event')
			else:
				handler(*event)
		self._timer_q.update()

class FdWatcher(object):
	'Parent class providing async fd monitoring'
	def __init__(self):
		self.dispatcher = EventDispatcher()

	def __del__(self):
		try:
			self.dispatcher.remove_fd(self._fd)
		except AttributeError, KeyError:
			pass

	def set_poll_flag(self, flag, val):
		if val:
			self._eventmask = self._eventmask | flag
		else:
			self._eventmask = self.eventmask & (~flag)
		self.dispatcher.modify_fd_events(self._fd, self._eventmask)

	def set_readable(self, val=True):
		self.set_poll_flag(select.POLLIN, val)

	def set_writable(self, val=True):
		self.set_poll_flag(select.POLLOUT, val)

	def setup_fd(self, fd, eventmask):
		try:
			'Check if we have an old fd to remove'
			if self._fd != fd:
				self.dispatcher.remove_fd(self._fd)
		except AttributeError:
			pass
		self.dispatcher.add_fd(fd, eventmask, self.event_handler)
		self._fd = fd
		self._eventmask = eventmask

	def event_handler(self, fd, events):
		if events & select.POLLIN:
			self.handle_read(fd)
		if events & select.POLLOUT:
			self.handle_write(fd)

	def handle_read(self, fd):
		pass

	def handle_write(self, fd):
		pass
