import thread
import BlynkLib
import time
import os
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(27, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
BLYNK_AUTH = '5bd3512dcaee4898870541225fadaffc'
clayMac = '78:4f:43:15:aa:c3'
lockGPIO = 27
unlockGPIO = 17
unlockTime = 10
unlockDoor = 0
lockDoor = 0
retValue = 0
retFlag = 1
c = 1

clayAway = False
found = False
matchers = []

# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# Toggle, Clay's Away
@blynk.VIRTUAL_WRITE(6)
def my_write_handler(value):        
    if value == '1':
        if matchers.count(clayMac) < 1:
            matchers.append(clayMac)            
    if value == '0':
        if matchers.count(clayMac) > 0:
            matchers.remove(clayMac)
            

# On Press, Unlock the Door
@blynk.VIRTUAL_WRITE(4)
def my_write_handler(value):
    global unlockDoor
    unlockDoor = value

# On Press, Lock the Door
@blynk.VIRTUAL_WRITE(3)
def my_write_handler(value):
    global lockDoor
    lockDoor = value
    
# This will run in a different thread to arp-scan LAN network
def my_mac_finder(c):
    global retvalue
    global retFlag
    global matchers
    global matching
    print('running arp-scan')
    retvalue = os.popen("sudo arp-scan --interface=wlan0 --localnet").readlines()
    retFlag = 1
    matching = [s for s in retvalue if any(xs in s for xs in matchers)]
    if len(matching):
        my_location_unlocker()
        
    
def my_location_unlocker():
    global unlockTime
    global matchers
    matchers.remove(clayMac)
    blynk.virtual_write(6, 0)    
    unlock_door()
    time.sleep(unlockTime)
    lock_door()

    
def unlock_door():
    GPIO.output(unlockGPIO, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(unlockGPIO, GPIO.LOW)
    time.sleep(1)    
    print('unlocked')
    blynk.virtual_write(4, 0)
    
def lock_door():
    GPIO.output(lockGPIO, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(lockGPIO, GPIO.LOW)
    time.sleep(1)
    print('locked')
    blynk.virtual_write(3, 0)
    
def my_user_task():
    blynk.sync_all()
    global unlockDoor
    global lockDoor
    global retFlag
    global c
    print 'loop',c
    c = c+1
	
	if GPIO.input(22) == '1':
		#DO FACIAL RECOGNITION
		#SEND PICTURE TO USER
		
    
    if unlockDoor == '1':
        unlock_door()

    if lockDoor == '1':
        lock_door()

    #Global retvalue
    if retFlag == 1:
        retFlag = 0
        thread.start_new_thread(my_mac_finder, (c,))

blynk.set_user_task(my_user_task, 1000)

# Start Blynk (this call should never return)
blynk.run()