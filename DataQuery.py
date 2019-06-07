import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import Main

"""
    Author: Emma Lieb
    
    This function allows the user to get a URL specified by input parameters that can be used to query solar data. 
    
    getURL(primaryParameter,secondayParameter, tertiaryParameter,'dataset', 'wavelengthLow', 'wavelengthHigh', 'timeLow', 'timeHigh' , 'operation')
    
    User is required to pass in EITHER: the data set name OR the desired wavelength range AND the primary and secondary parameters. 
        --> parameters should all be a string with no commas or spaces
        --> Typically, the primary parameter is irradiance and the secondary and tertiary parameters are wavelength and time but the User is free to choose.
        --> The user can input both a dataset name and a wavelength range. 
        
        High-Resolution Ultraviolet Data Set Name: 
            'sorce_solstice_ssi_high_res' - Mid and Far UV 
        
     
     Optional Parameters: 
       
        timeLow and timeHigh
            specify a time range
                e.g. timeLow = '2010-03-20' , timeHigh = '2010-03-24'
        
        operation
         Common Operations: 
            convert_time(units)
                Convert time values to the given units.
            drop(n)
                Return all but the first n samples.
            exclude_missing
                Exclude all samples that contain a missing value.
            first
                Return only the first sample.
            format_time(format)
                Convert time values to the given format (for text output) as specified by Java's SimpleDateFormat.
                    e.g. format_time(yyyy-MM-dd'T'HH:mm:ss.SSS)
            last
                Return only the last sample.
            limit(n)
                Return the first n samples.
            rename(orig, new)
                Change the name of a variable given its original and new name.
            replace_missing
                Replace any missing value with the given value.
            stride(n)
                Return every nth sample.
            take(n)
                Return the first n samples.
            take_right(n)
                Return the last n samples.

    Example:
        Input: 
            getURL('irradiance','wavelength',None, None, 180, 300, '2010-03-20', '2010-03-24', 'convert_time')
        Output: 
            http://lasp.colorado.edu/lisird/latis/dap/sorce_solstice_ssi_high_res.json?irradiance,wavelength&wavelength%3E=180&wavelength%3C=300&time%3E=2010-03-20&time%3C=2010-03-24
"""

'''Function to create a URL that queries the solar data from a given dataset on LISRD
Parameters:
    primaryParameter - commonly 'irradiance' but can be another quantity as long as the column exists in the data
    secondaryParameter - commonly 'wavelength' but can be another quantity as long as the column exists in the data
    tertiaryParameter - optional user input, commonly 'time'
    dataset - optional user input, if the user knows the solar data set name it can be passed in directly
    wavelengthLow, wavelengthHigh - wavelength range given by user to limit results, if they did not specify a solar dataset name it is used to find the dataset name
    timeLow, timeHigh - time range given by the user to limit results
'''
def getURL(primaryParameter, secondaryParameter, tertiaryParameter=None, dataset = None, wavelengthLow = None, wavelengthHigh = None, timeLow = None, timeHigh = None):
    
    urlStart = 'http://lasp.colorado.edu/lisird/latis/dap/'
    suffix = '.json?'
    url=''
    
    #If the user passed in a dataset name, an operation, and all three parameters, the URL is stitched together directly.
    if dataset is not None and tertiaryParameter is not None:
        url = urlStart+dataset+suffix+primaryParameter+','+secondaryParameter+','+tertiaryParameter
            
        #If the user also passed in a wavelength range, it it included in the URL
        if wavelengthLow is not None and wavelengthHigh is not None:
            url = urlStart+dataset+suffix+primaryParameter+','+secondaryParameter+','+tertiaryParameter+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)
            
            #If the user passed in a time range, it is included in the URL
            if timeLow is not None and timeHigh is not None:
                url = urlStart+dataset+suffix+primaryParameter+','+secondaryParameter+','+tertiaryParameter+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)+'&time>='+timeLow+'&time<='+timeHigh
    
    #If the user did not give a dataset name, but they did pass in a wavelength range and all three parameters, the wavelength range is used to find the dataset name and then the URL is stitched together directly.
    elif wavelengthLow is not None and wavelengthHigh is not None and secondaryParameter is not None and tertiaryParameter is not None:
        
        #Call to function that finds the dataset name
        foundDataset = findDataset(wavelengthLow, wavelengthHigh)
        url = urlStart+foundDataset+suffix+primaryParameter+','+secondaryParameter+','+tertiaryParameter+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)
    
        #If the user passed in a time range, it is included in the URL
        if timeLow is not None and timeHigh is not None:
            url = urlStart+foundDataset+suffix+primaryParameter+','+secondaryParameter+','+tertiaryParameter+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)+'&time>='+timeLow+'&time<='+timeHigh
    
    #If the user passed in a dataset name, an operation, but only the Primary and Secondary parameters, the URL is stitched together directly excluding a Tertiary parameter
    if dataset is not None and tertiaryParameter is None:
        url = urlStart+dataset+suffix+str(primaryParameter)+str(secondaryParameter)
        
        #If the user also passed in a wavelength range, it it included in the URL without the Tertiary parameter
        if wavelengthLow is not None and wavelengthHigh is not None:
            url = urlStart+dataset+suffix+str(primaryParameter)+','+str(secondaryParameter)+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)
            
            #If the user passed in a time range, it is included in the URL without the Tertiary parameter
            if timeLow is not None and timeHigh is not None:
                url = urlStart+dataset+suffix+str(primaryParameter)+','+str(secondaryParameter)+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)+'&time>='+timeLow+'&time<='+timeHigh
            
    elif wavelengthLow is not None and wavelengthHigh is not None and tertiaryParameter is None:
        
        #Call function to find dataset name based on wavelengths given
        foundDataset = findDataset(wavelengthLow, wavelengthHigh)
        
        url = urlStart+foundDataset+suffix+str(primaryParameter)+','+str(secondaryParameter)+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)
    
        #If the user passed in a time range, it is included in the URL without the tertiary parameter
        if timeLow is not None and timeHigh is not None:
            url = urlStart+foundDataset+suffix+str(primaryParameter)+','+str(secondaryParameter)+'&wavelength>='+str(wavelengthLow)+'&wavelength<='+str(wavelengthHigh)+'&time>='+timeLow+'&time<='+timeHigh
    
    return(url) 
 
'''Function to find the dataset that corresponds to the wavelength range given by the user
Parameters:
    wavelengthLow, wavelengthHigh - wavelength range given by user if they did not specify a solar dataset name 
'''
def findDataset(wavelengthLow, wavelengthHigh):
    
    #check the wavelength range given
    if wavelengthLow > 110 and wavelengthHigh < 320:
        foundDataset = 'sorce_solstice_ssi_high_res'
    
    return foundDataset

'''Function to plot the solar data queried from the URL created above.
Parameters:
    data - returned from 'getURL'
'''
def plotDataFromURL(data):
    
    #create dataframe using pandas - reading json
    df = pd.DataFrame(data["sorce_solstice_ssi_high_res"]["samples"][1]['samples'])
    
    print(df)
    
    #get data columns
    subdf = df[["irradiance","wavelength"]]
     
    #plot solar data
    subdf.plot(x="wavelength",y="irradiance", title="Solar Spectrum", color='m')
    plt.show()
