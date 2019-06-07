import spiceypy as spice
import numpy as py
import pandas as pd
import ftplib
from ftplib import FTP
from _ast import If

""" 
    Author: Emma Lieb
    
    This method gets the kernels needed for a given operations in the order they are called by the overall program and returns a meta-kernel of them. 

"""
'''Function to get mission name from target object name 
    Parameters:  
    target - user input
'''
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

'''Function to get mission name from target object name 
    Parameters:  
    target - user input
    functionName - passed in from functions that require the kernels
'''
def getKernels(target,  functionName):
    
    #get mission from target name
    mission = getMissionFromTarget(target)
    
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
    if functionName is 'UTC2ET':
        ftp.cwd('LSK')
        #load the kernels from here into metakernel
        #TO DO: WRITE METAKERNEL
    if functionName is 'SCLK2ET':
        ftp.cwd('LSK')
        #load the kernels from here into metakernel
        #TO DO: GET THE RIGHT KERNELS IN THIS DIRECTORY
        #back out of LSK directory and go into sclk directory
        
    #say goodbye
    ftp.quit()
    
def makeMetaKernel(kernels):
    #To do 

#NOT SURE HOW A MAIN WILL WORK FOR MY VARIOUS FILES OF FUNCTIONS, KIND OF WANT ONE MAIN FOR THE ALL THE FUNCTIONS WHERE THAT IS THE USER PROMPTS 
# if __name__ == '__main__':
#     
#     mission = getMissionFromTarget('Saturn')
#     print(mission)
#     
#     functionName = 'TO DO: figure out how to call getKernels in the order of the time/geometry functions so the proper kernels are found for each function'
#     
#     kernels = getKernels(mission, functionName)
#     
#     makeMetaKernel(kernels)
    