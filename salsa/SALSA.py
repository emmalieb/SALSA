from salsa.Geometry import getVectorFromSpaceCraftToSun,\
    getVectorFromSpaceCraftToTarget, getAngularSeparation, getTargetSunDistance
from salsa.SpectralCalibration import sunFaceCorrection, getFluxAtTarget,\
    getConvolvedSolarSpectrum, getPlanetaryData

def DistanceAdjustedSolarSpectrum(target, wavelengthLow, wavelengthHigh, time):
    #computer vector from spacecraft to target
    pos_vector = getVectorFromSpaceCraftToTarget(time, target)
    #compute vector from spaceraft to sun
    sunDir_vector = getVectorFromSpaceCraftToSun(time, target, pos_vector)
    #calculate distance vectgor from these two vectors
    distance_vector = sunDir_vector+pos_vector
    #calculate angular separation between earth and target
    angular_sep = getAngularSeparation(time, target, distance_vector)
    #correct for solar rotation rate
    solar_flux, wavelengths = sunFaceCorrection(angular_sep, time, wavelengthLow, wavelengthHigh)
    #compute physical distance between target and sun
    distance = getTargetSunDistance(distance_vector)
    #adjust solar spectrum for distance of target
    spectrum_at_target = getFluxAtTarget(solar_flux, wavelengths, distance)
     
    return spectrum_at_target 
 
def ConvolvedSolarSpectrum(target, time, wavelengthLow, wavelengthHigh, psf_waves = None, psf_vals = None):
    #get distance adjusted solar spectrum
    spectrum_at_target, wavelengths = DistanceAdjustedSolarSpectrum(target, time, wavelengthLow, wavelengthHigh)
    #do convolution - this will produce a plot
    convolved_spectrum = getConvolvedSolarSpectrum(spectrum_at_target, wavelengths, target, psf_waves, psf_vals)
     
    return convolved_spectrum

def PlanetaryReflectance(filename, target, time, wavelengthLow, wavelengthHigh, psf_waves=None, psf_vals = None):
    #get distance adjusted and colvolved solar spectrum - this will produce a plot
    convolved_spectrum, wavelengths = ConvolvedSolarSpectrum(target, time, wavelengthLow, wavelengthHigh, psf_waves, psf_vals)
    #get reflectance of planetary object - this will produce a plot
    data, wavelengths_ob = getPlanetaryData(filename, convolved_spectrum, wavelengths)
    
    return data