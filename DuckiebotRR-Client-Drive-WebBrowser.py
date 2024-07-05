#Example Drive client in Python
from js import document

from RobotRaconteur.Client import *
import time
import numpy as np
import sys

def drive_func(self):
    print_div('DRIVE')
    global d
    d.async_setWheelsSpeed(0.5,0.5,None)

def stop_func(self):
    print_div('STOP')
    global d
    d.async_setWheelsSpeed(0,0,None)
    
def drive_back_func(self):
    print_div('DRIVE BACK')
    global d
    d.async_setWheelsSpeed(-0.5,-0.5,None)
    
def turn_right_func(self):
    print_div('TURN RIGHT')
    global d
    d.async_setWheelsSpeed(0.2,-0.2,None)

def turn_left_func(self):
    print_div('TURN LEFT')
    global d
    d.async_setWheelsSpeed(-0.2,0.2,None)

async def client_drive():
    # rr+ws : WebSocket connection without encryption
    # url_drive ='rr+ws://192.168.1.128:2356?service=Drive' # ADDED
    # url_drive ='rr+ws://localhost:2356?service=Drive' # ADDED
    url_drive ='rr+ws://192.168.43.241:2356?service=Drive' # ADDED
        
    try:
        #Connect to the service
        global d
        d = await RRN.AsyncConnectService(url_drive,None,None,None,None)

        button1 = document.getElementById("drive_btn")
        button1.addEventListener("click", drive_func)
        
        button2 = document.getElementById("stop_btn")
        button2.addEventListener("click", stop_func)    
        
        button3 = document.getElementById("left_btn")
        button3.addEventListener("click", turn_left_func)
        
        button4 = document.getElementById("right_btn")
        button4.addEventListener("click", turn_right_func) 
        
        button5 = document.getElementById("drive_back_btn")
        button5.addEventListener("click", drive_back_func)
        


    except:
        import traceback
        print_div(traceback.format_exc())
        raise

RR.WebLoop.run(client_drive())
