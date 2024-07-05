from js import print_div
from js import document
from js import ImageData
#Simple example Robot Raconteur webcam client for web browsers
from RobotRaconteur.Client import *
import time
import numpy as np
import sys


def show_image(image):
    global canvas, ctx
    #Convert the packet to an image and set the global variable
    
    if (canvas == None):
        canvas = document.getElementById("image")
        ctx = canvas.getContext("2d")
    
    imageBytes=np.zeros(4*image.width*image.height, dtype=np.uint8)        #dtype essential here, IndexSizeError
    imageBytes[3::4] = 255
    imageBytes[0::4] = image.data[2::3]
    imageBytes[1::4] = image.data[1::3]
    imageBytes[2::4] = image.data[0::3]

    image_data=ImageData.new(bytes(imageBytes),image.width,image.height)
    ctx.putImageData(image_data, 0, 0,0,0,320,240)

async def client_webcam():
    # rr+ws : WebSocket connection without encryption
    # url ='rr+ws://localhost:2355?service=Webcam'
    # url ='rr+ws://192.168.1.128:2355?service=Webcam'
    url ='rr+ws://192.168.43.241:2355?service=Webcam'
    
    try:
        c_host = await RRN.AsyncConnectService(url,None,None,None,None)
        c1 = await c_host.async_get_Webcams(0,None)

        global canvas, ctx
        canvas = document.getElementById("image")
        ctx = canvas.getContext("2d")
        print_div("Running!")

        finish_time = 0
        while True:
            start_time = time.time()
            #Pull a frame from each camera, c1 and c2
            frame1= await c1.async_CaptureFrame(None)
            
            if (not frame1 is None):               
                #Show the images
                show_image(frame1)
                
                finish_time = time.time()
                # Print the passed time to capture and showing a frame
                # print_div(str(1/(finish_time - start_time + 0.00000001)), ' FPS') 

            # await RRN.AsyncSleep(0.01,None)

    except:
        import traceback
        print_div(traceback.format_exc())
        raise
    
RR.WebLoop.run(client_webcam())

