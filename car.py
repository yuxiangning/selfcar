import RPi.GPIO as GPIO
import time
import cv2
import sys
import curses
from picamera.array import PiRGBArray
from picamera import PiCamera

class Car:
	def __init__(self):
		p_pin = 14
		d_pin = 18
		steer_pin = 12

		self.throttle = 10	# 0 to 100, the higher the faster
		self.max_throttle = 40	# not too fast
		self.steer_angle = 70
		self.max_steer = 100
		self.min_steer = 50

		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(p_pin, GPIO.OUT)
		GPIO.setup(d_pin, GPIO.OUT)
		GPIO.setup(steer_pin, GPIO.OUT)

		# we don't support reverse gear yet :)
		GPIO.output(p_pin, GPIO.HIGH)
		self.d_pwm = GPIO.PWM(d_pin, 50)
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

	def Run(self):
		fps = 30
		self.BeginKeyBoardInput()
		camera = PiCamera()
		camera.resolution = (320, 240)
		camera.framerate =32 
		rawCapture = PiRGBArray(camera, size = (320, 240))
		seq = 0
		begin = time.time()
		fd = open('./data/steer.csv', 'a')

		for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
			if self.HandleKeyBoardIntput() == False:
				break

			image = frame.array
			name = str(seq).zfill(5)
			imgpath = './data/' + name + '.png'
			cv2.imwrite(imgpath, image)
			rec = name + ',' + str(self.steer_angle) + '\n'
			fd.write(rec)

			rawCapture.truncate(0)
			end = time.time()
			delay = 1.0 / fps - (end - begin)
			if delay > 0.0:
				time.sleep(delay)	
			seq += 1

		fd.close()

	def Halt(self):
		self.s_pwm.stop()
		self.d_pwm.stop()
		GPIO.cleanup()

		self.EndKeyBoardInput()


try:
	c = Car()
	c.Run()
finally:
	c.Halt()
