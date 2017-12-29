import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
import sys
import curses
from picamera.array import PiRGBArray
from picamera import PiCamera

# begin with a simple softmax linear mode
class Model:
	def __init__(self, w_dim, b_dim):
		# self.W = np.ndarray(shape=[1, w_dim], dtype=float)
		# self.b = np.ndarray(shape=[b_dim, 1], dtype=float)
		self.W = np.matrix([[1,2,3,4]])
		self.b = np.matrix([[5,5,5,5,5]])
		self.b = self.b.reshape(5,1)

	def Calculate(self, x):
		y = np.add(np.dot(self.W, x), self.b)
		print(y)

class Car:
	def __init__(self):
		motor_p_pin = 14
		motor_d_pin = 18
		steer_pin = 12

		self.throttle = 10	# 0 to 100, the higher the faster
		self.max_throttle = 40	# not too fast
		self.steer_angle = 70
		self.max_steer = 100
		self.min_steer = 50

		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(motor_p_pin, GPIO.OUT)
		GPIO.setup(motor_d_pin, GPIO.OUT)
		GPIO.setup(steer_pin, GPIO.OUT)

		# we don't support reverse gear yet :)
		GPIO.output(motor_p_pin, GPIO.HIGH)
		self.d_pwm = GPIO.PWM(motor_d_pin, 50)
		self.s_pwm = GPIO.PWM(steer_pin, 50)

		self.s_pwm.start(6.67)
		self.d_pwm.start(100 - self.throttle)

	def UpdateSteer(self, delta):
		self.steer_angle += delta
		if self.steer_angle >= self.max_steer:
			self.steer_angle = self.max_steer
		if self.steer_angle <= self.min_steer:
			self.steer_angle = self.min_steer

		dc = self.steer_angle / 18.0 + 2.5	# experiment data
		self.s_pwm.ChangeDutyCycle(dc)

	def UpdateThrottle(self, delta):
		self.throttle += delta 
		if self.throttle >= self.max_throttle:
			self.throttle = self.max_throttle
		if self.throttle <= 0:
			self.throttle = 0
		self.d_pwm.ChangeDutyCycle(100 - self.throttle)

	def BeginKeyBoardInput(self):
		self.stdscr = curses.initscr()
		self.stdscr.nodelay(1)
		self.stdscr.keypad(1)
		curses.noecho()
		curses.cbreak()

	def EndKeyBoardInput(self):
		self.stdscr.nodelay(0)
		curses.nocbreak();
		curses.echo()
		self.stdscr.keypad(0)
		curses.endwin()

	def HandleKeyBoardIntput(self):
		k = self.stdscr.getch()
		if k == ord('q'):
			return False

		if k== ord('a'):
			# left
			self.UpdateSteer(-5)
		elif k == ord('d'):
			# right
			self.UpdateSteer(5)
		elif k == ord('w'):
			# accel	
			self.UpdateThrottle(5)
		elif k == ord('s'):
			# de-accel
			self.UpdateThrottle(-5)
		return True

	def Run(self, recording, use_keyboard):
		# capture dimention
		fps = 30
		width = 160
		height = 128
		if use_keyboard == True:
			self.BeginKeyBoardInput()
		camera = PiCamera()
		camera.resolution = (width, height)
		camera.framerate = fps
		rawCapture = PiRGBArray(camera, size = (width, height))
		seq = 0
		begin = time.time()
		if recording == True:
			fd = open('./data/steer.csv', 'a')

		for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
			if use_keyboard and self.HandleKeyBoardIntput() == False:
				break

			str = "CAPTURE: {} STEER: {} THROTTLE: {} FPS: {}".format(seq, self.steer_angle, self.throttle, fps)
			self.stdscr.addstr(0, 0, str, curses.A_REVERSE)
			self.stdscr.refresh()

			image = frame.array
			if recording == True:
				name = str(seq).zfill(5)
				imgpath = './data/' + name + '.png'
				cv2.imwrite(imgpath, image)
				rec = name + ',' + str(self.steer_angle) + '\n'
				fd.write(rec)

			# XXX how to leverage four cores on raspberry pi???
			image = self.PreProcess(image, width, height)
			rawCapture.truncate(0)

			seq += 1
			if not (seq % 100):
				end = time.time()
				fps = seq/(end - begin)

		if recording:
			fd.close()

	def Halt(self):
		self.s_pwm.stop()
		self.d_pwm.stop()
		GPIO.cleanup()

		if use_keyboard:
			self.EndKeyBoardInput()

	def TopView(self, img, width, height):
		indent = 20
		level = 50
		pt1 = np.float32([[indent, level], [width - indent, level], [0, height], [width, height]])
		pt2 = np.float32([[0, 0],[width, 0], [0, height],[width, height]])

		M = cv2.getPerspectiveTransform(pt1, pt2)
		return cv2.warpPerspective(img, M, (width, height))

	def PreProcess(self, img, width, height):
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		th, img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
		img = self.TopView(img, width, height)
		img = cv2.resize(img, (40, 32))
		return img

# global params
use_keyboard = True
recording = False
try:
	c = Car()
	c.Run(recording, use_keyboard)
finally:
	c.Halt()
