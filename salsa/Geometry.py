""" AUTHOR: Emma Lieb
    
    This file contains functions for computing all necessary geometry to be used for spectra convulution
"""
#***********************GEOMETRY FUNCTIONS************************************
'''Function to get the vector position from space craft to planet
Parameters:  
    ET - seconds calculated from time conversion functions above
    target - user input
'''

import importlib
import os

from astropy.constants.iau2012 import au

import numpy as np
from salsa import *
import spiceypy as spice


def makeUnitVector(vector):
    unitvector = spice.vhat(vector)
    
    X = unitvector[0]
    Y = unitvector[1]
    Z = unitvector[2]
    
    rtn_vector = np.array([X,Y,Z])
    
    return rtn_vector

def getVectorFromSpaceCraftToTarget(time, target):
    from salsa.TimeConversions import UTC2ET
    from salsa.GetKernels import getMissionFromTarget, getKernels
    ET = UTC2ET(time, target)
    #get mission named from target
    mission = getMissionFromTarget(target) 
    #get metakernel
    metakernel = getKernels(mission, 'getVectorFromSpaceCraftToTarget', time) 
    #load kernels
    spice.furnsh(metakernel)
    """
    NOTE ON ABBERATION CORRECTION FACTORS: NONE, LT and LT+S. None gives geometric position of the target body relative to
    the observer. LT returns vector corresponds to the position of the target at the moment it emitted photons arriving at the observer at `et'
    LT+S returns a vector that takes into account the observer's velocity relative to the solar system barycenter. 
     
    Thinking that LT+S may be the way to go. 
    """

    #second position vector is using target as stationary reference frame -- includes velocity of space craft
    target = target.upper()
    frame = 'IAU_'+ target.upper()
    correction = 'LT+S' #NOTE ABOVE
    observer = mission
    

    #compute state of space craft relative to object
    [state, lighttime] = spice.spkezr(target, ET, frame, correction, observer)
    
    #position vector components
    X = state[0]
    Y = state[1]
    Z = state[2]
    
    pos_vector = np.array([X,Y,Z])
    
#     #need position vector to calculate distance vector in order to calculate true distance
#     getVectorFromSpaceCraftToSun(ET, target, pos_vector)
    
    print('Apparent state of '+target+' as seen from '+mission+' in the '+frame+' fixed-body frame (km):')
    print('x_pos = {:16.3f}'.format(state[0]))
    print('y_pos = {:16.3f}'.format(state[1]))
    print('z_pos = {:16.3f}'.format(state[1]))
    
    return(pos_vector)
    
    #unload kernels
    spice.unload(metakernel)
    
'''Function to get the vector position from the target to the barycenter of the SS
Parameters:  
    ET - ephemeris seconds calculated from time conversion functions above
    target - user input
'''
def getVectorFromSpaceCraftToSun(time, target, pos_vector):
    from salsa.TimeConversions import UTC2ET
    from salsa.GetKernels import getMissionFromTarget, getKernels
    ET = UTC2ET(time, target)
    #get mission named from target
    mission = getMissionFromTarget(target)
    #get metakernel
    metakernel = getKernels(mission, 'getVectorFromSpaceCraftToTarget', time)
    #load kernels
    spice.furnsh(metakernel)
    
    #define objects needed for position function
    frame = 'IAU_'+ target.upper()
    target = mission
    correction = 'LT+S' #NOTE ON THIS IN PREV FUNCTION
    observer = 'SUN'
    
    [sundirection, lighttime ] = spice.spkpos(target, ET, frame, correction, observer)

    #sun direction vector
    X = sundirection[0]
    Y = sundirection[1]
    Z = sundirection[2]
    
    sunDir_vector = np.array([X,Y,Z])
    
    distance_vector = sunDir_vector+pos_vector
    
    #need target to sun vector for angular separation function and distance function
#     getAngularSeparation(ET, target, distance_vector)
#     getTargetSunDistance(distance_vector)
    
    print('Apparent direction of '+target+' as seen from the Sun in the '+frame+' fixed-body frame (km):')
    print('x_dir = {:16.3f}'.format(sundirection[0]))
    print('y_dir = {:16.3f}'.format(sundirection[1]))
    print('z_dir = {:16.3f}'.format(sundirection[2]))

    return(sunDir_vector)
    #unload kernels
    spice.unload(metakernel)
    
''' Function to get distance in AU from Sun to Target. 
Parameters: 
    sundirection - vector computed in 'getVectorFromTargetToSun'
'''
def getTargetSunDistance(distance_vector):
    #compute distance to sun using vector from target to sun
    distance = spice.vnorm(distance_vector)
    #convert distance from KM to AU
    distance = spice.convrt( distance, 'KM', 'AU')
    return(distance)

'''Function to get the velocity of the spacecraft with respect to the fixed-body reference frame of the target
Parameters:  
    ET - ephemeris seconds calculated from time conversion functions above
    target - user input
'''
  
def getVelocityVectorOfSpaceCraft(time, target):
    from salsa.TimeConversions import UTC2ET
    from salsa.GetKernels import getMissionFromTarget, getKernels
    ET = UTC2ET(time, target)
    #get mission named from target
    mission = getMissionFromTarget(target) 
    #get metakernel
    metakernel = getKernels(mission, 'getVectorFromSpaceCraftToTarget',time) 
    #load kernels
    spice.furnsh(metakernel)

    #second position vector is using target as stationary reference frame -- includes velocity of space craft
    target = target.upper()
    frame = 'IAU_'+ target.upper()
    correction = 'LT+S' #NOTE ABOVE
    observer = mission

    #compute state of space craft relative to object
    [state, lighttime] = spice.spkezr(target, ET, frame, correction, observer)
    
    #velocity vector components
    vX = state[3]
    vY = state[4]
    vZ = state[5]
    
    vel_vector = np.array([vX,vY,vZ])
    
    #need position vector to calculate distance vector in order to calculate true distance
    #getVectorFromSpaceCraftToSun(ET, target, pos_vector)
    
    print('Apparent state of '+target+' as seen from '+mission+' in the '+frame+' fixed-body frame (km/s):')
    print('x_vel = {:16.3f}'.format(state[3]))
    print('y_vel = {:16.3f}'.format(state[4]))
    print('z_vel = {:16.3f}'.format(state[5]))
    
    return(vel_vector)
    
    #unload kernels
    spice.unload(metakernel)
    
'''Function to get the angular separation between the vector from the target to the sun and the vector from Earth to the Sun
Parameters:  
    ET - ephemeris seconds calculated from time conversion functions above
    target - user input
    vector - result from 'getVectorFromTargetToSun' function
'''     
def getAngularSeparation(time, target, dist_vector):
    from salsa.TimeConversions import UTC2ET
    from salsa.GetKernels import getMissionFromTarget, getKernels
    ET = UTC2ET(time, target)
    #get mission named from target
    mission = getMissionFromTarget(target)
    #get metakernel
    metakernel = getKernels(mission, 'getAngularSeparation',time)
    #load kernels
    spice.furnsh(metakernel)
    #define objects needed for position function - EARTH 2 SUN
    earth = 'EARTH'
    frame  = 'J2000'
    correction = 'LT+S'
    observer = 'SUN'
    
    #compute direction from Earth to Sun
    [sundirection, lighttime ]= spice.spkpos(earth, ET, frame, correction, observer)
    
    X = sundirection[0]
    Y = sundirection[1]
    Z = sundirection[2]
    earthvector = np.array([X,Y,Z])
    
    #compute angular separation between earth vector and target vector
    ang_sep = spice.vsep(dist_vector,earthvector)
    #convert from radians to degrees
    ang_sep = spice.convrt(ang_sep, 'RADIANS', 'DEGREES')
    
    print( 'Angular separation between '+target+' and Earth in '+frame+'frame (degrees):' )
    print( 'Separation = {:16.3f}'.format(ang_sep))
    
    return(ang_sep)
    #unload kernels
    spice.unload(metakernel)    
       
'''Function to get the vector position (including planetocentric radius, longitude and latitude) of the sub-spacecraft point on the target object.
    (In fixed-body reference frame of target)
Parameters:  
    ET - ephemeris seconds calculated from time conversion functions above
    target - user input
'''
def getSubCraftVector(time, target):
    from salsa.TimeConversions import UTC2ET
    from salsa.GetKernels import getMissionFromTarget, getKernels
    ET = UTC2ET(time, target)
    #get mission named from target
    mission = getMissionFromTarget(target)
    #get metakernel
    metakernel = getKernels(mission, 'getSubCraftAndSubSolarVectors',time)
    #load kernels
    spice.furnsh(metakernel)
    
    #define objects needed for position function - sub-OBSERVER
    method = 'NEAR POINT/Ellipsoid' #NOTE BELOW
    frame  = 'IAU_'+ target.upper()
    correction = 'LT+S'
    observer = mission
    target = target.upper()
    
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
    
    vector = np.array([alt,lon,lat])
    return(vector)

    #unload kernels
    spice.unload(metakernel)
    
'''Function to get the apparent sub-solar point on the target w.r.t the spacecraft. (In fixed-body reference frame of target)
Parameters:  
    ET - ephemeris seconds calculated from time conversion functions above
    target - user input
'''
def getSubSolarVector(time, target):
    from salsa.TimeConversions import UTC2ET
    from salsa.GetKernels import getMissionFromTarget, getKernels
    ET = UTC2ET(time, target)
    #get mission named from target
    mission = getMissionFromTarget(target)
    #get metakernel
    metakernel = getKernels(mission, 'getSubSolarVector',time)
    #load kernels
    spice.furnsh(metakernel)
    #define objects needed for position function - sub-SOLAR
    method = 'INTERCEPT/Ellipsoid' #NOTE BELOW
    frame  = 'IAU_'+ target.upper()
    correction = 'LT+S'
    observer = mission
    target = target.upper()
    
    '''NOTE ON METHOD: The "Intercept/ellipsoid" method defines the sub-solar point as the target surface intercept of the line containing the Sun and
     the target's center, while the "Near point/ellipsoid" method defines the sub-solar point as the the nearest point on the target relative to the Sun'''
    
    #compute sub-solar point on target as seen from spacecraft
    [subpointsol, targetcentsol, surfvectsol] = spice.subslr(method, target, ET, frame, correction, observer)
    
    print( 'Apparent sub-solar point on '+target+' as seen from '+mission+' in the '+frame+' frame (km):' )
    print( 'X = {:16.3f}'.format(subpointsol[0]))
    print( 'Y = {:16.3f}'.format(subpointsol[1]))
    print( 'Z = {:16.3f}'.format(subpointsol[2]))
    
    X = subpointsol[0]
    Y = subpointsol[1]
    Z = subpointsol[2]
    
    vector = np.array([X,Y,Z])
    return(vector)
    
    #unload kernels
    spice.unload(metakernel)
    