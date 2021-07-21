#!/usr/bin/env python3
#Bibliotheken einbinden
import RPi.GPIO as GPIO
import time, sys, datetime
import random
#from neopixel import *
from gpiozero import LED
from time import sleep


#GPIO Modus (BOARD / BCM)
#ansteuern per Boardnr. (1-40) oder über GPIO Nummer
GPIO.setmode(GPIO.BCM)	

#GPIO SETUP
SOUND_PIN = 21 		# PinNr. 15 - GPIO 22
GPIO.setup(SOUND_PIN, GPIO.IN) 
 
#LED PANEL configuration:
red = LED(14)
yellow = LED(15)
green = LED(18)

#setzt led farben
def setColor(color):
    if (color == "red"):
        red.on
        print("red")
        green.off
        yellow.off
    elif (color == "yellow"):
        yellow.on
        print("yellow")
        red.off
        green.off
    elif (color == "green"):
        green.on
        print("green")
        yellow.off
        red.off

    
count = 0 

#damit led nicht doppelt eingeschalten wird
ledcolor = "" 

#damit led nicht doppelt eingeschalten wird
#Fuer den Durchschnittsektor
ledcolor2 = ""    

#grenzen/vergleichswerte, die bestimmen, wann leds rot, gelb oder grün anzeigen
dblevel_min = 0   #0 
dblevel_mid = 8  #13 
dblevel_mid2 = 10 #20 
dblevel_max = 15  #25

#zählt count hoch oder runter, abhängig davon, ob eingang registriert wurde oder nicht
def DETECTED(SOUND_PIN): 
    global count 
    #nowtime = datetime.datetime.now() 
    if GPIO.input(SOUND_PIN): 
        count += 1 
    else: 
        count -= 1 
 
#Debugging 
print ("Sound Module Test (CTRL+C to exit)") 
time.sleep(1) 
print ("Ready  --> RUN") 
 
try: 
    #fügt einen trigger hinzu, der die methode DETECTED ausführt, wenn die spannung von SOUND_PIN steigt oder fällt
    #GPIO.BOTH registriert beides - ein fallen und ein steigen der spannung
    GPIO.add_event_detect(SOUND_PIN, GPIO.BOTH, callback=DETECTED) 
    
    
    middle = [] 
    middlevalue = 0 
    maxvalue = 0 
    minvalue = 0 

    #vermutlich eher debugging
    secoundoutput = 1 
    cyclus = 0 

    #zum tracken der zeit
    sleeptime = 0.005

    #zur berechnung der durchschnittswerte
    averagecyclus = 0  
    averagevalue = 0

    fiveminutes = 0

    #liste die später alle db werte enthält
    average = [] 

    while 1: 
        dB = (count+83.2073)/11.003 
        count = 0 
        position = 50+dB

        #DB Werte werden in eine Liste gepackt
        average.append(dB) 
        #print(dB)

 
        line = "" 
        for x in range(100): 
        #überprüft welchen wert zwischen 0 und 100 die variable position hat
        #setzt den ggf. den minimal und maximalwert
        #befüllt die liste middle mit den db werten um später den durchschnitt berechnen zu können
        #line dient zum debugging
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

        #vermutlich nur zum debugging
        cyclus += sleeptime

        #damit durchschnitt jede minute berechnet werden kann
        averagecyclus += sleeptime
  
        #um alle 5 minuten alte werte zu löschen
        fiveminutes += sleeptime 
    
    
        time.sleep(sleeptime) 
  
        #wird ausgeführt, wenn cyclus größer oder gleich 1 ist
        if cyclus >= secoundoutput: 
            #scheint eher debugging zu sein
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
            #überprüft die lautstärke (maxvalue) und setzt die farbe der leds
            if (maxvalue >= dblevel_mid2 and ledcolor != "red"): 
                ledcolor = "red" 
                setColor("red")
            elif (maxvalue < dblevel_mid2 and maxvalue >= dblevel_mid and ledcolor != "yellow"): 
                ledcolor = "yellow" 
                setColor("yellow")
            elif (maxvalue < dblevel_mid and ledcolor != "green"): 
                ledcolor = "green" 
                setColor("green")

            time.sleep(1) 

            #setzt alle werte wieder zurück
            cyclus = 0 
            middlevalue = 0 
            maxvalue = 0 
            minvalue = 0 
            middle = []

        #Nach jeder Minute startet die Berechnung und Durchfuehrung des Durchschnittwertes
        if averagecyclus >= 5: 

            #Sollte es unter 6 Minuten sein wird dies ausgefuehrt
            if fiveminutes < 30:  
      
                #zähle alle werte in der liste average (db-werte) zusammen
                for x in average:
                    averagevalue += x 
      
                #Berechnung des Durchschnitts
                averagevalue = averagevalue/(len(average)) 

                #Gleichen If-Anweisungen wie bei der aktuellen Lautstaerke
                if (averagevalue >= dblevel_mid2 and ledcolor2 != "red"):  
                    ledcolor2="red"
                    setColor("red")
                elif (averagevalue <dblevel_mid2 and averagevalue >= dblevel_mid and ledcolor2 !="yellow"):
                    ledcolor2="yellow"
                    setColor("yellow")
                elif (averagevalue < dblevel_mid and ledcolor2 != "green"):
                    ledcolor2="green"
                    setColor("green")

                averagecyclus = 0

            #nach 6 minuten wird zähler für gesamtzeit auf 5 minuten zurückgesetzt --> vermeidung von überlauf
            else:  
                fiveminutes = 30
                averagevalue = 0
                averagecyclus = 0

                #Die ersten 12000 Eintraege also die der ersten Minute der aktuellen 6 Minuten wird aus der Liste geloescht
                #12000 * sleeptime = 12000 * 0.005 sek = 60 sek
                for i in range(1000):  
                    average.pop(0)

                #Der Durchschnitt wird erneut berechnet aus den aktuellen 5 Minuten
                for x in average: 
                    averagevalue += x

                averagevalue = averagevalue/(len(average))

                #Gleiche If-Anweisungen wie beim aktuellen Wert
                if (averagevalue >= dblevel_mid2 and ledcolor2 != "red"): 
                    ledcolor2="red"
                    setColor("red")
                elif (averagevalue <dblevel_mid2 and averagevalue >= dblevel_mid and ledcolor2 !="yellow"):
                    ledcolor2="yellow"
                    setColor("yellow")
                elif (averagevalue < dblevel_mid and ledcolor2 != "green"):
                    ledcolor2="green"
                    setColor("green")

 
except KeyboardInterrupt:
    print ("Quit")
    GPIO.cleanup()