#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32

class VelocityScaler:
    def __init__(self):
        self.scale = rospy.get_param("~scale_default", 1.0)
        self.max_scale = rospy.get_param("~max_scale", 1.5)
        self.min_scale = rospy.get_param("~min_scale", 0.2)

        # move_base'in ham çıktısı burada olmalı:
        rospy.Subscriber("/cmd_vel_nav_raw", Twist, self.cb_cmd)
        rospy.Subscriber("/speed_scale", Float32, self.cb_scale)

        # ölçeklenmiş çıktı:
        self.pub = rospy.Publisher("/cmd_vel_nav", Twist, queue_size=10)

    def cb_scale(self, msg):
        s = float(msg.data)
        self.scale = max(self.min_scale, min(self.max_scale, s))

    def cb_cmd(self, msg):
        out = Twist()
        out.linear.x  = msg.linear.x  * self.scale
        out.linear.y  = msg.linear.y  * self.scale
        out.linear.z  = msg.linear.z  * self.scale
        out.angular.x = msg.angular.x * self.scale
        out.angular.y = msg.angular.y * self.scale
        out.angular.z = msg.angular.z * self.scale
        self.pub.publish(out)

if __name__ == "__main__":
    rospy.init_node("velocity_scaler")
    VelocityScaler()
    rospy.spin()