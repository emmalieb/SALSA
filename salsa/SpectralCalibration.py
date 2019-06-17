import numpy as np
import spiceypy as spice
from salsa import *
from .DataQuery import *

def fluxDistanceRelationship(solar_data, distance):
    #figure out units 
    df = pd.DataFrame(solar_data["sorce_solstice_ssi_high_res"]["samples"][1]['samples'])
    #get irradiance from data frame
    solar_flux = np.array(df[['irradiance']])
    #square the distance to divide by later
    square_factor = distance * distance
    #loop through irradiance values
    for item in solar_flux:
        #get each index of irradiance array
        flux_at_sun = solar_flux[item]
        #do the math - inverse square law
        flux_at_target = np.divide(flux_at_sun[item], square_factor)

    print(flux_at_target)