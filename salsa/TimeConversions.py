import spiceypy as spice
import numpy as np
import importlib
from salsa import *
from .GetKernels import getMissionFromTarget
from astropy.constants.iau2012 import au
import os
#****************************TIME CONVERSION FUNCTIONS**********************************
'''Function to convert UTC time into ephemeris seconds since J2000
Parameters:  
    time - user input
    target - user input
'''
def UTC2ET(time, target):
    #converting from UTC time to ephemeris seconds since J2000 -- need leapseconds kernel -- 'kernels/lsk/naif0008.tls'
    #get mission named from target
#     mission = getMissionFromTarget(target) #TO DO: figure out classes and how to get this functions available to these functions
    #get metakernel
#     metakernel = getKernels(mission, 'UTC2ET') #TO DO: figure out classes and how to get those kernel functions available to these functions
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
#     mission = getMissionFromTarget(target) #TO DO: figure out classes and how to get this functions available to these functions
    #get metakernel
#     metakernel = getKernels(mission, 'UTC2ET') #TO DO: figure out classes and how to get those kernel functions available to these functions
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
    return(date)

def makeUnitVector(vector):
    unitvector = spice.vhat(vector)
    
    X = unitvector[0]
    Y = unitvector[1]
    Z = unitvector[2]
    
    rtn_vector = np.array([X,Y,Z])
    
    return rtn_vector
