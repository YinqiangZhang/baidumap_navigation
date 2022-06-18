import requests
import json
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

class  RidePlaner(object):
    def  __init__(self):
        self._local_dir = os.path.split(os.path.realpath(__file__))[0]
        self.api_key = "SIxrxBpid4EOWamRCnB0adoepHvfMrYv"
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

    def calculate_path(self, origin_gps, destination_gps):
        url = "http://api.map.baidu.com/direction/v2/riding?&coord_type=wgs84&origin={}&destination={}&ak={}".format(
            origin_gps, destination_gps, self.api_key
        )
        html = requests.get(url, headers = self.header)

        html_dir = json.loads(html.text, encoding='utf-8')['result']['routes'][0]['steps']
        path_origin_dir = json.loads(html.text, encoding='utf-8')['result']['routes'][0]['originLocation']
        path_destination_dir = json.loads(html.text, encoding='utf-8')['result']['routes'][0]['destinationLocation']
        transformed_path_origin_gps = '{},{}'.format(path_origin_dir['lng'], path_origin_dir['lat'])
        transformed_path_destination_gps = '{},{}'.format(path_destination_dir['lng'], path_destination_dir['lat'])
        
        origin_lngs, origin_lats = [], []
        markers_gps = ''
        markers_gps = '{};'.format(transformed_path_origin_gps)
        for i in range(len(html_dir)):
            step_info = html_dir[i]
            origin_lng = step_info['stepOriginLocation']['lng']
            origin_lat = step_info['stepOriginLocation']['lat']
            # TODO: add transform from bd09 to wgs84
            # origin_lng, origin_lat = bd09_to_wgs84(origin_lng, origin_lat)
            origin_lngs.append(origin_lng)
            origin_lats.append(origin_lat)
            markers_gps += str(origin_lng)
            markers_gps += ','
            markers_gps += str(origin_lat)
            markers_gps += ';'
            paths = step_info['path'].split(';')[1: -1]
            for j in range(len(paths)):
                # lng, lat = bd09_to_wgs84(float(paths[j].split(',')[1]), float(paths[j].split(',')[0]))
                markers_gps += paths[j]
                # markers_gps += '{},{}'.format(lat,lng)
                markers_gps += ';'

        markers_gps += transformed_path_destination_gps
        # markers_gps += destination_gps.split(',')[1] + ',' + destination_gps.split(',')[0]
        center_lng = np.mean(np.array(origin_lngs))
        center_lat = np.mean(np.array(origin_lats))

        return center_lng, center_lat, markers_gps
    
    def save_path(self, center_lng, center_lat, markers_gps):
        url = "http://api.map.baidu.com/staticimage/v2?ak={}&center={},{}&width=1000&height=1000&zoom=18&paths={}&pathStyles=0xFF0000,5,1".format(
            self.api_key, center_lng, center_lat, markers_gps
        )
        image = requests.get(url, headers = self.header)
        image_path = os.path.join(self._local_dir, 'baidu_map')
        if not os.path.exists(image_path):
            os.makedirs(image_path)
        f = open(os.path.join(image_path, 'path_rideplan.png'), 'wb')
        f.write(image.content)
        f.close()

if __name__ == "__main__":
    # origin_gps = '22.60808431791728,114.00273340573993'
    # destination_gps = '22.599153684226555,114.00588269527528'
    
    # data from GPS 
    # For inputs, WGS84 coordinate is necessary here
    # origin_gps = '22.284486,114.138118' 
    # destination_gps = '22.283519,114.138126'
    
    # data from Baidu Map (SUST) 
    # origin_gps = '22.600639,114.008534'
    # destination_gps = '22.60808431791728,114.00273340573993' # '22.603759,114.004423'
    
    origin_gps = '22.2844866,114.1381188'
    destination_gps = '22.2835301,114.1391492'
    
    planner = RidePlaner()
    center_lng, center_lat, markers_gps = planner.calculate_path(origin_gps, destination_gps)
    planner.save_path(center_lng, center_lat, markers_gps)
