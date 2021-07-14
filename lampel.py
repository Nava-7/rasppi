#!/usr/bin/env python3
#Bibliotheken einbinden
import RPi.GPIO as GPIO
import time, sys, datetime

#GPIO Modus (BOARD / BCM)
#ansteuern per Boardnr. (1-40) oder über GPIO Nummer
GPIO.setmode(GPIO.BCM)	



from neopixel import *
import random
from gpiozero import LED
from time import sleep

#GPIO SETUP
SOUND_PIN = 22 		# PinNr. 15 - GPIO 22
GPIO.setup(SOUND_PIN, GPIO.IN) 
 
# LED PANEL configuration:
red = LED(14)
yellow = LED(15)
green = LED(18)
LED_COUNT      = 128      	# Number of LED pixels. 
LED_PIN        = 18       	# GPIO pin connected to the pixels (18 uses PWM!)
#LED_PIN       = 10      	# GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0)
LED_FREQ_HZ    = 800000   	# LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10    		# DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 5		# Set to 0 for darkest and 255 for brightest
LED_INVERT     = False    	# True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0        	# set to '1' for GPIOs 13, 19, 41, 45 or 53



# Define functions which animate LEDs in various ways. 
def colorWipe(strip, color, wait_ms=1):
  """Wipe color across display a pixel at a time."""
  for j in range(2):
    for i in range(40):
      strip.setPixelColor(i+(j*64) , color)
  #time.sleep(wait_ms/1000.0) 
  strip.show() 
 
# Create NeoPixel object with appropriate configuration. 
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL) 
# Intialize the library (must be called once before other functions). 

 
strip.begin() 

def colorWipeSeperator(strip, color):    #Die Funktion definiert um einen Seperator auf die LED Panels zu projizieren damit besser unterschieden werden kann
  for j in range(2):
    for i in range(40,48):
      strip.setPixelColor(i+(j*64) , color)

colorWipeSeperator(strip,Color(255,255,255)) #Der Seperator sollte zuerst Weiss sein, kann aber jederzeit hier geaendert werden
 
def colorWipeAverage(strip, color):   # Die Funktion definiert um die Durchschnittslautstaerke auf die LED Panels zu projizieren
  for j in range(2):
    for i in range(48,64):
      strip.setPixelColor(i+(j*64), color)
  strip.show()

count = 0 
ledcolor = "" 
dblevel_min = 0   #0 
dblevel_mid = 16  #13 
dblevel_mid2 = 23 #20 
dblevel_max = 28  #25
ledcolor2=""    #Fuer den Durchschnittsektor

 
def DETECTED(SOUND_PIN): 
 global count 
 #nowtime = datetime.datetime.now() 
 if GPIO.input(SOUND_PIN): 
  count += 1 
 else: 
  count -= 1 
 
 
print ("Sound Module Test (CTRL+C to exit)") 
time.sleep(1) 
print ("Ready  --> RUN") 
 
try: 
    GPIO.add_event_detect(SOUND_PIN, GPIO.BOTH, callback=DETECTED) 
    middle = [] 
    middlevalue = 0 
    maxvalue = 0 
    minvalue = 0 
    secoundoutput = 1 
    cyclus = 0 
    sleeptime = 0.005
    averagecyclus = 0  # Die Variablen die ich fuer die Berechnung des Durchschnittwertes benoetige
    averagevalue = 0
    fiveminutes = 0
    average = [] 
  
 while 1: 
  dB = (count+83.2073)/11.003 
  count = 0 
  position = 50+dB
  average.append(dB) # Die einzelnen DB Werte werden in eine Liste gepackt
  #print(dB)

 
  line = "" 
  for x in range(100): 
   if x == int(round(position)): 
    line += "*" 
    middle.append(dB) 
    if dB > maxvalue: 
     maxvalue = dB 
    if dB < minvalue: 
     minvalue = dB 
   if x == 50: 
    line += "|" 
   line += " " 
  #print line 
  #print "DB: "+str(dB) 
  cyclus += sleeptime
  averagecyclus += sleeptime #Die Zeit wird mitgezaehlt um nach 6 Minuten die erste wieder zu loeschen
  fiveminutes += sleeptime 
    
    
  time.sleep(sleeptime) 
    
  if cyclus >= secoundoutput: 
   for x in middle: 
    middlevalue += x
   #print len(middle) 
   #print "middle is: "+str((middlevalue/len(middle))) 
   #print "max is: "+str(maxvalue) 
   #print "min is: "+str(minvalue)  
   #test 
   maxvalue = maxvalue+(-1*minvalue) 
   # 
   #print "min-max-sum is: "+str(maxvalue+(-1*minvalue)) 
    
    
   #LED COLOR  
   if (maxvalue >= dblevel_mid2 and ledcolor != "red"): 
    ledcolor = "red" 
    colorWipe(strip, Color(0, 255, 0))  # Red wipe 
   elif (maxvalue < dblevel_mid2 and maxvalue >= dblevel_mid and ledcolor != "yellow"): 
    ledcolor = "yellow" 
    colorWipe(strip, Color(255, 255, 0))  # Yellow wipe 
   elif (maxvalue < dblevel_mid and ledcolor != "green"): 
    ledcolor = "green" 
    colorWipe(strip, Color(255, 0, 0))  # Green wipe 
   # 
   time.sleep(1) 
   cyclus = 0 
   middlevalue = 0 
   maxvalue = 0 
   minvalue = 0 
   middle = []
  if averagecyclus >= 60: #Nach einer jeden Minute startet die Berechnung und Durchfuehrung des Durchschnittwertes
    if fiveminutes < 359:  #Sollte es unter 6 Minuten sein wird dies ausgefuehrt
      for x in average:
        averagevalue += x
      averagevalue = averagevalue/(len(average)) #Berechnung des Durchschnitts
      if (averagevalue >= dblevel_mid2 and ledcolor2 != "red"):  #Gleichen If-Anweisungen wie bei der aktuellen Lautstaerke
        ledcolor2="red"
        colorWipeAverage(strip, Color(0,255,0))
      elif (averagevalue <dblevel_mid2 and averagevalue >= dblevel_mid and ledcolor2 !="yellow"):
        ledcolor2="yellow"
        colorWipeAverage(strip, Color(255,255,0))
      elif (averagevalue < dblevel_mid and ledcolor2 != "green"):
        ledcolor2="green"
        colorWipeAverage(strip, Color(255,0,0))
      averagecyclus = 0
    else:  #Sollten 6 Minuten erreicht werden wird der Zaehler der die Gesamtzeit zaehlt wieder auf 5 Minuten zurueckgesetzt um keinen Ueberlauf zu schaffen
      fiveminutes = 300
      averagevalue = 0
      averagecyclus = 0
      for i in range(12000):  #Die ersten 12000 Eintraege also die der ersten Minute der aktuellen 6 Minuten wird aus der Liste geloescht
        average.pop(0)
      for x in average: #Der Durchschnitt wird erneut berechnet aus den aktuellen 5 Minuten
        averagevalue += x
      averagevalue = averagevalue/(len(average))
      if (averagevalue >= dblevel_mid2 and ledcolor2 != "red"): #Gleiche If-Anweisungen wie beim aktuellen Wert
        ledcolor2="red"
        colorWipeAverage(strip, Color(0,255,0))
      elif (averagevalue <dblevel_mid2 and averagevalue >= dblevel_mid and ledcolor2 !="yellow"):
        ledcolor2="yellow"
        colorWipeAverage(strip, Color(255,255,0))
      elif (averagevalue < dblevel_mid and ledcolor2 != "green"):
        ledcolor2="green"
        colorWipeAverage(strip, Color(255,0,0))

 
except KeyboardInterrupt:
    print ("Quit")
    GPIO.cleanup()