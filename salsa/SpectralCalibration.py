import matplotlib.pyplot as plt
import numpy as np
from salsa import *
import scipy.signal as signal
import spiceypy as spice


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

def periodicAnalysis(solar_data):
    #instantiate arrays
    x = np.array([])
    y = np.array([])
    for i in range(365): #loop over number of days
        #get solar spectra
        df = pd.DataFrame(solar_data["sorce_ssi_l3"]["samples"][i])
        x = np.append(x, df['time'])
        df = pd.DataFrame(solar_data["sorce_ssi_l3"]["samples"][i]['spectrum'])
        y = np.append(y, df['irradiance'])
    freqs = np.linspace(x[0], x[len(x)-1])
    #perform lombscargle 
    pgram = signal.lombscargle(x, y, freqs)
    print(pgram)
#     plt.plot(x,y,'r+')
    plt.plot(freqs,pgram, 'r+')
    plt.show()
    #get modes
    #linearly combine

def sunFaceCorrection(angular_sep):
    #time of rotation of Sun depends on latitude of Sun - 25 days around equator, 30 days near poles
    degrees_of_rotation = 360 #degrees
    #equatorial rotation rate:
    rate_of_rotation = 27 #days 
    #time per degree
    rot_rate = rate_of_rotation/degrees_of_rotation #days per degree
    #convert to seconds per degree - 
    rot_rate = rot_rate*24*60*60
    #compute what face is at the planet according to angular separation from Earth
    sunface_corr = angular_sep * rot_rate
    
    print(sunface_corr)
    return(sunface_corr)
    