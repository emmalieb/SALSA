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
    observer = mission.toUpper()
    
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
    observer = mission.toUpper()

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
    mission = getMissionFromTarget(target)
    #get metakernel
    metakernel = getKernels(mission, 'getVectorFromSpaceCraftToTarget')
    #load kernels
    spice.furnsh(metakernel)
    
    #define objects needed for position function
    frame = 'J2000'
    correction = 'LT+S' #NOTE ON THIS IN PREV FUNCTION
    observer = 'SUN'
    
    [sundirection, lighttime ]= spice.spkpos(target, ET, frame, correction, observer)
    
    #sun direction vector
    X = sundirection[0]
    Y = sundirection[1]
    Z = sundirection[2]
    
    vector = [X,Y,Z]
    
    print('Apparent direction of '+target+' as seen from the Sun in the '+frame+' fixed-body frame (km, km/s):')
    print('x_dir = '.format(+X), 'y_dir = '.format(+Y), 'z_dir = '.format(+Z))
    
    #normalize vector
    sundirUnit = spice.vhat(sundirection)
    
    Xhat = sundirUnit[0]
    Yhat = sundirUnit[1]
    Zhat = sundirUnit[2]
    
    unitvector = [Xhat,Yhat,Zhat]
    
    print('Apparent direction of '+target+' as seen from the Sun in the '+frame+' fixed-body frame (km, km/s) expressed a unit vector:')
    print('x_dir = '.format(+Xhat), 'y_dir = '.format(+Yhat), 'z_dir = '.format(+Zhat))
    
    #need target to sun vector for angular separation function
    getAngularSeparation(ET, target, vector)

    #unload kernels
    spice.unload(metakernel)
    
'''Function to get the vector position (including planetocentric radius, longitude and latitude) of the sub-spacecraft point on the target object
        and to get the apparent sub-solar point on the target w.r.t the spacecraft. (Both in fixed-body reference frame of target)
    Parameters:  
    ET - ephemeris seconds calculated from time conversion functions above
    target - user input
'''
def getSubCraftAndSubSolarVectors(ET, target):
    #get mission named from target
    mission = getMissionFromTarget(target)
    #get metakernel
    metakernel = getKernels(mission, 'getSubCraftAndSubSolarVectors')
    #load kernels
    spice.furnsh(metakernel)
    
    #define objects needed for position function - sub-OBSERVER
    method = 'NEAR POINT/Ellipsoid' #NOTE BELOW
    frame  = 'IAU_'+ target.upper()
    correction = 'LT+S'
    observer = mission.toUpper()
    
    #Compute the apparent sub-observer point of mission on target (cartesian vector)
    [subpoint, targetcent, surfvect ]= spice.subpnt(method, target, ET, frame, correction, observer)
    #computer altitude of spacecraft from sub-observer point
    alt = spice.vnorm(surfvect)
    #convert to planetocentric radius, longitude, and latitude
    [rad, lon, lat] = spice.reclat(subpoint)
    #convert from radians to degrees
    lon,lat = lon,lat * spice.dpr()
    
    print( 'Apparent sub-observer point of '+mission+' on '+target+' in the '+frame+' frame (km):' )
    print( 'LONGITUDE = {:16.3f}'.format(lon))
    print( 'LATITUDE = {:16.3f}'.format(lat))
    print( 'ALTITUDE = {:16.3f}'.format(alt))
    
    #define objects needed for position function - sub-SOLAR
    method = 'INTERCEPT/Ellipsoid' #NOTE BELOW
    frame  = 'IAU_'+ target.upper()
    correction = 'LT+S'
    observer = mission.toUpper()
    
    '''NOTE ON METHOD: The "Intercept/ellipsoid" method defines the sub-solar point as the target surface intercept of the line containing the Sun and
     the target's center, while the "Near point/ellipsoid" method defines the sub-solar point as the the nearest point on the target relative to the Sun'''
    
    #compute sub-solar point on target as seen from spacecraft
    [subpointsol, targetcentsol, surfvectsol] = spice.subslr(method, target, ET, frame, correction, observer)
    
    print( 'Apparent sub-solar point on '+target+' as seen from '+mission+' in the '+frame+' frame (km):' )
    print( 'X = '.format(subpointsol[0]))
    print( 'Y = '.format(subpointsol[1]))
    print( 'Z = '.format(subpointsol[2]))
    
    #unload kernels
    spice.unload(metakernel)
    
'''Function to get the angular separation between the vector from the target to the sun and the vector from Earth to the Sun
    Parameters:  
    ET - ephemeris seconds calculated from time conversion functions above
    target - user input
    vector - result from 'getVectorFromTargetToSun' function
'''   
def getAngularSeparation(ET, target, vector):
    #get mission named from target
    mission = getMissionFromTarget(target)
    #get metakernel
    metakernel = getKernels(mission, 'getAngularSeparation')
    #load kernels
    spice.furnsh(metakernel)
    #define objects needed for position function - EARTH 2 SUN
    target = 'SUN'
    frame  = 'J2000'
    correction = 'LT+S'
    observer = 'EARTH'
    
    #compute direction from Earth to Sun
    [sundirection, lighttime ]= spice.spkpos(target, ET, frame, correction, observer)
    
    [X,Y,Z]= sundirection[0], sundirection[1], sundirection[2]
    earthvector = [X,Y,Z]
    
    #compute angular separation between earth vector and target vector
    ang_sep = spice.vsep(vector,earthvector)
    #convert from radians to degrees
    ang_sep = spice.convrt(ang_sep, 'RADIANS', 'DEGREES')
    
    print( 'Angular separation between '+target+' and Earth in '+frame+'frame (degrees):' )
    print( 'Separation = '.format(ang_sep[0]))

    #unload kernels
    spice.unload(metakernel)