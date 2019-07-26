from salsa.SALSA import DistanceAdjustedSolarSpectrum, ConvolvedSolarSpectrum, PlanetaryReflectance

#set target name
target = "Saturn"

#set time
time = '2004-06-11T19:32:00'

#set wavelength range
wavelengthLow = 110
wavelengthHigh = 190

#Set filename of planetary data
filename = 'FUV_Sat_Bring.fits'

#First, the user wants the distance adjusted solar spectrum 
spectrum_at_target = DistanceAdjustedSolarSpectrum(target, wavelengthLow, wavelengthHigh, time)

#this user does NOT have a specific point spread function to input
psf_waves = None
psf_vals = None

#Now, the user wants the convolved solar spectrum
convolved_spectrum = ConvolvedSolarSpectrum(target, time, wavelengthLow, wavelengthHigh, psf_waves, psf_vals)

#lastly, the user wants the reflectance of the object
reflectance = PlanetaryReflectance(filename, target, time, wavelengthLow, wavelengthHigh, psf_waves, psf_vals)
