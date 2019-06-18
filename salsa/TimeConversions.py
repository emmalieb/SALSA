import spiceypy as spice
import numpy as np
import importlib
from salsa import *
from .GetKernels import getMissionFromTarget
from astropy.constants.iau2012 import au
import os
import datetime
""" AUTHOR: Emma Lieb
    
    This file contains functions for converting user inputed time into ephemeris seconds.
"""

dir = '../../SALSA/test_kernels/'
#****************************TIME CONVERSION FUNCTIONS**********************************
'''Function to convert UTC time into ephemeris seconds since J2000
Parameters:  
    time - user input
    target - user input
'''
def UTC2ET(time, target):
    #converting from UTC time to ephemeris seconds since J2000 -- need leapseconds kernel -- 'kernels/lsk/naif0008.tls'
    #get mission named from target
#     mission = getMissionFromTarget(target) 
    #get metakernel
#     metakernel = getKernels(mission, 'UTC2ET') 
    #load kernels from metakernel
    spice.furnsh(dir+'naif0008.tls') #THIS WILL BE METAKERNEL
    #convert time from UTC to ET
    ET = spice.str2et(time)
    #unload kernels
    spice.unload('naif0008.tls')
    
    print(ET)
    return(ET)

'''Function to convert space craft clock string into ephemeris seconds since J2000
Parameters:  
    time - user input
    target - user input
'''
def SCLK2ET(time, target):
    #converting from space craft clock time string to ephemeris seconds since J2000 -- need leapseconds kernel and SCLK file for UTC time -'kernels/lsk/naif0008.tls','kernels/sclk/cas00084.tsc'
    #get mission name from target
    mission = getMissionFromTarget(target)
    #get metakernel
#     metakernel = getKernels(mission, 'UTC2ET') 
    #load kernels from metakernel
    spice.furnsh(dir+'naif0008.tls')
    spice.furnsh(dir+'cas00084.tsc')
    #convert time from UTC to ET
    ET = spice.scs2e(-82, time)
    #unload kernels
    spice.unload(dir+'naif0008.tls')
    spice.unload(dir+'cas00084.tsc')
    
    print(ET)
    return(ET)
    
def ET2Date(ET):
    #At the end for readability in plots, may not be needed
    date = spice.etcal(ET)
    print(date)
    return(date)

'''Function to convert UTC string time to SPK kernel date filename format'''
def UTC2SPKKernelDate(time):
    #UTC is: YYYY - MM - DD T hr:min:sec 
    #spk kernel format is: YYMMDD
    YY = time[2:4]
    MM = time[5:7]
    DD = time[8:10]
    kernelDate = YY+MM+DD
    
    return(kernelDate)

'''Function to convert UTC string time to CK kernel date filename format'''
def UTC2CKKernelDate(time):
    #UTC is: YYYY - MM - DD T hr:min:sec 
    #ck kernel AFTER Nov. 2003 is: YYDOY
    if int(time[0:10]) > int('2003-11-06'):
        YY = time[2:4]
        DOY = time.strftime('%j')
        kernelDate = YY+DOY
        
    #ck kernel BEFORE Nov. 2003 is: YYMMDD
    if int(time[0:10]) < int('2003-11-06'):
        YY = time[2:4]
        MM = time[5:7]
        DD = time[8:10]
        kernelDate = YY+MM+DD
    
    return(kernelDate)