import spiceypy as spice
import numpy as py
import pandas as pd
import ftplib
from ftplib import FTP
import kernelDescriptions
import Main

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
def getKernels(target, functionName):
    
    #get mission from target name
    mission = getMissionFromTarget(target)
    
    #open ftp connection
    ftp = ftplib.FTP('naif.jpl.nasa.gov')
    ftp.login()
    
    #go into NAIF directory
    ftp.cwd('/pub/naif')
      
    #go into mission director
    ftp.cwd(mission)
    
    #go to kernels directory
    ftp.cwd('kernels')
    
    #print what is in the kernels directory
    ftp.retrlines('LIST') 
    
    #find needed kernels based on function calling for them
    if functionName is 'UTC2ET':
        path_vals = 'kernels/lsk'
        ftp.cwd('LSK')
        #get kernel filenames
        kernels = ftp.retrlines('RETR filename')
        #load the kernels from here into metakernel
        writeMetaKernel(path_vals, kernels, functionName, mission)
        
    elif functionName is 'SCLK2ET':
        path_vals = "'kernels/lsk', 'kernels/sclk'"
        ftp.cwd('LSK')
        #get kernel filenames
        kernels = ftp.retrlines('RETR filename')
        #back out of LSK directory and go into sclk directory
        ftp.cwd('cd ..')
        ftp.cwd('SCLK')
        #get kernel filenames
        kernels = kernels+ftp.retrlines('RETR filename')
        #load the kernels from here into metakernel
        writeMetaKernel(path_vals, kernels, functionName, mission)

    #say goodbye
    ftp.quit()
    
def writeMetaKernel(path_vals, kernels, functionName, mission):
    #open file according to functionName 
    mode = 'w'
    filename = functionName.toUpper()
    mkfile = open(filename, mode)
    #write header
    mkfile.write('\begintext')
    mkfile.write('The names and contents of the kernels referenced by this meta-kernel are as follows:')
    #get descriptions of kernels for meta kernel
    kernelDscr = kernelDescriptions(kernels, mission)
    #Write kernel descriptions
    mkfile.write('FILE NAME'+"    "+"CONTENTS")
    mkfile.write(kernels+ "    "+kernelDscr)
    #oepn data block
    mkfile.write('\begindata')
    #write path values
    mkfile.write('PATH_VALUES = '+ '('+path_vals+')')
    #write KERNELS TO LOAD
    mkfile.write('KERNELS_TO_LOAD = '+'('+kernels+')')
    #enddata block
    mkfile.write('\begintext')
    #say goodbye
    mkfile.close()
    
def kernelDescriptions(kernels, mission):
    kernelDscr = ''
    for kernel in kernels:
        if kernel is '*.tls':
            kernelDscr = mission+' LSK'
        elif kernel is '*.bsp' or kernel is '*.xsp' or kernel is '*.tsp':
            kernelDscr = mission+' Ephemeris SPK'
        elif kernel is '*.tsc':
            kernelDscr = mission+' SCLK'
        elif kernel is '*.tpc':
            kernelDscr = mission+' PCK'
    return kernelDscr

    