import matplotlib.pyplot as plt
import numpy as np
from salsa import *
import scipy.signal as signal
import spiceypy as spice
from matplotlib.pyplot import xlabel


def fluxDistanceRelationship(solar_data, distance):
    #figure out units 
    df = pd.DataFrame(solar_data["sorce_solstice_ssi_high_res"]["samples"][1]['samples'])
    #get irradiance from data frame
    solar_flux = np.array(df[['irradiance']])
    #square the distance to divide by later
    square_factor = distance * distance
    #do the math
    flux_at_target = np.divide(solar_flux, square_factor)

    print(flux_at_target)
    return(flux_at_target)

'''Calculate solar rotation angle between Earth and given planet
and determine optimal number of days for time shifting
Earth-based irradiance to the planet
'''
def sunFaceCorrection(angular_sep, time):
    sorce_time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
    #time of rotation of Sun depends on latitude of Sun - 25 days around equator, 30 days near poles
    degrees_of_rotation = 360 #degrees
    #period of rotation of sun 
    period = 27 #days
    #compute rotation rate of sun
    sun_rot_rate_wrt_Earth = degrees_of_rotation/period #degrees per day
    #compute orbital rate of earth around sun
    period = 365 #days
    earth_rot_rate = degrees_of_rotation/period
    #add rates together to account for movement of earth
    sun_rot_rate = sun_rot_rate_wrt_Earth + earth_rot_rate
    print('The Suns rotation rate w.r.t to Solar System (degrees/day): ')
    print(sun_rot_rate)
    
    #compute day to query by dividing ang sep by rot rate(DEG/DAY * DEG = 1/DAY)
    days_rot = angular_sep / sun_rot_rate 
    
    print('Number of days to shift Solar spectra by: ')
    print(days_rot)
    