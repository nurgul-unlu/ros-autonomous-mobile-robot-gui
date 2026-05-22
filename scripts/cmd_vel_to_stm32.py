#!/usr/bin/env python3
import rospy
import serial
from geometry_msgs.msg import Twist

class ArduinoBridge:
    def __init__(self):
        port = rospy.get_param("~port", "/dev/ttYUSB0")
        baud = rospy.get_param("~baud", 115200)
        topic = rospy.get_param("~topic", "/cmd_vel")

        self.ser = serial.Serial(port, baud, timeout=1)
        rospy.sleep(2.0)

        rospy.Subscriber(topic, Twist, self.callback)
        rospy.on_shutdown(self.shutdown_hook)

        rospy.loginfo(f"Arduino bridge aktif | topic={topic} | port={port}")

    def callback(self, msg):
        v = msg.linear.x
        w = msg.angular.z
        cmd = f"V,{v:.3f},{w:.3f}\n"
        self.ser.write(cmd.encode("utf-8"))

    def shutdown_hook(self):
        try:
            self.ser.write(b"S\n")
            self.ser.close()
        except:
            pass

if __name__ == "__main__":
    rospy.init_node("arduino_bridge")
    ArduinoBridge()
    rospy.spin()
