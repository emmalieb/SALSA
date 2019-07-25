from salsa.Geometry import getVectorFromSpaceCraftToSun,\
    getVectorFromSpaceCraftToTarget, getAngularSeparation, getTargetSunDistance
from salsa.SpectralCalibration import sunFaceCorrection, getFluxAtTarget,\
    getConvolvedSolarSpectrum, getPlanetaryData
from datetime import datetime, timedelta
    
""" 
    - Main Function for SALSA: Solar Applied pLanetary dataSet cAlibration -
    
    Author: Emma Lieb
    Contributor: Joshua Elliott

"""
# def DistanceAdjustedSolarSpectrum(target, wavelengthLow, wavelengthHigh, time):
#     #computer vector from spacecraft to target
#     pos_vector = getVectorFromSpaceCraftToTarget(time, target)
#     #compute vector from spaceraft to sun
#     sunDir_vector = getVectorFromSpaceCraftToSun(time, target, pos_vector)
#     #calculate distance vectgor from these two vectors
#     distance_vector = sunDir_vector+pos_vector
#     #calculate angular separation between earth and target
#     angular_sep = getAngularSeparation(time, target, distance_vector)
#     #correct for solar rotation rate
#     solar_flux, wavelengths = sunFaceCorrection(angular_sep, time, wavelengthLow, wavelengthHigh)
#     #compute physical distance between target and sun
#     distance = getTargetSunDistance(distance_vector)
#     #adjust solar spectrum for distance of target
#     spectrum_at_target = getFluxAtTarget(solar_flux, wavelengths, distance)
#     
#     return spectrum_at_target, wavelengths
# 
# def ConvolvedSolarSpectrum(target, time, wavelengthLow, wavelengthHigh, psf_waves = None, psf_vals = None):
#     #get distance adjusted solar spectrum
#     spectrum_at_target, wavelengths = DistanceAdjustedSolarSpectrum(target, time, wavelengthLow, wavelengthHigh)
#     #do convolution 
#     convolved_spectrum = getConvolvedSolarSpectrum(spectrum_at_target, wavelengths, target, psf_waves, psf_vals)
#     
#     return convolved_spectrum


if __name__ == '__main__':
# #get user inputs for solar data query 
    target = input("Planetary object: \n")
    mission = input('What spacecraft is this data from?\n')
    instrument = input('What instrument is this data from?\n')

    wavelengthLow = input("Wavelength range - low end (nanometers): \n")
    wavelengthHigh = input('Wavelength range - high end (nanometers): \n')
    timeLow = input('UTC time string - start: \n')
    timeHigh = input('UTC time string - end: \n')
    
    filename = input('Filename containing planetary spectral data (in units of kR/Angstrom): \n')
    option2 = input('Do you want the solar spectrum corrected for the position of the object? (Y or N) \n')
    option3 = input('Do you want the solar spectrum convolved onto the PSF of the instrument? (Y or N) \n')
    option4 = input('Do you want the reflectance (I/F) of the object? (Y or N)\n')
    
    startTime = datetime.strptime(timeLow, '%Y-%m-%dT%H:%M:%S')
    endTime = datetime.strptime(timeHigh, '%Y-%m-%dT%H:%M:%S')
    #loop through days of date range
    delta = timedelta(days=1)
    while startTime <= endTime:

        pos_vector = getVectorFromSpaceCraftToTarget(str(startTime), target)
        
        sunDir_vector = getVectorFromSpaceCraftToSun(str(startTime), target, pos_vector)
        
        distance_vector = sunDir_vector+pos_vector
        
        angular_sep = getAngularSeparation(str(startTime), target, distance_vector)
        
        solar_flux, wavelengths = sunFaceCorrection(angular_sep, str(startTime), wavelengthLow, wavelengthHigh)
        
        distance = getTargetSunDistance(distance_vector)
        
        spectrum_at_target, wavelengths = getFluxAtTarget(solar_flux, wavelengths, distance)
        
        shouldConvolve = input('Do you have a point spread function array to input? (Y/N)\n')
        if shouldConvolve is 'Y':
            psf_filename = input('Filename for Point Spread Function wavelengths and values: ')
            convolved_spectrum = getConvolvedSolarSpectrum(spectrum_at_target, wavelengths, target)
        
        data, wavelengths_ob = getPlanetaryData(filename, convolved_spectrum, wavelengths)

        startTime += delta
        
    #astropy write fits files
    #print path to fits file written
