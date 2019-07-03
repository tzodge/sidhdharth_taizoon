#!/usr/bin/env python

import rospy

import roslib
roslib.load_manifest('tf')
import tf
from geometry_msgs.msg import Pose
from geometry_msgs.msg import Point
from geometry_msgs.msg import Quaternion
import transforms3d as tf3d

import numpy as np
import cv2
import cv2.aruco as aruco
from geometry_msgs.msg import Vector3


with np.load('/home/tejas/crazyflie-lib-python/examples/tejas_codes/vision/pose_detection/cam_param_fpv.npz') as X:
	mtx, dist = [X[i] for i in ('mtx','dist')]
cap = cv2.VideoCapture(0)
marker_length = 87 # millimeters
position_data = np.zeros((10000,3))


def convert_rodrigues(x):
	rot,_ = cv2.Rodrigues(x[0:3])
	quat = tf3d.quaternions.mat2quat(rot[0:3,0:3])
	eul = tf3d.euler.mat2euler(rot[0:3,0:3])
	return eul 


def talker():
	# pub1 = rospy.Publisher('chatter', String, queue_size=10)
	pub2 = rospy.Publisher('aruco_pose', Vector3, queue_size=30)
	br = tf.TransformBroadcaster()

		  

	## reference https://matthew-brett.github.io/transforms3d/reference/transforms3d.euler.html#transforms3d.euler.mat2euler


	rospy.init_node('talker1', anonymous=True)
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

		# check if the ids list is not empty
		# if no check is added the code will crash
		if np.all(ids != None):

			# estimate pose of each marker and return the values
			# rvet and tvec-different from camera coefficients 
			rvec, tvec ,_ = aruco.estimatePoseSingleMarkers(corners, marker_length, mtx, dist) 
			# print (tvec.flatten(),"tvec")
			position_data[j,:] = tvec[0].flatten()
			#(rvec-tvec).any() # get rid of that nasty numpy value array error

			for i in range(0, ids.size):
				# draw axis for the aruco markers
				aruco.drawAxis(frame, mtx, dist, rvec[i], tvec[i], 5)

			# draw a square around the markers
			aruco.drawDetectedMarkers(frame, corners)


			# code to show ids of the marker found
			strg = ''
			for i in range(0, ids.size):
				strg += str(ids[i][0])+', '

			cv2.putText(frame, "Id: " + strg, (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)
			a = np.array([1,2,3])
			rvec = a/np.linalg.norm(a) 
			eul = convert_rodrigues (rvec)
			aruco_pose = Vector3()
			#aruco_pose.position = Point(x=tvec[0][0][0],y=tvec[0][0][1],z=tvec[0][0][2])
			#aruco_pose.orientation = Quaternion(x=1,y=0,z=0,w=0)
			#rospy.loginfo(aruco_pose)
			aruco_pose.x= tvec[0][0][0]
			aruco_pose.y= tvec[0][0][1]
			aruco_pose.z= tvec[0][0][2]
			pub2.publish(aruco_pose) 
			#br.sendTransform((tvec[0][0][0],tvec[0][0][1],tvec[0][0][2]),
			#tf.transformations.quaternion_from_euler(0, 0, 0),
			#rospy.Time.now(),
			#camera,
			#"world")
			br.sendTransform((tvec[0][0][0],tvec[0][0][1],tvec[0][0][2]),
			tf.transformations.quaternion_from_euler(*eul),
			rospy.Time.now(),
			camera, "world")
		else:
			# code to show 'No Ids' when no markers are found
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
