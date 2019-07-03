#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Pose
from geometry_msgs.msg import Point
from geometry_msgs.msg import Quaternion

import numpy as np
import cv2
import cv2.aruco as aruco


with np.load('/home/tejas/crazyflie-lib-python/examples/tejas_codes/vision/pose_detection/cam_param_fpv.npz') as X:
	mtx, dist = [X[i] for i in ('mtx','dist')]
cap = cv2.VideoCapture(0)
marker_length = 87 # millimeters
position_data = np.zeros((10000,3))


def talker():
	pub2 = rospy.Publisher('aruco_pose', Pose, queue_size=30)
	rospy.init_node('talker', anonymous=True)
	rate = rospy.Rate(30) # 30hz
	j=0
	while not rospy.is_shutdown():
		ret, frame = cap.read()
		j = j+1
		print (j,"j")
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
		parameters = aruco.DetectorParameters_create()
		parameters.adaptiveThreshConstant = 10
		corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
		font = cv2.FONT_HERSHEY_SIMPLEX

		if np.all(ids != None):
			rvec, tvec ,_ = aruco.estimatePoseSingleMarkers(corners, marker_length, mtx, dist) 
			position_data[j,:] = tvec[0].flatten()

			for i in range(0, ids.size):
				aruco.drawAxis(frame, mtx, dist, rvec[i], tvec[i], 5)

			aruco.drawDetectedMarkers(frame, corners)

			strg = ''
			for i in range(0, ids.size):
				strg += str(ids[i][0])+', '

			cv2.putText(frame, "Id: " + strg, (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)
		
			aruco_pose = Pose()
			aruco_pose.position = Point(x=tvec[0][0][0],y=tvec[0][0][1],z=tvec[0][0][2])
			aruco_pose.orientation = Quaternion(x=1,y=0,z=0,w=0)
			rospy.loginfo(aruco_pose)
			pub2.publish(aruco_pose) 
		else:
			cv2.putText(frame, "No Ids", (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)
		# out.write(frame)
		
		
		# display the resulting frame
		cv2.imshow('frame',frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break  
		

		
		rate.sleep()

if __name__ == '__main__':
	try:
		talker()
	except rospy.ROSInterruptException:
		pass
