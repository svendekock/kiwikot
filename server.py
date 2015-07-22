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

# Variables

delay = 0.0055
steps = 500

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Enable GPIO pins for  ENA and ENB for stepper

enable_a = 18
enable_b = 22

# Enable pins for IN1-4 to control step sequence

coil_A_1_pin = 11
coil_A_2_pin = 13
coil_B_1_pin = 15
coil_B_2_pin = 16

# Set pin states

GPIO.setup(enable_a, GPIO.OUT)
GPIO.setup(enable_b, GPIO.OUT)
GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)

# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(11, GPIO.OUT)
# GPIO.setup(13, GPIO.OUT)
# GPIO.setup(15, GPIO.OUT)


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
		control()

	def on_close(self):
		self.connected = False

	def timeout_loop(self):
		if self.connected:
			print "in timeout looooop"
			tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=1), self.timeout_loop)
	
	def control():
		# Set ENA and ENB to high to enable stepper

		GPIO.output(enable_a, True)
		GPIO.output(enable_b, True)

		# loop through step sequence based on number of steps

		for i in range(0, steps):
			setStep(1,0,1,0)
			time.sleep(delay)
			setStep(0,1,1,0)
			time.sleep(delay)
			setStep(0,1,0,1)
			time.sleep(delay)
			setStep(1,0,0,1)
			time.sleep(delay)

		# Reverse previous step sequence to reverse motor direction

		for i in range(0, steps):
			setStep(1,0,0,1)
			time.sleep(delay)
			setStep(0,1,0,1)
			time.sleep(delay)
			setStep(0,1,1,0)
			time.sleep(delay)
			setStep(1,0,1,0)
			time.sleep(delay)
		
	# Function for step sequence
	def setStep(w1, w2, w3, w4):
		GPIO.output(coil_A_1_pin, w1)
		GPIO.output(coil_A_2_pin, w2)
		GPIO.output(coil_B_1_pin, w3)
		GPIO.output(coil_B_2_pin, w4)

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

