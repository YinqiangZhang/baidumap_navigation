import requests
import rosbag
import sys
import os

import numpy as np
import matplotlib.pyplot as plt

class PathEmersioner(object):
    def __init__(self):
        self._local_dir = os.path.split(os.path.realpath(__file__))[0]
        self.api_key = "XYACZ9uAnCtOCLoOL2vEKVRGjzk1l3bz"
        self.header = {
             'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

    def save_path(self, center_lng, center_lat, markers_gps):
        url = "http://api.map.baidu.com/staticimage/v2?ak={}&coordtype=wgs84ll&center={},{}&width=1000&height=1000&zoom=18&paths={}&pathStyles=0xFF0000,5,1".format(
           self.api_key, center_lng, center_lat, markers_gps
         )

        image = requests.get(url, self.header)
        image_path = os.path.join(self._local_dir, 'baidu_map')
        if not os.path.exists(image_path):
            os.makedirs(image_path)
        f = open(os.path.join(image_path, 'path.png'), 'wb')
        f.write(image.content)
        f.close()
    
    def obtain_path(self, bag_file):
        bag = rosbag.Bag(bag_file, 'r')

        lngs = []
        lats = []
        markers_gps = ''

        bag_data = bag.read_messages('/ublox_gps/fix')
        for i, msg in enumerate(bag_data):
            if i % 5 == 0:
                longitude = msg[1].longitude
                latitude = msg[1].latitude
                lngs.append(longitude)
                lats.append(latitude)
                markers_gps += str(longitude)
                markers_gps += ','
                markers_gps += str(latitude)
                markers_gps += ';'

        markers_gps = markers_gps[:-1]
        center_lng = np.mean(np.array(lngs))
        center_lat = np.mean(np.array(lats))
        return center_lng, center_lat, markers_gps

if __name__ == "__main__":
    try:
        bag_file = sys.argv[1]
    except IndexError:
        hku_demo_dir = 'hku_bag'
        hku_demo_name = 'hku_demo_01.bag'
        bag_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], hku_demo_dir, hku_demo_name) 
        
    emerisioner = PathEmersioner()
    center_lng, center_lat, markers_gps = emerisioner.obtain_path(bag_file)
    emerisioner.save_path(center_lng, center_lat, markers_gps)
