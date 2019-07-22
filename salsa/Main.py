from salsa.DataQuery import *
if __name__ == '__main__':
# #get user inputs for solar data query 
    target = input("Planetary object: \n")
    dataset = input("What solar data set do you want to use? (Default = solstice high resolution spectrum)\n")
    primaryParameter = input("Primary parameter:\n") #they dont need a choice here
    secondaryParameter= input("Secondary parameter:\n") #they dont need a choice hereSaturn
    wavelengthLow = input("Wavelength range - low end (nanometers): \n")
    wavelengthHigh = input('Wavelength range - high end (nanometers): \n')
    timeLow = input('UTC time string - start: \n')
    timeHigh = input('UTC time string - end: \n')
    filename = input('Filename containing planetary spectral data (in units of kR/Angstrom): \n')
    option1 = input('Do you want the solar spectrum for these times and wavelengths? (Y or N) \n')
    option2 = input('Do you want the solar spectrum corrected for the position of the object? (Y or N) \n')
    option3 = input('Do you want the solar spectrum convolved onto the PSF of the instrument? (Y or N) \n')
    option4 = input('Do you want the reflectance (I/F) of the object? (Y or N)\n')

#     url = getURL(primaryParameter, secondaryParameter, tertiaryParameter, dataset, wavelengthLow, wavelengthHigh, timeLow, timeHigh)
