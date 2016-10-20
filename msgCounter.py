import time
import RPi.GPIO as GPIO

def msgCounter(tot) :
	ones = tot%10				#get the number of ones
	tens = (tot%100-ones)/10	#get the number of tens
	hunds = (tot-tot%100)/100	#get the number of hundreds
	
	#send the LED values so that it is turned off
	GPIO.output(4, GPIO.LOW)
	GPIO.output(17, GPIO.LOW)
	GPIO.output(27, GPIO.LOW)

	#for the number of hundreds
	for digit in range(0, hunds) :
		GPIO.output(4, GPIO.HIGH)		#turn the red component of the LED on
		time.sleep(1)					#delay for one second
		GPIO.output(4, GPIO.LOW)		#turn off the red component of the LED
	
	#for the number of tens
	for digit in range(0, tens) :		
		GPIO.output(17, GPIO.HIGH)		#turn the green component of the LED on
		time.sleep(1)					#delay for one second
		GPIO.output(17, GPIO.LOW)		#turn off the green component of the LED
	
	#for the number of ones
	for digit in range(0, ones) :
		GPIO.output(27, GPIO.HIGH)		#turn the blue component of the LED on
		time.sleep(1)					#delay for one second
		GPIO.output(27, GPIO.LOW)		#turn off the blue component of the LED
	
	
msgCounter(762)