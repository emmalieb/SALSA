import matplotlib.pyplot as plt
import numpy as np
from salsa import *
import scipy.signal as signal
import spiceypy as spice

from .DataQuery import *


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
    #get solar spectra
    df = pd.DataFrame(solar_data["sorce_solstice_ssi_high_res"]["samples"][1]['samples'])
    x = np.array(df[['wavelength']])
    y = np.array(df[['irradiance']])
    freqs = np.linspace(0.01, 10, 100000)
    #perform lombscargle 
    period = signal.lombscargle(x, y, freqs)
    #plot
    plt.plot(x,y,'r+')
    plt.plot(freqs,period)
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
    