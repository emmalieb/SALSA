""" 
    Author: Emma Lieb
    
    This method gets the kernels needed for a given operations in the order they are called by the overall program and returns a meta-kernel of them. 

"""
from PyQt5.Qt import QGeoSatelliteInfo
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
        
    elif target is 'Mars' or target is 'Phobos' or target is 'Desmos':
        mission = 'MAVEN'
    
    elif target is 'Jupiter' or target is 'Europa' or target is 'Io' or target is 'Ganymede' or target is 'Callisto':
        mission = 'JUNO'
    
    elif target is 'saturn' or target is 'Saturn' or target is 'Phoebe' or target is 'Mimas' or target is 'Tethys' or target is 'Titan' or target is "Dione" or target is "Hyperion" or target is "Enceladus":
        mission = 'CASSINI'
        
    elif target is 'pluto' or target is 'Pluto' or target is 'Charon':
        mission = 'NEWHORIZONS'

    elif target is 'moon' or target is'Moon':
        mission = 'LUNARORBITER'
    
    return mission

def classifyTarget(target):
    if target is 'Phobos' or target is 'Desmos' or target is 'Europa' or target is 'Io' or target is 'Ganymede' or target is 'Callisto' or target is 'Charon':
        obtype = 'satellites'
    elif target is 'Phoebe' or target is 'Mimas' or target is 'Tethys' or target is 'Titan' or target is "Dione" or target is "Hyperion" or target is "Enceladus":
        obtype = "satellites"
    elif target is 'Mercury' or target is 'Venus' or target is 'Jupiter' or target is 'Saturn' or target is 'Neptune' or target is 'Uranus' or target is 'Pluto':
        obtype = 'planets'
    return obtype

'''Function to get mission name from target object name 
    Parameters:  
    target - user input
    functionName - passed in from functions that require the kernels
'''
def getKernels(mission, target, functionName, time):
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
        metaKernel = writeMetaKernel( kernels, filename, mission)
         
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
            #write kernel to local file
            ftp.retrlines('RETR '+lsk_kernel, append_newline)
            #get kernel filenames 
            kernels.append(lsk_kernel)
        else: #if so - add it
            #get kernel filenames 
            kernels.append(lsk_kernel)
        #add lsk to path values for metakernel
        path_vals.append('kernels/lsk')
        #get kernel filenames 
        kernels.append(lsk_kernel)
        
        obtype = classifyTarget(target)
        #back out of spk/kernels/mission folder
        ftp.cwd('../../../')
        #go into 'generic kernels' folder for spk kernels
        ftp.cwd('generic_kernels/spk/'+obtype+'/')
        #get file list
        files = ftp.nlst()
        #get generic spk kernel
        generic_spk = getGenericKernels(files)
        #check if kernel exists already, if not - create it
        if not os.path.exists(generic_spk):
            #open local file -- need to use os for an individualized path name
            file = open(generic_spk,'wb')
            #write kernel to local file
            ftp.retrbinary('RETR ' +generic_spk, file.write)
            #get generic planetary and solar system kernels    
            kernels.append(generic_spk)
        else: #if so - add it
            kernels.append(generic_spk)
        #go back a directory
        ftp.cwd('../')
#REALLY NEED TO WRITE SOME IF STATEMENTS BASED ON WHAT THE TARGET IS - MAYBE 'classifyTarget' function
        ftp.cwd(obtype+'/')
        files = ftp.nlst()
        if obtype is 'satellites':
            satellite_spk = getSatelliteKernels(files, mission)
            #loop through kernels
            for spk in satellite_spk:
                path_vals.append('kernels/spk')
                #check if kernel exists already, if not - create it
                if not os.path.exists(spk):
                    #open local file -- need to use os for an individualized path name
                    file = open(spk,'wb')
                    #write kernel to local file
                    ftp.retrbinary('RETR ' +spk, file.write)
                    kernels.append(spk)
                else: #if so - add it
                    kernels.append(spk)
        #back out of leapseconds directory
        ftp.cwd('../../../')
        #go into SPK directory
        ftp.cwd(mission+'/kernels/spk/')
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
                #write kernel to local file
                ftp.retrbinary('RETR ' +spk_kernel, file.write)
                kernels.append(spk_kernel)
            else: #if so - add it
                kernels.append(spk_kernel)
        #go back one directory
        ftp.cwd('../')
        #go  into pck directory
        ftp.cwd('pck/')
        #get files
        files = ftp.nlst()
        #get pck kernels 
        pck_kernel = getPCK(files, time, target)
        #check if kernel exists already, if not - create it
        if not os.path.exists(pck_kernel):
            #open local file -- need to use os for an individualized path name
            file = open(pck_kernel,'w')
            #write kernel to local file
            ftp.retrlines('RETR ' +pck_kernel, append_newline)
            #back out of spk/kernels/mission folder
            kernels.append(pck_kernel)
        else: #if so - add it
            kernels.append(pck_kernel)

        #filename depends on function
        filename = 'vectorGeometry_mk.tm'
        #load the kernels from here into metakernel
        metaKernel = writeMetaKernel( kernels, filename, mission)
        
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
            #write kernel to local file
            ftp.retrlines('RETR '+lsk_kernel, append_newline)
            #add lsk to path values for metakernel
            path_vals.append('kernels/lsk')
            #get kernel filenames 
            kernels.append(lsk_kernel)
        else: #if so -add it
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
            #write kernel over to local file
            ftp.retrlines('RETR ' +sclk_kernel, append_newline)
            #add this kernel to kernels list for meta kernel
            kernels.append(sclk_kernel)
        else: #if so -
            #add this kernel to kernels list for meta kernel
            kernels.append(sclk_kernel)
        
        obtype = classifyTarget(target)
        #back out of spk/kernels/mission folder
        ftp.cwd('../../../')
        #go into 'generic kernels' folder for spk kernels
        ftp.cwd('generic_kernels/spk/'+obtype+'/')
        #get file list
        files = ftp.nlst()
        #get generic spk kernel
        generic_spk = getGenericKernels(files)
        #check if kernel exists already, if not - create it
        if not os.path.exists(generic_spk):
            #open local file -- need to use os for an individualized path name
            file = open(generic_spk,'wb')
            #write kernel to local file
            ftp.retrbinary('RETR ' +generic_spk, file.write)
            #get generic planetary and solar system kernels    
            kernels.append(generic_spk)
        else: #if so - add it
            kernels.append(generic_spk)
        #go back a directory
        ftp.cwd('../')
#REALLY NEED TO WRITE SOME IF STATEMENTS BASED ON WHAT THE TARGET IS - MAYBE 'classifyTarget' function
        ftp.cwd(obtype+'/')
        files = ftp.nlst()
        if obtype is 'satellites':
            satellite_spk = getSatelliteKernels(files, mission)
            #loop through kernels
            for spk in satellite_spk:
                path_vals.append('kernels/spk')
                #check if kernel exists already, if not - create it
                if not os.path.exists(spk):
                    #open local file -- need to use os for an individualized path name
                    file = open(spk,'wb')
                    #write kernel to local file
                    ftp.retrbinary('RETR ' +spk, file.write)
                    kernels.append(spk)
                else: #if so - add it
                    kernels.append(spk)
        #back out of leapseconds directory
        ftp.cwd('../../../')
        #go into SPK directory
        ftp.cwd(mission+'/kernels/spk/')
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
                #write kernel to local file
                ftp.retrbinary('RETR ' +spk_kernel, file.write)
                kernels.append(spk_kernel)
            else: #if so - add it
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
            #write kernel to local file
            ftp.retrbinary('RETR ' +ck_kernel, file.write)
            kernels.append(ck_kernel)
        else: #if so - add it
            kernels.append(ck_kernel)
        #go back a directory 
        ftp.cwd('../')
        #go into SPK directory
        ftp.cwd('fk/')
        #get kernel filenames in directory
        files = ftp.nlst()
        #call get spk function with files -- THIS IS JUST THE SPACECRAFT SPK
        fk_kernel = getFK(files, mission)
        #loop through spacecraft spk kernels
        path_vals.append('kernels/fk')
        #check if kernel exists already, if not - create it
        if not os.path.exists(fk_kernel):
            #open local file -- need to use os for an individualized path name
            file = open(fk_kernel,'w')
            #write kernel to local file
            ftp.retrlines('RETR ' +fk_kernel, append_newline)
            kernels.append(fk_kernel)
        else: #if so - delete and create it
            kernels.append(fk_kernel)
        #go back one directory
        ftp.cwd('../')
        #go  into pck directory
        ftp.cwd('pck/')
        #get files
        files = ftp.nlst()
        #get pck kernels 
        pck_kernel = getPCK(files, time,target)
        #check if kernel exists already, if not - create it
        if not os.path.exists(pck_kernel):
            #open local file -- need to use os for an individualized path name
            file = open(pck_kernel,'w')
            #write kernel to local file
            ftp.retrlines('RETR ' +pck_kernel, append_newline)
            kernels.append(pck_kernel)
        else: #if so - add it
            kernels.append(pck_kernel)
        #set filename
        filename = 'complexGeometry_mk.tm'
        #load the kernels from here into metakernel
        metaKernel = writeMetaKernel( kernels, filename, mission)
    
    #say goodbye
    ftp.quit()
    return metaKernel

'''Function to get SPK kernels
    SPK are ephemeris 
'''  
def getSPK(files, time):
    
    from salsa.TimeConversions import UTC2SPKKernelDate
    kernels = []
    kernel_dates = []
    #change UTC string to SPK date
    date = UTC2SPKKernelDate(time) #YYDOY
    #loop through files
    for file in files:
        #these indices are the dates
        file_list = file.split('_')
        if len(file_list)>2:
            if file_list[2].isdigit():
                kernel_dates.append(file_list[2])
            else:
                continue
        else:
            continue
    numbers = [int(x) for x in kernel_dates]
    #find closest date string to given date string        
    nearest_date = min(numbers, key=lambda x: abs(x - int(date)))
    for file in files:
        if str(nearest_date) in file and file.endswith('.bsp'):
                #format string into datetime object to check for nearest date
                kernels.append(file)
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
def getFK(files, mission):
    kernel = ''
    #loop through files 
    for file in files:
        if mission is 'CASSINI':
            #find the correct kernel
            if 'cas_v41.tf' in file:
                kernel = file
    return kernel
# '''Function to get PCK kernels''' #TO DO: THERE ARE DIFFERENT PCK TYPES (spacecraft, and target) - MUST BE CALLED SEPARATELY FROM GET KERNELS 
def getPCK(files, time, target):
    from bisect import bisect
    from salsa.TimeConversions import UTC2PCKKernelDate
    file_dates = []
    file_list = []
    date = datetime.strptime(time,'%Y-%m-%dT%H:%M:%S')
    #loop through files 
    for file in files:
        if file.startswith('cpck') and not file.startswith('cpck_rock'):
            #find the kernel dates
            file_date = file[4:13]
            kernel_date = datetime.strptime(file_date,'%d%b%Y')
            file_dates.append(kernel_date)
            file_list.append(file)
    #sort lists       
    file_dates.sort()
    file_list.sort()
    
    ind = bisect(file_dates, date, hi=len(file_dates)-1)
    nearest = min(file_dates[ind], file_dates[ind-1],key=lambda x: abs(x - date))

    nearest_date = UTC2PCKKernelDate(str(nearest), target)
    for file in file_list:
        if nearest_date in file:
            kernel = file
    
    return kernel

def getGenericKernels(files):
    for file in files:
        if 'de430.bsp' in file:
            kernel = file
    return kernel

def getSatelliteKernels(files,mission):
    kernels =[]
    for file in files:
        if mission is 'CASSINI' and file.startswith('sat') and file.endswith('.bsp'):
            kernels.append(file)
        if mission is 'MAVEN' and file.startswith('mar') and file.endswith('.bsp'):
            kernels.append(file)
        if mission is 'JUNO' and file.startswith('jup') and file.endswith('.bsp'):
            kernels.append(file)
        #TO DO - MAKE THIS MORE ROBUST FOR MORE PLANETS' MOONS
    return kernels
'''Function to construct and write a metakernel file from the kernels needed for each function
Parameters: 
    path_vals - obtype of kernel passed in from getKernels
    kernels - filenames of kernels needed to be loaded passed in from getKernels
    filename - name for the metakernel file passed in from getKernels
    mission - mission passed in from getKernels, gotten from target name
'''
def writeMetaKernel( kernels, filename, mission):
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
#     #write path values
#     mkfile.write('PATH_VALUES = (\n')
#     for val in path_vals:    
#         mkfile.write('\'{0}\'\n'.format(val))
#     mkfile.write(')\n\n')
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
    elif kernel.endswith('.bsp'):
        kernelDscr = mission+' Ephemeris SPK'
    elif kernel.startswith('sat'):
        kernelDscr = 'Target Epehemeris SPK'
    elif kernel.endswith('.tf'):
        kernelDscr = mission+' FK'
    elif kernel.endswith('.tpc'):
        kernelDscr = mission+' PCK'
    elif kernel.endswith('.bc'):
        kernelDscr = mission+' CK'
    return kernelDscr


    