#! /usr/bin/python
import os
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from tornado import web, websocket

import datetime
import json

import RPi.GPIO as GPIO
import time

root = os.path.dirname(__file__)
port = 4567

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)


class SocketHandler(websocket.WebSocketHandler):
#	@tornado.web.asynchronous
#	def get(self):
#		try:
#			with open(os.path.join(root, 'index.html'), 'r') as f:
#				self.write(f.read())
#		except IOError as e:
#			self.write("404: Not found")
#		self.finish()
	def open(self):
		self.connected = True
		print "New Connection"
		self.write_message("LED " 
			+ str(GPIO.input(11))
			+ str(GPIO.input(13))
			+ str(GPIO.input(15)))
		#self.timout_loop()

	def on_message(self, message):
		print "Incoming ", message
		self.write_message(message)

	def on_close(self):
		self.connected = False

	def timeout_loop(self):
		if self.connected:
			print "in timeout looooop"
			tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=1), self.timeout_loop)

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")


app = tornado.web.Application([
	(r"/", IndexHandler),
	(r"/ws", SocketHandler),
	(r"/(.*)", web.StaticFileHandler, dict(path=root)),	
])

if __name__ == "__main__":
	GPIO.output(11, False)
	GPIO.output(13, True)
	GPIO.output(15, False)	
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(port)
	print "Server started"
	tornado.ioloop.IOLoop.instance().start()

