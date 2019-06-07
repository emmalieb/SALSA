import spiceypy as spice
import numpy as np
import pandas as pd
import importlib
import Main
from GetKernels import *


""" AUTHOR: Emma Lieb
    
    This file contains functions for converting user inputed time into ephemeris seconds 
    and computes all necessary geometry to be used for spectra convolutions
"""
#****************************TIME CONVERSION FUNCTIONS**********************************
'''Function to convert UTC time into ephemeris seconds since J2000
    Parameters:  
    time - user input
    target - user input
'''
def UTC2ET(time, target):
    #converting from UTC time to ephemeris seconds since J2000 -- need leapseconds kernel -- 'kernels/lsk/naif0008.tls'
    #get mission named from target
    mission = getMissionFromTarget(target) #TO DO: figure out classes and how to get this functions available to these functions
    #get metakernel
    metakernel = getKernels(mission, 'UTC2ET') #TO DO: figure out classes and how to get those kernel functions available to these functions
    #load kernels from metakernel
    spice.furnsh(metakernel)
    #convert time from UTC to ET
    ET = spice.str2et(time)
    #unload kernels
    spice.unload(metakernel)
    
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
    mission = getMissionFromTarget(target) #TO DO: figure out classes and how to get this functions available to these functions
    #get metakernel
    metakernel = getKernels(mission, 'UTC2ET') #TO DO: figure out classes and how to get those kernel functions available to these functions
    #load kernels from metakernel
    spice.furnsh(metakernel)
    #convert time from UTC to ET
    ET = spice.str2et(time)
    #unload kernels
    spice.unload(metakernel)
    
    print(ET)
    return(ET)
    
def ET2Date(ET):
    #At the end for readability in plots, may not be needed
    date = spice.etcal(ET)
    return(date)

#***********************GEOMETRY FUNCTIONS************************************
'''Function to get the vector position from space craft to planet
    Parameters:  
    ET - ephemeris seconds calculated from time conversion functions above
    target - user input
'''
def getVectorFromSpaceCraftToTarget(ET, target):
    #get mission named from target
    mission = getMissionFromTarget(target) #TO DO: figure out classes and how to get this functions available to these functions
    #get metakernel
    metakernel = getKernels(mission, 'getVectorFromSpaceCraftToTarget') #TO DO: figure out classes and how to get those kernel functions available to these functions
    #load kernels
    spice.furnsh(metakernel)
    #first position vector is using 'j2000' reference frame -- includes velocity of space craft
    frame = 'J2000'
    correction = 'LT+S' #NOTE BELOW
    observer = mission
    
    """
    NOTE ON ABBERATION CORRECTION FACTORS: NONE, LT and LT+S. None gives geometric position of the target body relative to
    the observer. LT returns vector corresponds to the position of the target at the moment it emitted photons arriving at the observer at `et'
    LT+S returns a vector that takes into account the observer's velocity relative to the solar system barycenter. 
    
    Thinking that LT+S may be the way to go. 
    """
    
    #compute state of space craft relative to object
    [state, lighttime] = spice.spkezr(target, ET, frame, correction, observer)
    
    #position vector components
    X = state[0]
    Y = state[1]
    Z = state[2]
    #velocity vector components
    vX = state[3]
    vY = state[4]
    vZ = state[5]
    
    print('Apparent state of '+target+' as seen from '+mission+' in the J2000 frame (km, km/s):')
    print('x_pos = '.format(X), 'y_pos = '.format(Y), 'z_pos = '.format(Z))
    print('x_vel = '.format(vX), 'y_vel = '.format(vY), 'z_vel = '.format(vZ))
    
    #second position vector is using target as stationary reference frame -- includes velocity of space craft
    frame = 'IAU_'+ target.upper()
    correction = 'Not sure what this should be yet' #NOTE ABOVE
    observer = mission

    #compute state of space craft relative to object
    [state, lighttime] = spice.spkezr(target, ET, frame, correction, observer)
    
    # ' f ' is for fixed-body reference frame - don't know which frame is better, keeping both for now
    #position vector components
    fX = state[0]
    fY = state[1]
    fZ = state[2]
    #velocity vector components
    fvX = state[3]
    fvY = state[4]
    fvZ = state[5]
    
    print('Apparent state of '+target+' as seen from '+mission+' in the '+frame+' fixed-body frame (km, km/s):')
    print('x_pos = '.format(fX), 'y_pos = '.format(fY), 'z_pos = '.format(fZ))
    print('x_vel = '.format(fvX), 'y_vel = '.format(fvY), 'z_vel = '.format(fvZ))
    
    #unload kernels
    spice.unload(metakernel)
    
'''Function to get the vector position from the target to the barycenter of the SS
    Parameters:  
    ET - ephemeris seconds calculated from time conversion functions above
    target - user input
'''
def getVectorFromTargetToSun(ET, target):
    #get mission named from target
    mission = getMissionFromTarget(target) #TO DO: figure out classes and how to get this functions available to these functions
    #get metakernel
    metakernel = getKernels(mission, 'getVectorFromSpaceCraftToTarget') #TO DO: figure out classes and how to get those kernel functions available to these functions
    
    #load kernels
    spice.furnsh(metakernel)
    frame = 'J2000'
    correction = 'Not sure what this should be yet' #NOTE ON THIS IN PREV FUNCTION
    observer = 'SUN'
    
    sundirection, lightime = spice.spkpos(target, ET, frame, correction, observer)
    
    #sun directin vector
    X = sundirection[0]
    Y = sundirection[1]
    Z = sundirection[2]
    
    print('Apparent direction of '+target+' as seen from the Sun in the '+frame+' fixed-body frame (km, km/s):')
    print('x_dir = '.format(+X), 'y_dir = '.format(+Y), 'z_dir = '.format(+Z))
    
    #make into unit vector
    sundirUnit = spice.vhat(sundirection)
    
    Xhat = sundirUnit[0]
    Yhat = sundirUnit[1]
    Zhat = sundirUnit[2]
    
    print('Apparent direction of '+target+' as seen from the Sun in the '+frame+' fixed-body frame (km, km/s) expressed a unit vector:')
    print('x_dir = '.format(+Xhat), 'y_dir = '.format(+Yhat), 'z_dir = '.format(+Zhat))
    
    #unload kernels
    spice.unload(metakernel)
  
    