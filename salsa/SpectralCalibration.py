import matplotlib.pyplot as plt
import numpy as np
from salsa import *
import scipy.signal as signal
from scipy import interpolate
import spiceypy as spice
from matplotlib.pyplot import xlabel
from networkx.algorithms.distance_measures import center
from dask.array.overlap import reflect
import requests
import pandas as pd
import os


'''Calculate solar rotation angle between Earth and given planet
and determine optimal number of days for time shifting
Earth-based irradiance to the planet
'''
def sunFaceCorrection(angular_sep, time, waveLow, waveHigh):
    from datetime import datetime, timedelta
    sorce_time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

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
    url_forward = getURL(waveLow, waveHigh, sorce_time_forward, sorce_time_forward_range)
    url_backward = getURL(waveLow, waveHigh, sorce_time_backward, sorce_time_backward_range)
    
    #get data from urls and put into arrays
    data_forward = requests.get(url_forward).json()
    data_backward = requests.get(url_backward).json()
    #create dataframe
    df_forward = pd.DataFrame(data_forward["sorce_solstice_ssi_high_res_template"]["samples"][0]["samples"])
    #get irradiance from data frame
    irrad_forward = np.array(df_forward[['irradiance']])
    #create data frame
    df_backward = pd.DataFrame(data_backward["sorce_solstice_ssi_high_res_template"]["samples"][0]['samples'])
    #get irradiance from data frame
    irrad_backward = np.array(df_backward[['irradiance']])
    #linearly combine both spectra with weights as coefficients
    solar_flux = weight_forward*irrad_forward + weight_back*irrad_backward
    wavelengths = np.array(df_forward[['wavelength']])
    
    return solar_flux, wavelengths

"""
Compute flux at the distance of the given target 
    - follows an inverse square law
"""   
def getFluxAtTarget(solar_flux, distance):
    #square the distance to divide by later
    square_factor = distance * distance
    #do the math
    flux_at_target = np.divide(solar_flux, square_factor)

    return flux_at_target

def plotBeforeAfterDistCorr(solar_flux, wavelengths, flux_at_target):
    import matplotlib.pyplot as plt

    plt.plot(wavelengths,solar_flux,color = 'k', label = 'Before')
    plt.title('Solar Flux Before Distance Correction', fontsize=20)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Irradiance (W/m**2/nm)')
    plt.show()
    
    plt.plot(wavelengths, flux_at_target, color='c', label = 'After')
    plt.title('Solar Flux After Distance Correction', fontsize=20)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Irradiance (W/m**2/nm)')
    plt.show()
"""
These are preset point spread functions
    - compatible with Cassini UVIS and Maven IUVS

"""
def getPSF(coeffs, wave, mission):
#check mission for what psf is needed - only return wanted psf
    if mission is 'CASSINI':
        func = coeffs[0]+coeffs[1]*np.exp((-0.5*((wave-coeffs[2])**2.))/(coeffs[3]**2.))+((coeffs[4])/(1.+(1./coeffs[5])*(wave-coeffs[2])**2.))
    
    elif mission is 'MAVEN':
        x = np.linspace(0, 100, 101, dtype=np.int)
        y = np.linspace(0, 100, 101, dtype=np.int)
        z = np.zeros(shape=(101,101),dtype=np.double)
        for i,j in zip(x,y): 
            z[j,i] = np.sqrt((i-0)**2.+(j-50)**2.)
        func = 1.*coeffs[0]*np.exp(-z*z/2./coeffs[1]/coeffs[1])+coeffs[2]/((z*z+coeffs[3]*coeffs[3]))+coeffs[4]
    return func 
"""
Function to compute user specified point spread function
Parameters: 
    wavelengths - wavelengths of point spread function
    values - points that describe point spread function
    center_wave - the current solar wavelength 
    solar_waves - solar wavelengths
"""
def simplePSF(wavelengths, values, center_wave, solar_waves):
    #find index of maximum in values
    max = np.where(values == max(values))
    peak_wave = wavelengths[max]
    #take difference between where center wave and maximum of vals
    shift = np.subtract(peak_wave, center_wave)
    #add or subtract the same difference from the wavelengths array
    new_waves = wavelengths - shift
    
    w = np.where(solar_waves<=max(new_waves) and solar_waves>=min(new_waves))
    new_values = np.interp(solar_waves[w], wavelengths, values)
    
    return solar_waves[w], new_values

"""
Function to calculate convolution of the distance adjusted solar spectrum onto a point spread function
Parameters: 
    spectra_at_target - distance adjusted solar spectrum
    wavelengths - solar wavelengths
    target - user input
    user_waves - optional: user can specify their own point spread function-array of wavelengths
    user_vals - optional: user can specify their own point spread function-array of numbers
"""
def getConvolvedSolarSpectrum(spectra_at_target, wavelengths, target, user_waves=None, user_vals=None): 
    from salsa.GetKernels import getMissionFromTarget
    from bisect import bisect
    
    if user_waves is not None and user_vals is not None:
        convolved_spectrum = np.zeros(shape=(len(wavelengths)))
        for i,wave in zip(range(0,len(wavelengths)),wavelengths):
            center_wave = wave
            psf_waves, psf_vals = simplePSF(user_waves, user_vals, center_wave, wavelengths)
            w = np.where(wavelengths<=max(psf_waves) and wavelengths>=min(psf_waves))
            psf = psf_vals/np.sum(psf_vals)
            convolved_spectrum[i] = np.sum(spectra_at_target[w]*psf)
    else:
        #get mission name
        mission = getMissionFromTarget(target)
        if mission is 'CASSINI':
    #        these are the cassini uvis coefficients
            coeffs = np.array([0.0, 0.318, 121.569, 0.149, 0.00373, 1.507])
            #create array for convolved spectrum
            convolved_spectrum = np.zeros(shape=(len(wavelengths),))
            for i,wave in zip(range(0,len(wavelengths)),wavelengths):
                coeffs[2]=wave
                #get point spread function
                psf = getPSF(coeffs, wavelengths,mission)
                psf = psf/np.sum(psf)
                #perform convolution
                convolved_spectrum[i] = np.sum(spectra_at_target*psf)
    
        elif mission is 'MAVEN':
    #        these are the maven iuvs coefficients
            coeffs = np.array([0.295565,2.15489,3.00259,1.97700,-0.00239266])
            #create wavelength array 
            waves = np.linspace(110, 190, len(wavelengths), dtype=np.double)
            for i,wave in zip(range(0,len(wavelengths)),waves):
                #search new wavelength array for the wavelength that you want - the indices are the pixel and what should be passed into psf
                ind = bisect(waves, wave, hi=len(waves)-1)
                center_wave = min(waves[ind], waves[ind-1],key=lambda x: abs(x - wave))
                pix = list(waves).index(center_wave)
                #get point spread function
                psf = getPSF(coeffs, pix, mission)
                psf = psf[:,0]
                #perform convolution
                convolved_spectrum[i] = np.mean(spectra_at_target[pix-50:pix+50]*psf)  
    #plot convolved spectrum     
    plotConvolvedSpectrum(spectra_at_target, convolved_spectrum, wavelengths)           
         
    return convolved_spectrum
"""
This function was written and developed by the Cassini UVIS processing team. 
The source code can be found at https://github.com/Cassini-UVIS/tools
"""
def cassini_uvis_fuv_wavelengths(xbin):
    RAD=180./3.1415926
    D=1.E7/1066
    ALP=(9.22+.032)/RAD
    ALP=ALP+3.46465e-5
    BET=(np.linspace(0,1023,1024)-511.5)*0.025*0.99815/300.0
    BET=np.arctan(BET)+0.032/RAD+3.46465e-5
    lam=D*(np.sin(ALP)+np.sin(BET))
    e_wavelength=lam
    if xbin == 1:
        return e_wavelength
    
    e_wavelength=np.zeros(shape=(1024//xbin,))
    for k in range(0,1024//xbin):
        e_wavelength[k]=np.sum(lam[k*xbin:(k+1)*xbin])/xbin
    
    return e_wavelength
"""
Function to get planetary data from FITS file data cube and plot reflectance of data based on solar data
Parameters: 
    filename - FITS file of planetary data
    solar_spectrum - distance adjusted and convolved solar spectrum
    wavelengths_sol - solar wavelengths
"""
def getPlanetaryData(filename, solar_spectrum, wavelengths_sol):
    from astropy.io import fits
    from astropy import units as u
    #read fits file
    hdu = fits.open(os.getcwd()+'/salsa/'+filename)
    #get data
    data = hdu[3].data['UVIS']
    ring = hdu[3].data['CENTER_RING_PLANE_RADII']
    w = ((ring > 92000) & (ring < 116500))
    
    xbin = hdu[3].data['XBIN'][0,0]
    print(data.shape)
    #get wavelengths
    wavelengths_ob = cassini_uvis_fuv_wavelengths(xbin)
    num = 1024//xbin
    wavelengths_ob = wavelengths_ob*(u.angstrom)
    wavelengths_ob = wavelengths_ob.to(u.nm)
    array = np.zeros(shape=len(wavelengths_ob),)
    counter = 0
    #loop over spatial dimension
    for x in range(data.shape[3]):
        #loop over read out dimension
        for y in range(data.shape[1]):
            if w[0,y,x]:
                #get slice
                spectrum = data[0,y,:num,x]
                #do unit conversion
                irradiance = unitConversion(spectrum, wavelengths_ob)
                #get I/F
                reflectance = getPlanetaryReflectance(solar_spectrum, irradiance, wavelengths_sol, wavelengths_ob, x, y)
                data[0,y,:num,x] = reflectance
                array += data[0,y,:num, x]
                counter += 1
                
    avg = array/counter
    
    #plot the ratio
    plt.plot(wavelengths_ob, avg, color = 'c')
    plt.title("Reflectance of Saturn's B-ring", fontsize=20)
    plt.ylabel('( I / F )', fontsize=17)
    plt.xlabel('Wavelength (nm)', fontsize=17)
    plt.show()

    return(data, wavelengths_ob)
"""
Function to convert units of planetary data in kR/Angstrom to the units of solar data in W/m^2/nm
Parameters: 
    irrad - intensity or flux of data
    wavelengths - planetary data wavelengths
"""
def unitConversion(irr, wavelengths):
    from astropy import units as u, constants as const
    #get plancks const and speed of light
    h = const.h
    c = const.c
    #convert wavelengths to meters
    wavelengths_m = wavelengths.to(u.m)
    #compute energy per photon at each wavelength
    E = h*c/wavelengths_m
    #unit conversion
    irradiance = irr*( 10**14*E/(4*np.pi))
    return(irradiance)

"""
Function to do ratio of solar data to planetary data - value known as reflectance of the planet
Parameters: 
    solar_spectrum - distance adjusted and convolved solar spectrum
    planetary_spectrum - planetary data irradiance (flux)
    wavelengths_sol - solar wavelengths
    wavelengths_ob - planetary wavelengths
"""
def getPlanetaryReflectance(solar_spectrum, planetary_spectrum, wavelengths_sol, wavelengths_ob, x, y):

    solar_spectrum = np.interp(wavelengths_ob, wavelengths_sol[:,0], solar_spectrum)
    #do ratio
    reflectance = planetary_spectrum/solar_spectrum
    
    return reflectance

'''
Function to plot the convolved solar spectrum 
    -overplotted with the distance adjusted solar spectrum
'''
def plotConvolvedSpectrum(spectra, convolved_spectrum, wavelengths):
    
    plt.plot(wavelengths,spectra, color = 'y',label = 'Normal')
    plt.plot(wavelengths,convolved_spectrum, color = 'k', label = 'Convolved')
    plt.legend(loc='upper right')
    plt.xlabel('Wavelength (nm)',fontsize=17)
    plt.ylabel('Irradiance (W/m^2/nm)',fontsize=17)
    plt.title('Solstice Spectra Convolved onto Cassini UVIS Point Spread Function', fontsize=20)
    plt.show()