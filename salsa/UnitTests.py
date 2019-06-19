import unittest
from salsa import *
from .SpectralCalibration import *
from .TimeConversions import *
import os

'''AUTHOR: Emma Lieb

    All tests use Saturnian satellite Pheobe as an example and UTC time 2004-06-11T19:32:00
'''
# class DataQueryTest(unittest.TestCase):
#     def test_getURL(self):
#         primaryParameter = 'irradiance'
#         secondaryParameter = 'wavelength'
#         tertiaryParameter = 'NONE'
#         dataset = 'NONE'
#         wavelengthLow = '180'
#         wavelengthHigh = '300'
#         timeLow = '2010-03-20'
#         timeHigh = '2010-03-24'
#         self.assertAlmostEqual(getURL(primaryParameter, secondaryParameter, tertiaryParameter, dataset, wavelengthLow, wavelengthHigh, timeLow, timeHigh), 0.00)
#         
class GetKernelsTest(unittest.TestCase):
    
    def test_getMissionFromTarget(self):
        target = 'Phoebe'
        self.assertEqual(getMissionFromTarget(target), "CASSINI")
        
    def test_getKernels(self):
        time = '2004-06-11T19:32:00'
        target = 'Phoebe'
        functionName = 'SCLK2ET'
        self.assertEqual(getKernels(target, functionName, time), ['naif0008.tls','cas00172.tsc'])
        
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
    def test_UTC2ET(self):
        time = '2004-06-11T19:32:00'
        target = 'Phoebe'
        result = 140254384.184625
        self.assertAlmostEqual(UTC2ET(time, target), result, 4)
           
    def test_SCLK2ET(self):
        timeStr = '1465674964.105'
        target = 'Phoebe'
        result = 140254384.183426
        self.assertAlmostEqual(SCLK2ET(timeStr, target), result, 4)
         
    def test_ET2Date(self):
        ET = 140254384.184625
        self.assertAlmostEqual(ET2Date(ET), '2004 JUN 11 19:33:04.184')
         
    def test_UTC2SPKKernelDate(self):
        time = '2004-06-11T19:32:00'
        self.assertEqual(UTC2SPKKernelDate(time), '040611')
        
    def test_UTC2CKKernelDate(self):
        time = '2004-06-11T19:32:00'
        self.assertEqual(UTC2CKKernelDate(time), '04162')
    def test_UTC2PCKKErnelDate(self):
        time = '2004-06-11T19:32:00'
        self.assertEqual(UTC2PCKKernelDate(time), '11Jun2004')
        
# class GeometryAndTimeCnvtTest(unittest.TestCase):
#      
#     def test_getVectorFromSpaceCraftToTarget(self):
#         time = '2004-06-11T19:32:00'
#         target = 'Phoebe'
#         ET = UTC2ET(time, target)
#         comp_vector = np.array([ -376599061.916539, 1294487780.929154, -7064853.054698])
#         self.assertAlmostEqual(getVectorFromSpaceCraftToTarget(ET, target).all(), comp_vector.all(), 4)
#          
#     def test_getVectorFromCraftToSun(self):
#         time = '2004-06-11T19:32:00'
#         target = 'Phoebe'
#         ET = UTC2ET(time, target)
#         pos_vector = getVectorFromSpaceCraftToTarget(ET, target)
#         comp_vector = np.array([-0.290204, 0.881631, 0.372167])
#         self.assertAlmostEqual(getVectorFromSpaceCraftToSun(ET, target, pos_vector).all(), comp_vector.all(), 4)
#          
#     def test_getTargetSunDistance(self):
#         time = '2004-06-11T19:32:00'
#         target = 'Phoebe'
#         ET = UTC2ET(time, target)
#         pos_vector = getVectorFromSpaceCraftToTarget(ET, target)
#         sunDir_vector = getVectorFromSpaceCraftToSun(ET, target, pos_vector)
#         distance_vector = sunDir_vector+pos_vector
#         distance = 9.4769 #Astronomical Units
#          
#         self.assertAlmostEqual(getTargetSunDistance(distance_vector), distance, 4)
#          
#     def test_getAngularSeparation(self):
#         time = '2004-06-11T19:32:00'
#         target = 'Phoebe'
#         ET = UTC2ET(time, target)
#         pos_vector = getVectorFromSpaceCraftToTarget(ET, target)
#         sunDir_vector = getVectorFromSpaceCraftToSun(ET, target,pos_vector)
#         distance_vector = pos_vector + sunDir_vector
#         comp_val = 71.924
#         self.assertAlmostEqual(getAngularSeparation(ET, target, distance_vector), comp_val, 4)
        
# class SpectralCalibrationTest(unittest.TestCase):     
#       
#     def test_fluxDistanceRelationship(self):
#         target = 'Phoebe'
#         time = '2004-06-11T19:32:00'
#         ET = UTC2ET(time, target)
#         
#         url = getURL('irradiance','wavelength',None, None, 180, 300, '2010-03-20', '2010-03-24')
#         data = requests.get(url).json()
#         
#         pos_vector = getVectorFromSpaceCraftToTarget(ET, target)
#         
#         sunDir_vector = getVectorFromSpaceCraftToSun(ET, target, pos_vector)
#         distance_vector = sunDir_vector+pos_vector
#         
#         distance = getTargetSunDistance(distance_vector)
#         self.assertAlmostEqual(fluxDistanceRelationship(data, distance), 0.00) #
        
if __name__ == '__main__':
    unittest.main()
        