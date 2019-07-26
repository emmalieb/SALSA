"""
    Author: Emma Lieb
"""
'''Function to create a URL that queries the solar data from a given dataset on LISRD
Parameters:
    wavelengthLow, wavelengthHigh - wavelength range given by user to limit results, if they did not specify a solar dataset name it is used to find the dataset name
    timeLow, timeHigh - time range given by the user to limit results
'''
def getURL(wavelengthLow, wavelengthHigh, timeLow, timeHigh):
    
    urlStart = 'http://lasp.colorado.edu/lisird/latis/dap/'
    suffix = '.json?'
    primaryParameter = 'irradiance'
    secondaryParameter = 'wavelength'
    
    dataset = findDataset(wavelengthLow, wavelengthHigh)
    
    url = urlStart+dataset+suffix+primaryParameter+','+secondaryParameter+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)+'&time>='+timeLow+'&time<='+timeHigh
    
    return(url) 
 
'''Function to find the dataset that corresponds to the wavelength range given by the user
Parameters:
    wavelengthLow, wavelengthHigh - wavelength range given by user if they did not specify a solar dataset name 
'''
def findDataset(wavelengthLow, wavelengthHigh):
    
    #check the wavelength range given
    if wavelengthLow >= '110' and wavelengthHigh <= '320':
        foundDataset = 'sorce_solstice_ssi_high_res'
    elif wavelengthLow<='110' or wavelengthHigh >= '320':
        foundDataset = 'sorce_ssi_l3' 
    
    return foundDataset

    
