#!/usr/bin/env python
 
import rospy
from geometry_msgs.msg import Pose

def callback(data):    
    print (str(data))

def listener():

    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber('aruco_pose', Pose, callback)

    rospy.spin()

if __name__ == '__main__':
    listener()
