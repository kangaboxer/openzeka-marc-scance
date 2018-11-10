#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2              # opencv kütüphanesi
import numpy as np
import os
import time
import signal

import rospkg
import sys
import rospy
from std_msgs.msg import Float64
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge, CvBridgeError
from ackermann_msgs.msg import AckermannDriveStamped

bridge = CvBridge()
rospy.init_node('collect_data')



class seyir_logger:
        def __init__(self):

            rospack = rospkg.RosPack()
            self.package_path = rospack.get_path('deep_learning')
            if not os.path.exists(self.package_path + '/data/'):
                os.makedirs(self.package_path + '/data/')
            path = self.package_path + '/data/'
            i = 1
            while True:
                dname = path+'%03d'%i
                if os.path.exists(dname):
                    i += 1
                else:
                    os.makedirs(dname)
                    break

            self.path = dname+'/'
            self.index = 0
            self.speed = None
            self.angle = None
            self.cv2_img = None
            self.zed_camera = rospy.Subscriber('/zed/left/image_rect_color/compressed', CompressedImage, self.zed_callback)
            self.sub = rospy.Subscriber('/ackermann_cmd', AckermannDriveStamped, self.drive_call, queue_size=1)
            self.rate = rospy.Rate(20)
            self.debug = False
        
        def drive_call(self, data):
            if self.debug:
                rospy.loginfo(data)
            self.angle = data.drive.steering_angle
            self.speed = data.drive.speed
        
        def zed_callback(self,data):
            try:
                np_arr = np.fromstring(data.data, np.uint8)
                self.cv2_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                #self.cv2_img = cv2.resize(self.cv2_img,(720,480),interpolation=cv2.INTER_AREA)
                #self.cv2_img = bridge.imgmsg_to_cv2(data, "bgr8")
            except CvBridgeError, e:
                print(e)
        def write(self):
            try:
                
                if self.cv2_img is None:
                    print('Camera could not detected!')
                if self.speed is None:
                    print('Speed could not detected!')
                if self.angle is None:
                    print('Angle could not detected!')

                if not self.cv2_img is None and not self.speed is None and not self.angle is None:
                    fname = self.path+'%05d.jpg'%self.index
                    if self.debug:
                        cv2.imshow('Image', self.cv2_img)
                    k = cv2.waitKey(10)
                    cv2.imwrite(fname,self.cv2_img)
                self.index += 1
                
            except Exception,e:
                print('Hang on a sec...',e)
                pass
def exit_gracefully(signal,frame):
    print('Exiting, wait for it...')
    sys.exit(0)



logger = seyir_logger()



if __name__ == '__main__':
    while not rospy.is_shutdown():
        #time.sleep(0.1)
        signal.signal(signal.SIGINT, exit_gracefully)
        if logger.speed != 0.0:
            logger.write()
            logger.rate.sleep()
            print('Speed : ', logger.speed, ' Angle : ', logger.angle)
        else:
            print("Not moving")
    rospy.spin()
