import time
import RPi.GPIO as GPIO

def msgCounter(tot) :
	ones = tot%10
	tens = (tot%100-ones)/10
	hunds = (tot-tot%100)/100
	
	GPIO.output(4, GPIO.LOW)
	GPIO.output(17, GPIO.LOW)
	GPIO.output(27, GPIO.LOW)

	
	for digit in range(0, hunds) :
		GPIO.output(4, GPIO.HIGH)
		time.sleep(1)
		GPIO.output(4, GPIO.LOW)
		
	for digit in range(0, tens) :
		GPIO.output(17, GPIO.HIGH)
		time.sleep(1)
		GPIO.output(17, GPIO.LOW)
	
	for digit in range(0, ones) :
		GPIO.output(27, GPIO.HIGH)
		time.sleep(1)
		GPIO.output(27, GPIO.LOW)
	
	
msgCounter(762)