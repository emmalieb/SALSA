""" 
    Author: Emma Lieb
    
    This method gets the kernels needed for a given operations in the order they are called by the overall program and returns a meta-kernel of them. 

"""
'''Function to get mission name from target object name 
    Parameters:  
    target - user input
'''
import ftplib
from ftplib import FTP
import os
from posix import mkdir
import shutil
from shutil import rmtree

from astropy.io.ascii.tests.test_connect import files

from salsa import *
import spiceypy as spice
from datetime import datetime


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
def getKernels(mission, functionName, time):
    #open ftp connection
    ftp = ftplib.FTP('naif.jpl.nasa.gov')
    ftp.login()
    #go into NAIF directory
    ftp.cwd('/pub/naif/')
    #go into mission director
    ftp.cwd(mission+'/')
    #go to kernels directory
    ftp.cwd('kernels/')

    #for formatting kernels correctly in local file - only for text kernels 
    def append_newline(input):
        file.write(input + "\n")
        
    if functionName is 'SCLK2ET' or functionName is 'UTC2ET':
        #create kernels list
        kernels = []
        #go into lsk directory first
        ftp.cwd('lsk/')
        #get kernel filenames in directory
        files = ftp.nlst()
        #get path values
        path_vals = 'kernels/lsk', 'kernels/sclk'
        lsk_kernel = files[2]
        #check if kernel exists already, if not - create it
        if not os.path.exists(lsk_kernel):
            #open local file -- need to use os for an individualized path name
            file = open(lsk_kernel,'w')
        else: #if so - delete and create it
            os.remove(lsk_kernel)
            file = open(lsk_kernel,'w')
        #write kernel to local file
        ftp.retrlines('RETR '+files[2], append_newline)
        #get kernel filenames 
        leap_kernel = files[2]
        #back out of lsk directory
        ftp.cwd('../')
        #go into sclk directory
        ftp.cwd('sclk/')
        #get kernel filenames in directory
        files = ftp.nlst()
        #sclk kernels are named for version so this uses last one in directory
        sclk_kernel = files[-1]
        #check if kernel exists already, if not - create it
        if not os.path.exists(sclk_kernel):
            #open local file -- need to use os for an individualized path name
            file = open(sclk_kernel,'w')
        else: #if so - delete and create it
            os.remove(sclk_kernel)
            file = open(sclk_kernel,'w')
        #get kernel filenames
        ftp.retrlines('RETR ' +sclk_kernel, append_newline)
        kernels = [leap_kernel,sclk_kernel]
        #set filename for metakernel
        if functionName is 'SCLK2ET':
            filename = 'sclk2et_mk.tm'
        elif functionName is 'UTC2ET':
            filename = 'utc2et_mk.tm'
        #load the kernels from here into metakernel
        metaKernel = writeMetaKernel(path_vals, kernels, filename, mission)
         
    elif functionName is 'getVectorFromSpaceCraftToTarget' or functionName is 'getVectorFromSpaceCraftToSun':
        #create kernels list
        kernels = []
        #get path values
        path_vals = []
        #go into lsk directory first
        ftp.cwd('lsk/')
        #get kernel filenames in directory
        files = ftp.nlst()
        #set kernel name
        lsk_kernel = files[2]
        #check if kernel exists already, if not - create it
        if not os.path.exists(lsk_kernel):
            #open local file -- need to use os for an individualized path name
            file = open(lsk_kernel,'w')
        else: #if so - delete and create it
            os.remove(lsk_kernel)
            file = open(lsk_kernel,'w')
        #write kernel to local file
        ftp.retrlines('RETR '+lsk_kernel, append_newline)
        #add lsk to path values for metakernel
        path_vals.append('kernels/lsk')
        #get kernel filenames 
        kernels.append(lsk_kernel)
        #back out of leapseconds directory
        ftp.cwd('../')
        #go into SPK directory
        ftp.cwd('spk/')
        #get kernel filenames in directory
        files = ftp.nlst()
        #call get spk function with files -- THIS IS JUST THE SPACECRAFT SPK
        spk_kernels = getSPK(files, time)
        #loop through spacecraft spk kernels
        for spk_kernel in spk_kernels:
            path_vals.append('kernels/spk')
            #check if kernel exists already, if not - create it
            if not os.path.exists(spk_kernel):
                #open local file -- need to use os for an individualized path name
                file = open(spk_kernel,'wb')
            else: #if so - delete and create it
                os.remove(spk_kernel)
                file = open(spk_kernel,'wb')
            #write kernel to local file
            ftp.retrbinary('RETR ' +spk_kernel, file.write)
            kernels.append(spk_kernel)
        #back out of spk/kernels/mission folder
        ftp.cwd('../../../')
        #go into 'generic kernels' folder for spk kernels
        ftp.cwd('generic_kernels/spk/planets/')
        #get file list
        files = ftp.nlst()
        #get generic spk kernel
        generic_spk = getGenericKernels(files)
        #check if kernel exists already, if not - create it
        if not os.path.exists(generic_spk):
            #open local file -- need to use os for an individualized path name
            file = open(generic_spk,'wb')
        else: #if so - delete and create it
            os.remove(generic_spk)
            file = open(generic_spk,'wb')
        #write kernel to local file
        ftp.retrbinary('RETR ' +generic_spk, file.write)
        #get generic planetary and solar system kernels    
        kernels.append(generic_spk)
        #filename depends on function - check function name
        if functionName is 'getVectorFromSpaceCraftToTarget':
            #set filename for metakernel
            filename = 'targetCraftVector_mk.tm'
        elif functionName is 'getVectorFromSpaceCraftToSun':
            #set filename for metakernel
            filename = 'craftSunVector_mk.tm'
        #load the kernels from here into metakernel
        metaKernel = writeMetaKernel(path_vals, kernels, filename, mission)
        
    elif functionName is 'getVelocityVectorOfSpaceCraft' or functionName is 'getSubCraftVector' or functionName is 'getSubSolarVector' or functionName is 'getAngularSeparation':
        #create kernels list
        kernels = []
        #get path values
        path_vals = []
        #go into lsk directory first
        ftp.cwd('lsk/')
        #get kernel filenames in directory
        files = ftp.nlst()
        #set kernel name
        lsk_kernel = files[2]
        #check if kernel exists already, if not - create it
        if not os.path.exists(lsk_kernel):
            #open local file -- need to use os for an individualized path name
            file = open(lsk_kernel,'w')
        else: #if so - delete and create it
            os.remove(lsk_kernel)
            file = open(lsk_kernel,'w')
        #write kernel to local file
        ftp.retrlines('RETR '+leap_kernel, append_newline)
        #add lsk to path values for metakernel
        path_vals.append('kernels/lsk')
        #get kernel filenames 
        kernels.append(lsk_kernel)
        #back out of lsk directory
        ftp.cwd('../')
        #go into sclk directory
        ftp.cwd('sclk/')
        #get kernel filenames in directory
        files = ftp.nlst()
        path_vals.append('kernels.sclk')
        #set next kernel name
        sclk_kernel = files[-1]
        #sclk kernels are named for version so this uses last one in directory
        kernels.append(sclk_kernel)
        #check if kernel exists already, if not - create it
        if not os.path.exists(sclk_kernel):
            #open local file -- need to use os for an individualized path name
            file = open(sclk_kernel,'w')
        else: #if so - delete and create it
            os.remove(sclk_kernel)
            file = open(sclk_kernel,'w')
        #write kernel over to local file
        ftp.retrlines('RETR ' +sclk_kernel, append_newline)
        #add this kenrel to kernels list for meta kernel
        kernels = [leap_kernel, sclk_kernel]
        #go back a directory 
        ftp.cwd('../')
        #go into SPK directory
        ftp.cwd('spk/')
        #get kernel filenames in directory
        files = ftp.nlst()
        #call get spk function with files -- THIS IS JUST THE SPACECRAFT SPK
        spk_kernels = getSPK(files, time)
        #loop through spacecraft spk kernels
        for spk_kernel in spk_kernels:
            path_vals.append('kernels/spk')
            #check if kernel exists already, if not - create it
            if not os.path.exists(spk_kernel):
                #open local file -- need to use os for an individualized path name
                file = open(spk_kernel,'wb')
            else: #if so - delete and create it
                os.remove(spk_kernel)
                file = open(spk_kernel,'wb')
            #write kernel to local file
            ftp.retrbinary('RETR ' +spk_kernel, file.write)
            kernels.append(spk_kernel)
        #go back a directory 
        ftp.cwd('../')
        #go into SPK directory
        ftp.cwd('ck/')
        #get kernel filenames in directory
        files = ftp.nlst()
        #call get spk function with files -- THIS IS JUST THE SPACECRAFT SPK
        ck_kernel = getCK(files, time)
        #loop through spacecraft spk kernels
        path_vals.append('kernels/ck')
        #check if kernel exists already, if not - create it
        if not os.path.exists(ck_kernel):
            #open local file -- need to use os for an individualized path name
            file = open(ck_kernel,'wb')
        else: #if so - delete and create it
            os.remove(ck_kernel)
            file = open(ck_kernel,'wb')
        #write kernel to local file
        ftp.retrbinary('RETR ' +ck_kernel, file.write)
        kernels.append(ck_kernel)
        #go back a directory 
        ftp.cwd('../')
        #go into SPK directory
        ftp.cwd('fk/')
        #get kernel filenames in directory
        files = ftp.nlst()
        #call get spk function with files -- THIS IS JUST THE SPACECRAFT SPK
        fk_kernel = getFK(files)
        #loop through spacecraft spk kernels
        path_vals.append('kernels/fk')
        #check if kernel exists already, if not - create it
        if not os.path.exists(fk_kernel):
            #open local file -- need to use os for an individualized path name
            file = open(fk_kernel,'wb')
        else: #if so - delete and create it
            os.remove(fk_kernel)
            file = open(fk_kernel,'wb')
        #write kernel to local file
        ftp.retrbinary('RETR ' +fk_kernel, file.write)
        kernels.append(fk_kernel)
        #back out of spk/kernels/mission folder
        ftp.cwd('../../../')
        #go into 'generic kernels' folder for spk kernels
        ftp.cwd('generic_kernels/spk/planets/')
        #get file list
        files = ftp.nlst()
        #get generic spk kernel
        generic_spk = getGenericKernels(files)
        #check if kernel exists already, if not - create it
        if not os.path.exists(generic_spk):
            #open local file -- need to use os for an individualized path name
            file = open(generic_spk,'wb')
        else: #if so - delete and create it
            os.remove(generic_spk)
            file = open(generic_spk,'wb')
        #write kernel to local file
        ftp.retrbinary('RETR ' +generic_spk, file.write)
        #get generic planetary and solar system kernels    
        kernels.append(generic_spk)

        #filename depends on function - check function name
        if functionName is 'getVelocityVectorOfSpaceCraft':
            #set filename for metakernel
            filename = 'craftVelocity_mk.tm'
        elif functionName is 'getSubCraftVector':
            #set filename for metakernel
            filename = 'subCraft_mk.tm'
        elif functionName is 'getSubSolarVector':
            #set filename for metakernel
            filename = 'subSolar_mk.tm'
        elif functionName is 'getAnuglarSeparation':
            #set filename for metakernel
            filename = 'aungularSep_mk.tm'
        #load the kernels from here into metakernel
        metaKernel = writeMetaKernel(path_vals, kernels, filename, mission)
    
                
    return metaKernel
    #say goodbye
    ftp.quit()

'''Function to get SPK kernels
    SPK are ephemeris 
'''  
def getSPK(files, time):
    
    from salsa.TimeConversions import UTC2SPKKernelDate
    kernels = []
    file_dates = []
    #change UTC string to SPK date
    date = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
    #loop through files
    for file in files:
        #these indices are the dates
        file_date = file[0:6]
        #check if the date is a date - some files have weird strings instead of dates
        if file_date.isdigit():
            #format string into datetime object to check for nearest date
            file_dates.append(datetime.strptime(file_date, '%y%m%d'))
    #find closest date string to given date string        
    nearest_date = min(file_dates, key=lambda x: abs(x - date))
    #convert to kernel date format for finding filename 
    nearest_date = UTC2SPKKernelDate(str(nearest_date))
    #create array for more than one kernel of the same date
    nearest_dates = []
    #loop through files again to find files with nearest date 
    for file in files:
        #check if the date is in the file
        if nearest_date in file:
            #if so, add it to the array for kernel filenames 
            nearest_dates.append(file)
    #convert to kernel date format for finding filename
    date = UTC2SPKKernelDate(time)
    for nearest_date in nearest_dates:
        #find correct kernel dated file 
        if nearest_date.endswith('.bsp'):
            #set kernel to that file
            kernels.append(nearest_date)
    return(kernels)

'''Function to get CK kernels
    CK are spacecraft orientation
'''
def getCK(files, time):
    
    from salsa.TimeConversions import UTC2CKKernelDate
    kernel=''
    #change UTC time to CK date
    date = UTC2CKKernelDate(time)
    #loop through files 
    for file in files:
        #find the correct kernel
        if date in file and file.endswith('.bc'):
            kernel = file
    return kernel
'''Function to get FK kernels
    FK are spacecraft reference frames
'''
def getFK(files):
    kernel = ''
    #loop through files 
    for file in files:
        #find the correct kernel
        if 'cas_v41.tf' in file:
            kernel = file
    return kernel
# '''Function to get PCK kernels''' #TO DO: THERE ARE DIFFERENT PCK TYPES (spacecraft, and target) - MUST BE CALLED SEPARATELY FROM GET KERNELS 
def getPCK(files, time, target):
    
    from salsa.TimeConversions import UTC2PCKKernelDate
    kernel =''
    date = UTC2PCKKernelDate(time, target)
    #loop through files 
    for file in files:
        #find the correct kernel
        if date in file:
            kernel = file
    return kernel
def getGenericKernels(files):
    for file in files:
        if 'de430.bsp' in file:
            kernel = file
    return kernel
'''Function to construct and write a metakernel file from the kernels needed for each function
Parameters: 
    path_vals - type of kernel passed in from getKernels
    kernels - filenames of kernels needed to be loaded passed in from getKernels
    filename - name for the metakernel file passed in from getKernels
    mission - mission passed in from getKernels, gotten from target name
'''
def writeMetaKernel(path_vals, kernels, filename, mission):
    #open file according to functionName
    mode = 'w'
    mkfile = open(filename, mode)
    #write header
    mkfile.write('\\begintext\n\n')
    mkfile.write('The names and contents of the kernels referenced by this meta-kernel are as follows:\n')
    #Write kernel descriptions
    mkfile.write('FILE NAME'+"        "+"CONTENTS\n")
    for kernel in kernels:
        #get descriptions of kernels for meta kernel
        kernelDscr = kernelDescriptions(kernel, mission)
        mkfile.write(kernel+ "    "+kernelDscr+'\n')
    #open data block
    mkfile.write('\\begindata \n\n')
    #write path values
    mkfile.write('PATH_VALUES = (\n')
    for val in path_vals:    
        mkfile.write('\'{0}\'\n'.format(val))
    mkfile.write(')\n\n')
    #write KERNELS TO LOAD
    mkfile.write('KERNELS_TO_LOAD = (\n')
    for kernel in kernels:
        mkfile.write('\'{0}\'\n'.format(kernel))
    mkfile.write(')\n\n')
        
    return(filename)
    #say goodbye
    mkfile.close()
    
'''Function to describe kernels by their type to be written into metakernel for readability'''
def kernelDescriptions(kernel, mission):
    kernelDscr = ''

    if kernel == 'naif0008.tls':
        kernelDscr = 'Generic LSK'
    elif kernel.endswith('.tsc'):
        kernelDscr = mission+' Ephemeris SPK'
    elif kernel == '*.tsc':
        kernelDscr = mission+' SCLK'
    elif kernel == '*.tpc':
        kernelDscr = mission+' PCK'
        
    return kernelDscr


    