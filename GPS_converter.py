import numpy as np


class GPSConverter():
    """
        Global-local Transformatrion for GPS coordinates
    """    
    def __init__(self):
        """
            Parameter initialization
        """
        
        # earth parameters 
        self.a = 6378137.0 # Semi-major axis
        self.b = 6356752.3142 # Semi-minor axis
        self.f = (self.a - self.b) / self.a # inverse of reciprocal of flattening
        self.e_square = self.f * (2 - self.f) # First eccentricity squared
    
    def wgs84_to_ecef(self, geo_pos):
        """
            converts coordinates P1 from WGS84 to ECEF coordinates
        """
        
        lon = geo_pos[0] * np.pi /180.0
        lat = geo_pos[1] * np.pi /180.0
        alt = 0.0

        N = self.a/np.sqrt(1 - self.e_square*np.sin(lat)*np.sin(lat))
        x = (N + alt)*np.cos(lat)*np.cos(lon)
        y = (N + alt)*np.cos(lat)*np.sin(lon)
        z = ((1-self.e_square)*N + alt)*np.sin(lat) 

        return np.array([x, y, z], ndmin=2)

    def get_enu_position(self, geo_pos, ref_pos):
        """
            converts the target ECEF points in the ENU reference
            reference: https://gssc.esa.int/navipedia/index.php/Transformations_between_ECEF_and_ENU_coordinates
        """
        
        ref_ecef = self.wgs84_to_ecef(ref_pos)
        
        ref_lon = ref_pos[0] * np.pi/180.0
        ref_lat = ref_pos[1] * np.pi/180.0
        
        ref_R = np.array([[-np.sin(ref_lon), np.cos(ref_lon), 0], 
            [-np.sin(ref_lat)*np.cos(ref_lon), -np.sin(ref_lat)*np.sin(ref_lon), np.cos(ref_lat)], 
            [np.cos(ref_lat)*np.cos(ref_lon), np.cos(ref_lat)*np.sin(ref_lon), np.sin(ref_lat)]])
            
        delta_ecef = self.wgs84_to_ecef(geo_pos) - ref_ecef
        enu = np.dot(ref_R, delta_ecef.T)
        
        return enu
