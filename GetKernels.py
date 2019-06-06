import spiceypy as spice
import numpy as py
import pandas as pd
import ftplib
from ftplib import FTP

""" 
    Author: Emma P. Lieb
    
    This method gets the kernels needed for a given operation and returns a metakernel of them. 

"""

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
    
    #not really a target
    elif target is 'pluto' or target is 'Pluto':
        mission = 'NEWHORIZONS'
    
    #really not a target
    elif target is 'moon' or target is'Moon':
        mission = 'LUNARORBITER'
        
    return mission

#this can only be used after knowing what the function has to do - it has to take in the mission, date, and function 'type'
def getKernels(mission,  functionName):
    
    #open ftp connection
    ftp = ftplib.FTP('naif.jpl.nasa.gov')
    ftp.login()
    
    #go into NAIF directory
    ftp.cwd('/pub/naif')
    
    #print what is in the NAIF directory
    #ftp.retrlines('LIST') 
    
    #go into mission director
    ftp.cwd(mission)
    
    #go to kernels directory
    ftp.cwd('kernels')
    
    #print what is in the kernels directory
    ftp.retrlines('LIST') 
    
    #find needed kernals
    #GOING TO USE IF STATEMENTS WITH FUNCTION NAMES FOR WHAT KERNALS TO GET - GOTTA PASS IN FUNCTIN NAMES
    
    #say goodbye
    ftp.quit()
    
def makeMetaKernel(kernels):
    

if __name__ == '__main__':
    
    mission = getMissionFromTarget('Saturn')
    print(mission)
    
    functionName = 'TO DO: figure out how to call getKernels in the order of the time/geometry functions so the proper kernels are found for each function'
    
    kernels = getKernels(mission, functionName)
    
#     makeMetaKernel(kernels)
    