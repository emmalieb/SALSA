from salsa.Geometry import getVectorFromSpaceCraftToSun,\
    getVectorFromSpaceCraftToTarget, getAngularSeparation, getTargetSunDistance
from salsa.SpectralCalibration import sunFaceCorrection, getFluxAtTarget,\
    getConvolvedSolarSpectrum, getPlanetaryData
from datetime import datetime, timedelta
from astropy.io import fits
import numpy as np
    
""" 
    - Main Function for SALSA: Solar Applied pLanetary dataSet cAlibration -
    
    Author: Emma Lieb
    Contributor: Joshua Elliott

"""

if __name__ == '__main__':
# #get user inputs for solar data query 
    target = input("Planetary object: \n")
#     mission = input('What spacecraft is this data from?\n')
#     instrument = input('What instrument is this data from?\n')

    wavelengthLow = input("Wavelength range - low end (nanometers): \n")
    wavelengthHigh = input('Wavelength range - high end (nanometers): \n')
    timeLow = input('UTC time string - start: \n')
    timeHigh = input('UTC time string - end: \n')
    
    filename = input('Filename containing planetary spectral data (in units of kR/Angstrom): \n')
    option1 = input('Do you want the solar spectrum corrected for the position of the object?(Y or N) \n')
    option2 = input('Do you want the solar spectrum convolved onto the PSF of the instrument?(Y or N) \n')
    option3 = input('Do you want the reflectance (I/F) of the object?(Y or N)\n')
#     
    shouldConvolve = input('Do you have a specific point spread function array to input? (Y/N)\n')
    
    if shouldConvolve is 'Y':
        psf_filename = input('Filename for Point Spread Function wavelengths and values: ')
        array_txt = np.loadtxt(psf_filename)
        psf_waves = array_txt[:0]
        psf_vals = array_txt[:1]
    else:
        psf_waves = None
        psf_vals = None
    
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
        
        spectrum_at_target = getFluxAtTarget(solar_flux, distance)
        
        convolved_spectrum = getConvolvedSolarSpectrum(spectrum_at_target, wavelengths, target, psf_waves, psf_vals)
        
        data, wavelengths_ob = getPlanetaryData(filename, convolved_spectrum, wavelengths)
        
#         if option1 is 'Y':
#                 #write fits files
#                 wavelength_col = fits.column(name = 'Wavelengths', array = wavelengths)
#                 irrad_col = fits.column(name = 'Irradiance', array = spectrum_at_target)
#                 t = fits.BinTableHDU.from_columns(wavelength_col, irrad_col)
#                 t.writeto('DistanceAdjustedSolarSpectrum.fits')
#         if option2 is 'Y':
#                 wavelength_col = fits.column(name = 'Wavelengths', array = wavelengths)
#                 irrad_col = fits.column(name = 'Irradiance', array = convolved_spectrum)
#                 t = fits.BinTableHDU.from_columns(wavelength_col, irrad_col)
#                 t.writeto('ConvolvedSolarSpectrum.fits')
#         if option3 is 'Y':
#                 wavelength_col = fits.column(name = 'Wavelengths', array = wavelengths_ob)
#                 irrad_col = fits.column(name = 'Irradiance', array = data)
#                 t = fits.BinTableHDU.from_columns(wavelength_col, irrad_col)
#                 t.writeto('PlanetaryReflectance.fits')
                
        startTime += delta
