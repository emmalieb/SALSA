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

def periodicAnalysis(solar_data,days):
    #instantiate arrays
#     x = np.array([])
    y = np.array([])
    print(days)
    for i in range(days): #loop over number of days
        #get solar spectra
#         df = pd.DataFrame(solar_data["sorce_ssi_l3"]["samples"][i])
#         x = np.append(x, df['time'])
        df = pd.DataFrame(solar_data["sorce_ssi_l3"]["samples"][i]['spectrum'])
        y = np.append(y,df['irradiance'].to_numpy(dtype='float64'))

    w = np.where(np.isfinite(y))
    y = y[w]
    y[y == None] = 0
#     print(x)
    print(y)

    #get periodogram  
    f,pgram = signal.periodogram(y)
    f[f == 0] = None
#     print(pgram)
    #plot periodogram
    plt.plot(1/f,pgram, 'r-')
    plt.xlabel('Frequency')
    plt.ylabel('Power Spectral Density')
    plt.show()
    #get modes
    peaks, peak_heights = signal.find_peaks(pgram,height = 0)
    #loop through heights which is a dictionary to make array of just the heights
    for key,val in peak_heights.items():
        heights = val
    #instantiate arrays for getting desired periods only
    indices = []
    periods = []
    #loop through peaks
    for i in range(len(peaks)):
        #check to see if the peaks are in desired range
        if peaks[i] >=24 and peaks[i] <=32:
            #add indice to array to get corresponding heights later
            indices.append(i)
            #add desired peaks to array
            periods.append(peaks[i])
    print(periods)
    #get corresponding heights to the desired periods
    heights = heights[indices]
    print(heights)
        
    #dive each peak height by sum of all heights
    height_sum = heights.sum()
    height_coeffs = heights/height_sum
    print(height_coeffs)
                
    return(height_coeffs)

def sunFaceCorrection(angular_sep, coeffs, time):
    sorce_time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
    #time of rotation of Sun depends on latitude of Sun - 25 days around equator, 30 days near poles
    degrees_of_rotation = 360 #degrees
    #equatorial rotation rate:
    periods_of_rotation = [25,29,31] #days
    #time per degree
    rotation_rates = periods_of_rotation/degrees_of_rotation #days per degree
    print(rotation_rates)
    #compute time to query
    times_to_rotate = rotation_rates*angular_sep
    print(times_to_rotate)
    times_to_query = sorce_time-times_to_rotate
    print(times_to_query)
    
    
    