import spiceypy as spice
import numpy as np
import pandas as pd

def getMissionFromTarget(target):
    
    mission = ''
    
    if target is 'mercury' or target is 'Mercury':
        mission = 'MESSENGER'
    
    elif target is 'venus' or target is 'Venus':
        mission = 'VEGA'
        
    elif target is 'mars' or target is 'Mars':
        mission = 'MAVEN'
    
    elif target is 'jupiter' or target is 'Jupiter':
        mission = 'JUNO'
    
    elif target is 'saturn' or target is 'Saturn':
        mission = 'CASSINI'
    
    elif target is 'pluto' or target is 'Pluto':
        mission = 'NEWHORIZONS'
    
    elif target is 'moon' or target is'Moon':
        mission = 'LUNARORBITER'
        
    return mission


#TIME CONVERSION FUNCTIONS
def UTC2ET(time, metakernel, target):
    #converting from UTC time to ephemeris seconds since J2000 -- need leapseconds kernel -- 'kernels/lsk/naif0008.tls'
    #load kernels from metakernel
    spice.furnsh(metakernel)
    #convert time from UTC to ET
    ET = spice.str2et(time)
    #unload kernels
    spice.unload(metakernel)
    
    print(ET)
    return(ET)
    
def SCLK2ET(time, metakernel, target):
    #converting from space craft clock time string to ephemeris seconds since J2000 -- need leapseconds kernel and SCLK file for UTC time -'kernels/lsk/naif0008.tls','kernels/sclk/cas00084.tsc'
    #load kernels from metakernel
    spice.furnsh(metakernel)
    #convert time from UTC to ET
    ET = spice.str2et(time)
    #unload kernels
    spice.unload(metakernel)
    
    print(ET)
    return(ET)
    
def ET2Date(ET, metakernel):
    #At the end for readability in plots, may not be needed
    date = spice.etcal(ET)
    
    return(date)

#GEOMETRY FUNCTIONS
def getVectorFromSpaceCraftToTarget(ET, metakernel, target, mission):
    #getting vector position from space craft to planet
    #load kernels
    spice.furnsh(metakernel)
    #first position vector is using 'j2000' reference frame -- includes velocity of space craft
    frame = 'J2000'
    correction = 'Not sure what this should be yet' #NOTE BELOW
    observer = mission
    """
    NOTE ON ABBERATION CORRECTION FACTORS: NONE, LT and LT+S. None gives geometric position of the target body relative to
    the observer. LT returns vector corresponds to the position of the target at the moment it emitted photons arriving at the observer at `et'
    LT+S returns a vector that takes into account the observer's velocity relative to the solar system barycenter. 
    
    Thinking that LT+S may be the way to go. 
    """
    
    #compute state 9of space craft relative to object
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
    print('x_pos = '.format(+X), 'y_pos = '.format(+Y), 'z_pos = '.format(+Z))
    print('x_vel = '.format(+vX), 'y_vel = '.format(+vY), 'z_vel = '.format(+vZ))
    
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
    print('x_pos = '.format(+fX), 'y_pos = '.format(+fY), 'z_pos = '.format(+fZ))
    print('x_vel = '.format(+fvX), 'y_vel = '.format(+fvY), 'z_vel = '.format(+fvZ))
    
    #unload kernels
    spice.unload(metakernel)
    
    
def getVectorFromTargetToSun(ET, metakernel, target, mission):
    #getting vector position from planet to barycenter of the SS
    #load kernels
    spice.furnsh(metakernel)
    frame = 'J2000'
    correction = 'Not sure what this should be yet'
    observer = mission
    
    #unload kernels
    spice.unload(metakernel)

if __name__ == '__main__':
    #get meta kernel for all these functions, TODO: figure out how to tie that script to this one and tie both to 'user input' file
    