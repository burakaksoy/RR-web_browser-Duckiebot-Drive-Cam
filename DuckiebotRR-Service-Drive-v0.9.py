#Duckibot Driver Robot Raconteur service in Python

import time
import RobotRaconteur as RR
#Convenience shorthand to the default node.
#RRN is equivalent to RR.RobotRaconteurNode.s
RRN=RR.RobotRaconteurNode.s
import threading
import traceback
import sys
import argparse
# Import these to control motor hats
from Adafruit_MotorHAT import Adafruit_MotorHAT
from math import fabs, floor

#The service definition of this service.
# Note; Change it with Simplifiedd.py later
drive_servicedef="""
#Service to provide sample interface to the Duckiebot Drive
service experimental.duckiebot

option version 0.5

object Drive
    option constant int16 LEFT_MOTOR_MIN_PWM = 60
    option constant int16 LEFT_MOTOR_MAX_PWM = 255
    option constant int16 RIGHT_MOTOR_MIN_PWM = 60
    option constant int16 RIGHT_MOTOR_MAX_PWM = 255
    option constant double SPEED_TOLERANCE = 1.e-2

    function void setWheelsSpeed(double v_left, double v_right)

end object
"""

#-----------------------------------------------------------------
class DaguWheelsDriver:
    LEFT_MOTOR_MIN_PWM = 60        # Minimum speed for left motor  
    LEFT_MOTOR_MAX_PWM = 255       # Maximum speed for left motor  
    RIGHT_MOTOR_MIN_PWM = 60       # Minimum speed for right motor  
    RIGHT_MOTOR_MAX_PWM = 255      # Maximum speed for right motor  
    SPEED_TOLERANCE = 1.e-2       # speed tolerance level

    def __init__(self, verbose=False, debug=False, left_flip=False, right_flip=False):
        self.motorhat = Adafruit_MotorHAT(addr=0x60)
        self.leftMotor = self.motorhat.getMotor(1)
        self.rightMotor = self.motorhat.getMotor(2)
        self.verbose = verbose or debug
        self.debug = debug

        self._lock=threading.RLock()
        self._streaming=False
        self._ep=0
        # Set directions based on flip property
        self.left_sgn = 1.0
        if left_flip:
            self.left_sgn = -1.0
        self.right_sgn = 1.0
        if right_flip:
            self.right_sgn = -1.0
        # Set initial speeds to zero
        self.leftSpeed = 0.0
        self.rightSpeed = 0.0
        self.updatePWM()

    def PWMvalue(self, v, minPWM, maxPWM):
        pwm = 0
        if fabs(v) > self.SPEED_TOLERANCE:
            pwm = int(floor(fabs(v) * (maxPWM - minPWM) + minPWM))
        return min(pwm, maxPWM)

    def updatePWM(self):
        vl = self.leftSpeed*self.left_sgn
        vr = self.rightSpeed*self.right_sgn

        pwml = self.PWMvalue(vl, self.LEFT_MOTOR_MIN_PWM, self.LEFT_MOTOR_MAX_PWM)
        pwmr = self.PWMvalue(vr, self.RIGHT_MOTOR_MIN_PWM, self.RIGHT_MOTOR_MAX_PWM)

        if self.debug:
            print ("v = %5.3f, u = %5.3f, vl = %5.3f, vr = %5.3f, pwml = %3d, pwmr = %3d" % (v, u, vl, vr, pwml, pwmr))

        if fabs(vl) < self.SPEED_TOLERANCE:
            leftMotorMode = Adafruit_MotorHAT.RELEASE
        elif vl > 0:
            leftMotorMode = Adafruit_MotorHAT.FORWARD
        elif vl < 0: 
            leftMotorMode = Adafruit_MotorHAT.BACKWARD

        if fabs(vr) < self.SPEED_TOLERANCE:
            rightMotorMode = Adafruit_MotorHAT.RELEASE
            pwmr = 0
        elif vr > 0:
            rightMotorMode = Adafruit_MotorHAT.FORWARD
        elif vr < 0: 
            rightMotorMode = Adafruit_MotorHAT.BACKWARD

        self.leftMotor.setSpeed(pwml)
        self.leftMotor.run(leftMotorMode)
        self.rightMotor.setSpeed(pwmr)
        self.rightMotor.run(rightMotorMode)

    def setWheelsSpeed(self, left, right):
        with self._lock:
            self.leftSpeed = left
            self.rightSpeed = right
            self.updatePWM()

    # Stop the streaming thread
    def StopStreaming(self):
        if (not self._streaming):
            raise Exception("Not streaming")
        self._streaming=False

    def Shutdown(self):
        with self._lock:
            self.leftMotor.run(Adafruit_MotorHAT.RELEASE)
            self.rightMotor.run(Adafruit_MotorHAT.RELEASE)
            del self.motorhat

#-----------------------------------------------------------------
## Put Simplifiedd.py here later

#------------------------------------------------------------------------------
def main():
    #Accept the names of the webcams and the nodename from command line            
    parser = argparse.ArgumentParser(description="Example Robot Raconteur Duckiebot Drive service")
    parser.add_argument("--nodename",type=str,default="experimental.duckiebot.Drive",help="The NodeName to use")
    parser.add_argument("--tcp-port",type=int,default=2356,help="The listen TCP port") #random port, any unused port is fine
    parser.add_argument("--wait-signal",action='store_const',const=True,default=False)
    args = parser.parse_args()
    
    #Initialize the object in the service
    obj=DaguWheelsDriver()

    with RR.ServerNodeSetup(args.nodename,args.tcp_port) as node_setup:

        RRN.RegisterServiceTypeFromFile("experimental.duckiebot") # This is the .robdef file
        RRN.RegisterService("Drive","experimental.duckiebot.Drive",obj)
    
        # These are for using the service on Web Browsers
        node_setup.tcp_transport.AddWebSocketAllowedOrigin("http://localhost")
        node_setup.tcp_transport.AddWebSocketAllowedOrigin("http://localhost:8000")
        node_setup.tcp_transport.AddWebSocketAllowedOrigin("https://johnwason.github.io")
        
        if args.wait_signal:  
            #Wait for shutdown signal if running in service mode          
            print("Press Ctrl-C to quit...")
            import signal
            signal.sigwait([signal.SIGTERM,signal.SIGINT])
        else:
            #Wait for the user to shutdown the service
            if (sys.version_info > (3, 0)):
                input("Server started, press enter to quit...")
            else:
                raw_input("Server started, press enter to quit...")
    
        #Shutdown
        obj.Shutdown()

if __name__ == '__main__':
    main()
