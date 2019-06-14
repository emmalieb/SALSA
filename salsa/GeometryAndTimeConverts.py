import spiceypy as spice
import numpy as np
import importlib
from salsa import *
from GetKernels import *
from astropy.constants.iau2012 import au


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
#     metakernel = getKernels(mission, 'UTC2ET') #TO DO: figure out classes and how to get those kernel functions available to these functions
    #load kernels from metakernel
    spice.furnsh('naif0008.tls') #THIS WILL BE METAKERNEL
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
    mission = getMissionFromTarget(target) #TO DO: figure out classes and how to get this functions available to these functions
    #get metakernel
#     metakernel = getKernels(mission, 'UTC2ET') #TO DO: figure out classes and how to get those kernel functions available to these functions
    #load kernels from metakernel
    spice.furnsh('naif0008.tls')
    spice.furnsh('cas00084.tsc')
    #convert time from UTC to ET
    ET = spice.scs2e(-82, time)
    #unload kernels
    spice.unload('naif0008.tls')
    spice.unload('cas00084.tsc')
    
    print(ET)
    return(ET)
    
def ET2Date(ET):
    #At the end for readability in plots, may not be needed
    date = spice.etcal(ET)
    return(date)

def makeUnitVector(vector):
    unitvector = spice.vhat(vector)
    
    X =  unitvector[0]
    Y = unitvector[1]
    Z=unitvector[2]
    rtn_vector = np.array(X,Y,Z)
    
    return rtn_vector

#***********************GEOMETRY FUNCTIONS************************************
'''Function to get the vector position from space craft to planet
Parameters:  
    ET - ephemeris seconds calculated from time conversion functions above
    target - user input
'''
def getVectorFromSpaceCraftToTarget(ET, target):
    #get mission named from target
    mission = getMissionFromTarget(target) 
    #get metakernel
#     metakernel = getKernels(mission, 'getVectorFromSpaceCraftToTarget') 
    #load kernels
    spice.furnsh('metakernelTEST.tm')
    
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
    
    pos_vector = np.array(X,Y,Z)
    
#     #need position vector to calculate distance vector in order to calculate true distance
#     getVectorFromSpaceCraftToSun(ET, target, pos_vector)
    
    print('Apparent state of '+target+' as seen from '+mission+' in the '+frame+' fixed-body frame (km, km/s):')
    print('x_pos = {:16.3f}'.format(state[0]))
    print('y_pos = {:16.3f}'.format(state[1]))
    print('z_pos = {:16.3f}'.format(state[1]))
    
    return(pos_vector)
    
    #unload kernels
    spice.unload('metakernelTEST.tm')
    
'''Function to get the vector position from the target to the barycenter of the SS
Parameters:  
    ET - ephemeris seconds calculated from time conversion functions above
    target - user input
'''
def getVectorFromSpaceCraftToSun(ET, target, pos_vector):
    #get mission named from target
    mission = getMissionFromTarget(target)
    #get metakernel
#     metakernel = getKernels(mission, 'getVectorFromSpaceCraftToTarget')
    #load kernels
    spice.furnsh('metakernelTEST.tm')
    
    #define objects needed for position function
    frame = 'IAU_'+ target.upper()
    target = mission
    correction = 'LT+S' #NOTE ON THIS IN PREV FUNCTION
    observer = 'SUN'
    
    [sundirection, lighttime ]= spice.spkpos(target, ET, frame, correction, observer)

    #sun direction vector
    X = sundirection[0]
    Y = sundirection[1]
    Z = sundirection[2]
    
    sunDir_vector = np.array(X,Y,Z)
    
    distance_vector = sunDir_vector+pos_vector
    
    #need target to sun vector for angular separation function and distance function
#     getAngularSeparation(ET, target, distance_vector)
#     getTargetSunDistance(distance_vector)
    
    print('Apparent direction of '+target+' as seen from the Sun in the '+frame+' fixed-body frame (km, km/s):')
    print('x_dir = {:16.3f}'.format(sundirection[0]))
    print('y_dir = {:16.3f}'.format(sundirection[1]))
    print('z_dir = {:16.3f}'.format(sundirection[2]))

    return(sunDir_vector)
    #unload kernels
    spice.unload('metakernelTEST.tm')
    
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

'''Function to get the vvelocity of the spacecraft with respect to the fixed-body reference frame of the target
Parameters:  
    ET - ephemeris seconds calculated from time conversion functions above
    target - user input
'''
  
def getVelocityVectorOfSpaceCraft(ET, target):
    #get mission named from target
    mission = getMissionFromTarget(target) 
    #get metakernel
#     metakernel = getKernels(mission, 'getVectorFromSpaceCraftToTarget') 
    #load kernels
    spice.furnsh('metakernelTEST.tm')

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
    
    vel_vector = [vX,vY,vZ]
    
     #need position vector to calculate distance vector in order to calculate true distance
#     getVectorFromSpaceCraftToSun(ET, target, pos_vector)
    
    print('Apparent state of '+target+' as seen from '+mission+' in the '+frame+' fixed-body frame (km, km/s):')
    print('x_vel = {:16.3f}'.format(state[3]))
    print('y_vel = {:16.3f}'.format(state[4]))
    print('z_vel = {:16.3f}'.format(state[5]))
    
    return(vel_vector)
    
    #unload kernels
    spice.unload('metakernelTEST.tm')
    
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
#     metakernel = getKernels(mission, 'getAngularSeparation')
    #load kernels
    spice.furnsh('metakernelTEST.tm')
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
    print( 'Separation = {:16.3f}'.format(ang_sep[0]))
    
    return(ang_sep[0])
    #unload kernels
    spice.unload('metakernelTEST.tm')    
       
'''Function to get the vector position (including planetocentric radius, longitude and latitude) of the sub-spacecraft point on the target object.
    (In fixed-body reference frame of target)
Parameters:  
    ET - ephemeris seconds calculated from time conversion functions above
    target - user input
'''
def getSubCraftVector(ET, target):
    #get mission named from target
    mission = getMissionFromTarget(target)
    #get metakernel
#     metakernel = getKernels(mission, 'getSubCraftAndSubSolarVectors')
    #load kernels
    spice.furnsh('metakernelTEST.tm')
    
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
    
    vector = [alt,lon,lat]
    return(vector)

    #unload kernels
    spice.unload('metakernelTEST.tm')
    
'''Function to get the apparent sub-solar point on the target w.r.t the spacecraft. (In fixed-body reference frame of target)
Parameters:  
    ET - ephemeris seconds calculated from time conversion functions above
    target - user input
'''
def getSubSolarVector(ET, target):
    #get mission named from target
    mission = getMissionFromTarget(target)
    #get metakernel
#     metakernel = getKernels(mission, 'getSubSolarVector')
    #load kernels
    spice.furnsh('metakernelTEST.tm')
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
    
    vector = [X,Y,Z]
    return(vector)
    
    #unload kernels
    spice.unload('metakernelTEST.tm')
    