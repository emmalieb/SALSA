import unittest
from GeometryAndTimeConverts import *
from GetKernels import *

'''AUTHOR: Emma Lieb

    All tests use Saturnian satellite Pheobe as an example and UTC time 2004-06-11T19:32:00
'''

class GeometryAndTimeCnvtTest(unittest.TestCase):
    
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
    
    def test_getVectorFromSpaceCraftToTarget(self):
        time = '2004-06-11T19:32:00'
        target = 'Phoebe'
        ET = UTC2ET(time, target)
        comp_vector = [ -376599061.916539, 1294487780.929154, -7064853.054698]
        self.assertAlmostEqual(getVectorFromSpaceCraftToTarget(ET, target), comp_vector, 4)
        
    def test_getVectorFromCraftToSun(self):
        time = '2004-06-11T19:32:00'
        target = 'Phoebe'
        ET = UTC2ET(time, target)
        pos_vect = getVectorFromSpaceCraftToTarget(ET, target)
        comp_vector = [-0.290204, 0.881631, 0.372167]
        self.assertAlmostEqual(getVectorFromSpaceCraftToSun(ET, target), comp_vector)
        
    def test_getTargetSunDistance(self):
        time = '2004-06-11T19:32:00'
        target = 'Phoebe'
        ET = UTC2ET(time, target)
        pos_vector = getVectorFromSpaceCraftToTarget(ET, target)
        sunDir_vector = getVectorFromSpaceCraftToSun(ET, target, pos_vector)
        distance_vector = sunDir_vector+pos_vector
        distance = 9.4769 #Astronomical Units
        
        self.assertAlmostEqual(getTargetSunDistance(distance_vector), distance)
        
#     def test_getAngularSeparation(self):
#         time = '2004-06-11T19:32:00'
#         target = 'Phoebe'
#         ET = UTC2ET(time, target)
#         pos_vector = getVectorFromSpaceCraftToTarget(ET, target)
#         sunDir_vector = getVectorFromSpaceCraftToSun(ET, target,pos_vector)
#         distance_vector = pos_vector + sunDir_vector
#         comp_vector = []
#         self.assertAlmostEqual(getAngularSeparation(ET, target, distance_vector), comp_vector)

class GetKernelsTest(unittest.TestCase):
    
    def test_getMissionFromTarget(self):
        target = 'Phoebe'
        
        self.assertEqual(getMissionFromTarget(target), "CASSINI")      
        
if __name__ == '__main__':
    unittest.main()
        