from astropy import units as u

def rayleighPerAng2Solstice(data):
    #create units given from instrument
    data_orig_units = data*(u.R/u.angstrom)
    #convert to solstice hi res units
    data_solar_units = data_orig_units.to(u.Watt/u.m**2/u.nm, equivalence = u.spectral())
    
    return(data_solar_units)