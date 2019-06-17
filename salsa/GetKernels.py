import spiceypy as spice
import numpy as py
import pandas as pd
import ftplib
from ftplib import FTP
import os
from salsa import *
from posix import mkdir
import shutil
from shutil import rmtree

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
        
    elif target is 'phoebe' or target is 'Phoebe':
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
    ftp.cwd(mission+'/')
    
    #go to kernels directory
    ftp.cwd('kernels/')
    
    #set kernel folder name
    kernel_dir = 'kernels_to_load'
    
    #check if kernel folder exists already, if not - create it
    if not os.path.exists(kernel_dir):
        mkdir('kernels_to_load')
    else: #if so - delete and create it
        shutil.rmtree(os.path.abspath(kernel_dir))
        mkdir('kernels_to_load')
    
    #use os to get local path
    kernel_path = os.path.abspath(kernel_dir)
    
    def append_newline(input):
        file.write(input + "\n")

    #find needed kernels based on function calling for them
    if functionName is 'UTC2ET':
        #go into lsk directory
        ftp.cwd('lsk/')
        #get kernel filenames in directory
        files = ftp.nlst()
        #get path values
        path_vals = 'kernels/lsk'
        #open local file -- need to use os for an individualized path name 
        file = open(kernel_path+'/leapseconds.tls','w')
        #write kernel to local file
        ftp.retrlines('RETR '+files[2], append_newline)
        #get kernel filenames 
        kernels = files[2]
        #set metakernel filename
        filename = 'utc2et_mk.tm'
        #load the kernels from here into metakernel
        writeMetaKernel(path_vals, kernels, filename, mission)
        
#     elif functionName is 'SCLK2ET':
#         ftp.cwd('LSK')
#         path_vals = "'kernels/lsk', 'kernels/sclk'"
#         #get kernel filenames
#         kernels = ftp.retrlines('RETR filename')
#         print(kernels)
#         #back out of LSK directory and go into sclk directory
#         ftp.cwd('cd ..')
#         ftp.cwd('SCLK')
#         #get kernel filenames
#         kernels = kernels+ftp.retrlines('RETR filename')
#         filename = 'sclk2et_mk.tm'
#         #load the kernels from here into metakernel
#         writeMetaKernel(path_vals, kernels, filename, mission)
        
    return kernels
    #say goodbye
    ftp.quit()
    
def writeMetaKernel(path_vals, kernels, filename, mission):
    #open file according to functionName
    mode = 'w'
    mkfile = open(filename, mode)
    #write header
    mkfile.write('\\begintext\n\n')
    mkfile.write('The names and contents of the kernels referenced by this meta-kernel are as follows:\n')
    #get descriptions of kernels for meta kernel
    kernelDscr = kernelDescriptions(kernels, mission)
    #Write kernel descriptions
    mkfile.write('FILE NAME'+"    "+"CONTENTS\n")
    mkfile.write(kernels+ "    "+kernelDscr+'\n\n')
    #oepn data block
    mkfile.write('\\begindata \n\n')
    #write path values
    mkfile.write('PATH_VALUES = (\n')
    mkfile.write('\'{0}\'\n'.format(path_vals))
    mkfile.write(')\n\n')
    #write KERNELS TO LOAD
    mkfile.write('KERNELS_TO_LOAD = (\n')
    mkfile.write('\'{0}\'\n'.format(kernels))
    mkfile.write(')\n\n')
    
    return(filename)
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

    