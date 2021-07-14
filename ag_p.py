def setup_coin_acceptor():
 	"""Initialises the coin acceptor parameters and sets up a callback for button pushes
 	and coin inserts.
 	"""
 	print('begin setup_coin_acceptor')
 	# Defining GPIO BCM Mode
 	GPIO.setmode(GPIO.BCM)
 	 
 	# Setup GPIO Pins for coin acceptor, button and button-led
 	GPIO.setwarnings(False)
 	GPIO.setup(13, GPIO.OUT)
 	GPIO.output(13, GPIO.LOW)
 	GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
 	GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
 	 
 	# Setup coin interrupt channel (bouncetime for switch bounce)
 	GPIO.add_event_detect(5, GPIO.RISING, callback=button_event, bouncetime=350)
 	GPIO.add_event_detect(6, GPIO.FALLING, callback=coin_event)


# GPIO.add_event_detect(5, GPIO.RISING, callback=button_event, bouncetime=350)