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
    #do the math
    flux_at_target = np.divide(solar_flux, square_factor)

    print(flux_at_target)
    return(flux_at_target)