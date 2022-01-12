#! /usr/bin/python

import os
import tf
import time
import rospy
import numpy as np
from sensor_msgs.msg import NavSatFix
import matplotlib.pyplot as plt

class GPSReceivor():
    def __init__(self):
        
        rospy.init_node("gnss_node")
        
        # earth parameters 
        self.a = 6378137.0 # Semi-major axis
        self.b = 6356752.3142 # Semi-minor axis
        self.f = (self.a - self.b) / self.a # inverse of reciprocal of flattening
        self.e_square = self.f * (2 - self.f) # First eccentricity squared
        
        # initial geodetic coordinates
        self.ref_geo_pos = NavSatFix()
        self.ref_ecef = np.zeros((3,))
        # TODO: a rosservice can be written here for setting origin adaptively 
        self.set_initial_position = False
        
        # gnss subscriber and publisher
        self._gnss_sub = rospy.Subscriber('/ublox_gps/fix', NavSatFix, self._gnss_cb)
        
        # tf
        self._tf_broadcaster = tf.TransformBroadcaster()
        
        # result list
        self.coords_list = list()
        
        time.sleep(1)
    
    def run(self):
        loop = rospy.Rate(0.5)
        plt.ion()
        while not rospy.is_shutdown():
            if len(self.coords_list) != 0:
                temp_list = np.array(self.coords_list)
                plt.plot(temp_list[0, :], temp_list[1, :], color='r', linewidth=1.5)
                plt.pause(0.2)
                plt.ioff()
            loop.sleep()
        
    def wgs84_to_ecef(self, geo_pos):
        """
            converts coordinates P1 from WGS84 to ECEF coordinates
        """
        
        lon = geo_pos.longitude * np.pi /180.0
        lat = geo_pos.latitude * np.pi /180.0
        alt = geo_pos.altitude
        
        # intermidate results
        temp = np.sqrt(1 + (1-self.e_square)* np.square(np.tan(lon)))
        temp2 = np.sqrt(1-self.e_square*np.square(np.sin(lat))) 
        
        x = (self.a * np.cos(lon)) / temp + alt*np.cos(lon)*np.cos(lat)
        y = (self.a * np.sin(lon)) / temp + alt*np.sin(lon)*np.sin(lat)
        z = (self.a * (1-self.e_square) * np.sin(lat)) / temp2 + alt*np.sin(lat)

        return np.array([x, y, z])
    
    def get_enu_position(self, geo_pos):
        """
            converts the target ECEF points in the ENU reference
        """
        
        ref_lon = self.ref_geo_pos.longitude * np.pi /180.0
        ref_lat = self.ref_geo_pos.latitude * np.pi /180.0
        
        ref_R = np.array([[-np.sin(ref_lon), np.cos(ref_lat), 0], 
                      [-np.sin(ref_lat)*np.cos(ref_lon), -np.sin(ref_lat)*np.sin(ref_lon), np.cos(ref_lat)], 
                      [np.cos(ref_lat)*np.cos(ref_lon), np.cos(ref_lat)*np.sin(ref_lon), np.sin(ref_lat)]])
        
        delta_ecef = self.wgs84_to_ecef(geo_pos) - self.ref_ecef
        
        enu = np.matmul(ref_R, delta_ecef)
        
        return enu
    
    def _gnss_cb(self, msg):
        """
            callback function of GNSS subscriber
        """
        if not self.set_initial_position:
            self.ref_geo_pos = msg
            self.ref_ecef = self.wgs84_to_ecef(self.ref_geo_pos)
            self.set_initial_position = True
        
        current_enu = self.get_enu_position(msg)
        rospy.loginfo('E:{},N:{},U:{}'.format(current_enu[0], current_enu[1], current_enu[2]))
        
        self.coords_list.append([current_enu[0], current_enu[1]])

        # remove z coordinate
        t_w2o = (current_enu[0],
                 current_enu[1],
                 0.0)
        quat_w2o = (0,0,0,1)
        
        self._tf_broadcaster.sendTransform(t_w2o, quat_w2o, msg.header.stamp, 'odom', 'world')
            
    
if __name__ == "__main__":
    GPS_node = GPSReceivor()
    GPS_node.run()