""" AUTHOR: Emma Lieb
    
    This file contains functions for converting user inputed time into ephemeris seconds.
"""

from datetime import datetime,date
import importlib
import os

from astropy.constants.iau2012 import au

import numpy as np
import spiceypy as spice
from salsa.GetKernels import *


#****************************TIME CONVERSION FUNCTIONS**********************************
'''Function to convert UTC time into ephemeris seconds since J2000
Parameters:  
    time - user input
    target - user input
'''
def UTC2ET(time, target):
    #converting from UTC time to ephemeris seconds since J2000 -- need leapseconds kernel -- 'kernels/lsk/naif0008.tls'
    #get mission named from target
    mission = getMissionFromTarget(target) 
    #get metakernel
    metakernel = getKernels(mission, target, 'UTC2ET',time) 
    #load kernels from metakernel
    spice.furnsh(metakernel) #THIS WILL BE METAKERNEL
    #convert time from UTC to ET
    ET = spice.str2et(time)
    #unload kernels
    spice.unload(metakernel)
    
    return(ET)

'''Function to convert space craft clock string into ephemeris seconds since J2000
Parameters:  
    time - user input
    target - user input
'''
# def SCLK2ET(time, target):
#     #converting from space craft clock time string to ephemeris seconds since J2000 -- need leapseconds kernel and SCLK file for UTC time -'kernels/lsk/naif0008.tls','kernels/sclk/cas00084.tsc'
#     #get mission name from target
#     mission = getMissionFromTarget(target)
#     #get metakernel
#     metakernel = getKernels(mission, 'SCLK2ET', time) 
#     #load kernels from metakernel
#     spice.furnsh(metakernel)
#     #convert time from SCLK to ET
#     ET = spice.scs2e(-82, time)
#     #unload kernels
#     spice.unload(metakernel)
#     
#     print(ET)
#     return(ET)
#     
def ET2Date(ET):
    #At the end for readability in plots, may not be needed
    date = spice.etcal(ET)
    return(date)

'''Function to convert UTC string time to SPK kernel date filename format'''
def UTC2SPKKernelDate(time):
    #UTC is: YYYY - MM - DD T hr:min:sec 
    #spk kernel format is: YYMMDD
    YY = time[2:4]
    month = time[5:7]
    day = time[8:10]
    a = datetime.strptime(month+'/'+day+'/'+YY, '%m/%d/%y')
    day = a.timetuple()
    DOY = day.tm_yday
    kernelDate = YY+str(DOY) 
    return(kernelDate)

'''Function to convert UTC string time to CK kernel date filename format'''
def UTC2CKKernelDate(time):
#     kernelDate = ''
    year = time[2:4]
    month = time[5:7]
    day = time[8:10]
    
    a = datetime.strptime(month+'/'+day+'/'+year, '%m/%d/%y')
    b = datetime.strptime('11/06/03', '%m/%d/%y')
    #UTC is: YYYY - MM - DD T hr:min:sec 
    #ck kernel AFTER Nov. 2003 is: YYDOY
    if a > b:
        YY = time[2:4]
        day = a.timetuple()
        DOY = day.tm_yday
        kernelDate = YY+str(DOY)
        
    #ck kernel BEFORE Nov. 6 2003 is: YYMMDD
    elif a < b:
        YY = time[2:4]
        MM = time[5:7]
        DD = time[8:10]
        kernelDate = YY+MM+DD
    
    return(kernelDate)

'''Function to convert UTC string time to PCK date filename format'''
def UTC2PCKKernelDate(time,target):
    #UTC is: YYYY - MM - DD T hr:min:sec 
    #PCK kernel is: DDMonthYYYY - ex: 11Jun2004
    et = UTC2ET(time, target)
    date = spice.etcal(et)
    
    YYYY = date[0:4]
    Month = date[5:8].lower()
    DD = date[9:11]
    
    mon = Month.capitalize()
    
    kernelDate = DD+mon+YYYY
    
    return kernelDate

def getNumberOfDaysBetween(timeLow, timeHigh):
    d1 = datetime.strptime(timeLow, '%Y-%m-%d')
    d2 = datetime.strptime(timeHigh,'%Y-%m-%d')
    delta = d2-d1
    return(delta.days)