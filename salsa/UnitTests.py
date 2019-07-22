'''AUTHOR: Emma Lieb

    All tests use Saturnian satellite Pheobe as an example and UTC time 2004-06-11T19:32:00
'''
import os
import unittest

from salsa.TimeConversions import *
from salsa.GetKernels import *
from salsa.DataQuery import *
from salsa.SpectralCalibration import *

class DataQueryTest(unittest.TestCase):
    def test_getURL(self):
        primaryParameter = 'irradiance'
        secondaryParameter = 'wavelength'
        tertiaryParameter = 'NONE'
        dataset = 'NONE'
        wavelengthLow = '180'
        wavelengthHigh = '300'
        timeLow = '2010-03-20'
        timeHigh = '2010-03-24'
        self.assertAlmostEqual(getURL(primaryParameter, secondaryParameter, tertiaryParameter, dataset, wavelengthLow, wavelengthHigh, timeLow, timeHigh), 0.00)
# 
        
class GetKernelsTest(unittest.TestCase):
    def test_getMissionFromTarget(self):
        target = 'Phoebe'
        self.assertEqual(getMissionFromTarget(target), "CASSINI")
    def test_getKernels(self):
#         import cProfile, pstats, io
#         from pstats import SortKey
#         pr = cProfile.Profile()
#         pr.enable()
        time = '2004-06-11T19:32:00'
        target = 'Phoebe'
        functionName = 'getVelocityVectorOfSpaceCraft'
        getKernels('CASSINI', functionName, time)
           
#         pr.disable()
#         s = io.StringIO()
#         sortby = SortKey.CUMULATIVE
#         ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#         ps.print_stats()
#         print(s.getvalue()) 
        
    def test_writeMetaKernel(self):
        dir = '../../SALSA/test_kernels/'
        path_vals = 'kernels/LSK/'
        kernels = ['naif0008.tls', 'cas00172.tsc']
        filename = dir+'test_writingmk.tm'
        target = 'Phoebe'
        mission = getMissionFromTarget(target)
            
        file = writeMetaKernel(path_vals, kernels, filename, mission)
        read_mktestfile = open(file,'r')
        comp_timemktestfile = open(dir+'time_mktest.tm','r')
            
        first = read_mktestfile.read()
        second = comp_timemktestfile.read()
    
        print(first)
        self.assertMultiLineEqual(first, second)
        
class TimeConvertsTest(unittest.TestCase):
    def test_UTC2time(self):
        time = '2004-06-11T19:32:00'
        target = 'Phoebe'
        result = 140254384.184625
        self.assertAlmostEqual(UTC2ET(time, target), result, 4)
              
#     def test_SCLK2time(self):
#         timeStr = '1465674964.105'
#         target = 'Phoebe'
#         result = 140254384.183426
#         self.assertAlmostEqual(SCLK2ET(timeStr, target), result, 4)
            
    def test_time2Date(self):
        time = 140254384.184625
        target = 'Phoebe'
        ET = UTC2ET(time, target)
        self.assertAlmostEqual(ET2Date(ET), '2004 JUN 11 19:33:04.184')
            
    def test_UTC2SPKKernelDate(self):
        time = '2004-06-11T19:32:00'
        self.assertEqual(UTC2SPKKernelDate(time), '040611')
           
    def test_UTC2CKKernelDate(self):
        time = '2004-06-11T19:32:00'
        self.assertEqual(UTC2CKKernelDate(time), '04163')
           
    def test_UTC2PCKKernelDate(self):
        time = '2004-06-11T19:32:00'
        self.assertEqual(UTC2PCKKernelDate(time), '11Jun2004')
        
class GeometryAndTimeCnvtTest(unittest.TestCase):
       
    def test_getVectorFromSpaceCraftToTarget(self):
        time = '2004-06-11T19:32:00'
        target = 'Phoebe'
        comp_vector = np.array([ -376599061.916539, 1294487780.929154, -7064853.054698])
        self.assertAlmostEqual(getVectorFromSpaceCraftToTarget(time, target).all(), comp_vector.all(), 4)
           
    def test_getVectorFromCraftToSun(self):
        time = '2004-06-11T19:32:00'
        target = 'Phoebe'
        pos_vector = getVectorFromSpaceCraftToTarget(time, target)
        comp_vector = np.array([-0.290204, 0.881631, 0.372167])
        self.assertAlmostEqual(getVectorFromSpaceCraftToSun(time, target, pos_vector).all(), comp_vector.all(), 4)
           
    def test_getTargetSunDistance(self):
        time = '2004-06-11T19:32:00'
        target = 'Phoebe'
        pos_vector = getVectorFromSpaceCraftToTarget(time, target)
        sunDir_vector = getVectorFromSpaceCraftToSun(time, target, pos_vector)
        distance_vector = sunDir_vector+pos_vector
        distance = 9.4769 #Astronomical Units
           
        self.assertAlmostEqual(getTargetSunDistance(distance_vector), distance, 4)
           
    def test_getAngularSeparation(self):
        time = '2004-06-11T19:32:00'
        target = 'Phoebe'
        pos_vector = getVectorFromSpaceCraftToTarget(time, target)
        sunDir_vector = getVectorFromSpaceCraftToSun(time, target,pos_vector)
        distance_vector = pos_vector + sunDir_vector
        comp_val = 71.924
        self.assertAlmostEqual(getAngularSeparation(time, target, distance_vector), comp_val, 4)

 
class SpectralCalibrationTest(unittest.TestCase):     
        
    def test_SolarSpectraCalibration(self):
        target = 'Saturn'
        time = '2004-06-11T19:32:00'
          
        pos_vector = getVectorFromSpaceCraftToTarget(time, target)
          
        sunDir_vector = getVectorFromSpaceCraftToSun(time, target, pos_vector) 
        distance_vector = sunDir_vector+pos_vector
        
        ang_sep = getAngularSeparation(time, target, distance_vector)
        solar_flux, wavelengths = sunFaceCorrection(ang_sep, time)
          
        distance = getTargetSunDistance(distance_vector)
        print(distance)
        spectra_at_target = getFluxAtTarget(solar_flux, wavelengths, distance)
        plotBeforeAfterDistCorr(solar_flux, wavelengths, spectra_at_target)
        
        convolved_spectrum = getConvolvedSolarSpectrum(spectra_at_target, wavelengths,target)
        
        filename = 'FUV2005_247_20_15.fits'
        plotConvolvedSpectrum(spectra_at_target,convolved_spectrum, wavelengths)
        data, wavelenths_ob = getPlanetaryData(filename, convolved_spectrum, wavelengths)
        
     
    def test_sunFaceCorrection(self):

        target = 'Phoebe'
        time = '2004-06-11T19:32:00'
        
        pos_vector = getVectorFromSpaceCraftToTarget(time, target)
        sunDir_vector = getVectorFromSpaceCraftToSun(time, target, pos_vector)
        distance_vector = sunDir_vector+pos_vector
        
        print("Distance vector between Sun and Target (km) :")
        print(distance_vector)
        
        ang_sep = getAngularSeparation(time, target, distance_vector)

        solar_flux = sunFaceCorrection(ang_sep,time)
        
       
if __name__ == '__main__':
    unittest.main()
        