import matplotlib.pyplot as plt
import numpy as np
from salsa import *
import scipy.signal as signal
from scipy import interpolate
import spiceypy as spice
from matplotlib.pyplot import xlabel


'''Calculate solar rotation angle between Earth and given planet
and determine optimal number of days for time shifting
Earth-based irradiance to the planet
'''
def sunFaceCorrection(angular_sep, time):
    from datetime import datetime, timedelta
    sorce_time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
    
#     if angular_sep > 180:
#         angular_sep = angular_sep-360
#     elif angular_sep < -180:
#         angular_sep = angular_sep + 360

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
    
    #compute day to query by  - dividing ang sep by rot rate(DEG/DAY * DEG = 1/DAY)
    days_rot_forward = angular_sep / sun_rot_rate 
    
    #compute negativebackards angle 
    ang_sep_back = 360 - angular_sep
    #compute day to shift spectra by 
    days_rot_backward = ang_sep_back/sun_rot_rate
     
    #compute weights 
    weight_per_degree = 0.5/180
    weight_forward = weight_per_degree*angular_sep
    weight_back = weight_per_degree*ang_sep_back
    #compute time to query
    sorce_time_forward = sorce_time + timedelta(days = days_rot_forward)
    sorce_time_backward = sorce_time - timedelta(days = days_rot_backward)
    
    sorce_time_forward_range = sorce_time_forward + timedelta(days=1)
    sorce_time_backward_range = sorce_time_backward + timedelta(days=1)
    #make times into strings
    sorce_time_forward = str(sorce_time_forward)
    sorce_time_backward = str(sorce_time_backward)
    #strip spaces from time strings
    sorce_time_forward = sorce_time_forward.replace(sorce_time_forward[10:], "")
    sorce_time_backward = sorce_time_backward.replace(sorce_time_backward[10:], "")
    #turn time range into string
    sorce_time_forward_range = str(sorce_time_forward_range)
    sorce_time_backward_range = str(sorce_time_backward_range)
    #strip spaces from time string
    sorce_time_forward_range = sorce_time_forward_range.replace(sorce_time_forward_range[10:], "")
    sorce_time_backward_range = sorce_time_backward_range.replace(sorce_time_backward_range[10:], "")
    
    print("Times to query Solar data (forward and backward in time): ")
    print(sorce_time_forward, sorce_time_forward_range)
    print(sorce_time_backward, sorce_time_backward_range)
    
    #query solar spectra for both of these times
    url_forward = getURL('irradiance','wavelength', None, None, 180, 300, sorce_time_forward, sorce_time_forward_range)
    url_backward = getURL('irradiance','wavelength', None, None, 180, 300, sorce_time_backward, sorce_time_backward_range)
    
    #get data from urls and put into arrays
    data_forward = requests.get(url_forward).json()
    data_backward = requests.get(url_backward).json()
    #create dataframe
    df_forward = pd.DataFrame(data_forward["sorce_solstice_ssi_high_res"]["samples"][0]["samples"])
    #get irradiance from data frame
    irrad_forward = np.array(df_forward[['irradiance']])
    #create data frame
    df_backward = pd.DataFrame(data_backward["sorce_solstice_ssi_high_res"]["samples"][0]['samples'])
    #get irradiance from data frame
    irrad_backward = np.array(df_backward[['irradiance']])
    #linearly combine both spectra with weights as coefficients
    solar_flux = weight_forward*irrad_forward + weight_back*irrad_backward
    wavelengths = np.array(df_forward[['wavelength']])
    
    return(solar_flux, wavelengths)

"""Compute flux at the distance of the given target 
    - follows an inverse square law
"""   
def getFluxAtTarget(solar_flux, wavelengths, distance):
    #square the distance to divide by later
    square_factor = distance * distance
    #do the math
    flux_at_target = np.divide(solar_flux, square_factor)
    
    return(flux_at_target,wavelengths)

def plotBeforeAfterDistCorr(solar_flux, wavelengths, flux_at_target):
    import matplotlib.pyplot as plt

    plt.plot(wavelengths,solar_flux, marker = '.',color = 'r')
    plt.title('Solar Flux Before Distance Correction')
    plt.xlabel('Wavelength')
    plt.ylabel('Irradiance')
    plt.show()
    
    plt.plot(wavelengths, flux_at_target, marker = '.', color='b')
    plt.title('Solar Flux After Distance Correction')
    plt.xlabel('Wavelength')
    plt.ylabel('Irradiance')
    plt.show()
    
    ratio = solar_flux/flux_at_target
    
    plt.plot(wavelengths, ratio, marker = '.', color = 'm')
    plt.title('Ratio of Solar Flux to Solar Flux at Target')
    plt.xlabel('Wavelength')
    plt.ylabel('Ratio')
    plt.show()

def getPSF_CassiniUVIS(coeffs,wave):
    #NEED MORE EXPLANATION
    func = coeffs[0]+ coeffs[1]**((-0.5*(wave-coeffs[2])**2)/coeffs[3]**2)+coeffs[4]/(1+1/coeffs[5](wave-coeffs[2]**2))
    
    #not sure how to code last term --> Xrect(x-a2/w)
    
    return(func)
def getConvolvedSolarSpectrum_CassiniUVIS(spectra_at_target, wavelengths):
    #these are the cassini uvis coefficients - WANT TO WRITE FUNCTION THAT GETS THESE DYNAMICALLY BUT MAY NOT HAVE ENOUGH TIME
    coeffs = [0, 0.318, 121.569, 0.149, 0.00373, 1.507]
    convolved_spectrum = []
    #loop through wavelengths
    for wave in wavelengths:
        #convolving using lyman alpha
        coeffs[2]=wave
        #get point spread function
        psf = getPSF_CassiniUVIS(coeffs, wave)
        #perform convolution
        convolved_spectrum[wave] = signal.convolve(spectra_at_target, psf)
        
    #interpolate convolved spectra onto cassini UVIS wavelength grid
    convolved_specrtrum = interpolate.interp1d(convolved_spectrum,wavelengths)