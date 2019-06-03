import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.units import second

#http://lasp.colorado.edu/lisird/latis/dap/dataset.suffix?projection&selection&operation

urlStart = 'http://lasp.colorado.edu/lisird/latis/dap/'
suffix = '.json?'

def findDataset(wavelengthLow, wavelengthHigh):
    #FIND WAVELENGTH RANGES FOR DIFFERENT INSTRUMENTS 
    
    if wavelengthLow > 110 and wavelengthHigh < 320:
        foundDataset = 'sorce_solstice_ssi_high_res'
    
    
    return foundDataset

def getURL(primaryParameter, secondaryParameter=None, tertiaryParameter=None, dataset = None, wavelengthLow = None, wavelengthHigh = None, timeLow = None, timeHigh = None, operation=None):
    
    url=''
    
    if dataset is not None and operation is not None and secondaryParameter is not None and tertiaryParameter is not None:
        url = urlStart+dataset+suffix+primaryParameter+','+secondaryParameter+','+tertiaryParameter+'&operation'
        
        if operation is None:
            url = urlStart+dataset+suffix+primaryParameter+','+secondaryParameter+','+tertiaryParameter
        
        if wavelengthLow is not None and wavelengthHigh is not None:
            url = urlStart+dataset+suffix+primaryParameter+','+secondaryParameter+','+tertiaryParameter+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)
            
            if timeLow is not None and timeHigh is not None:
                url = urlStart+dataset+suffix+primaryParameter+','+secondaryParameter+','+tertiaryParameter+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)+'&time>='+timeLow+'&time<='+timeHigh
            
    elif wavelengthLow is not None and wavelengthHigh is not None and secondaryParameter is not None and tertiaryParameter is not None:
        
        foundDataset = findDataset(wavelengthLow, wavelengthHigh)
        url = urlStart+foundDataset+suffix+primaryParameter+','+secondaryParameter+','+tertiaryParameter+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)
    
        if timeLow is not None and timeHigh is not None:
            url = urlStart+foundDataset+suffix+primaryParameter+','+secondaryParameter+','+tertiaryParameter+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)+'&time>='+timeLow+'&time<='+timeHigh

    if dataset is not None and operation is not None and tertiaryParameter is None:
        url = urlStart+dataset+suffix+str(primaryParameter)+str(secondaryParameter)+'&operation'
        
        if operation is None:
            url = urlStart+dataset+suffix+str(primaryParameter)+str(secondaryParameter)
        
        if wavelengthLow is not None and wavelengthHigh is not None:
            url = urlStart+dataset+suffix+str(primaryParameter)+','+str(secondaryParameter)+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)
            
            if timeLow is not None and timeHigh is not None:
                url = urlStart+dataset+suffix+str(primaryParameter)+','+str(secondaryParameter)+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)+'&time>='+timeLow+'&time<='+timeHigh
            
    elif wavelengthLow is not None and wavelengthHigh is not None and tertiaryParameter is None:
        
        foundDataset = findDataset(wavelengthLow, wavelengthHigh)
        
        url = urlStart+foundDataset+suffix+str(primaryParameter)+','+str(secondaryParameter)+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)
    
        if timeLow is not None and timeHigh is not None:
            url = urlStart+foundDataset+suffix+str(primaryParameter)+','+str(secondaryParameter)+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)+'&time>='+timeLow+'&time<='+timeHigh
    return(url)    

def plotDataFromURL(data):
    
    df = pd.DataFrame(data["sorce_solstice_ssi_high_res"]["samples"][1]['samples'])
    
    print(df)
    
    subdf = df[["irradiance","wavelength"]]
     
    subdf.plot(x="wavelength",y="irradiance")
    plt.show()

if __name__ == '__main__':

    
    """ 
    getURL(parameters,'dataset', 'wavelengthLow', 'wavelengthHigh', 'timeLow', 'timeHigh' , 'operation')
    
    User must pass in EITHER: the data set name or the desired wavelength range AND the primary parameter. 
        --> parameters should be a string with no commas or spaces
        --> Typically, the primary parameter is Irradiance and the secondary and tertiary parameters are Wavelength and Time
        
        Common Data Set Names: 
            'sorce_solstice_ssi_high_res' - Mid and Far UV 
            NEED MORE EXAMPLES 
     
     optional: 
        timeLow and timeHigh: specify a time range --> if the using a time range, do not include 'time' in parameters 
        
        operation
         Common Operations: 
            ADD EXAMPLES
            
    example: 
        queryData('irradiance','sorce_solstice_ssi_high_res', '180', '300', '2010-03-20', '2010-03-24', 'convert_time')
        
     """
    parameters = ['time','wavelength','irradiance']
    
    url = getURL('irradiance','wavelength',None,None, 180, 300, '2010-03-20', '2010-03-24', 'convert_time')
   
    print(url)
    
    data = requests.get(url).json() 
    
    plottingData = plotDataFromURL(data)
