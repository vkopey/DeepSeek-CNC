from testStreamlit2 import parse_gcode
import unittest

class TestAddFunction(unittest.TestCase):
    def test_add(self):
        self.assertEqual(parse_gcode("G1 X1 Y2 Z3"), ([1],[2],[3]))
        self.assertNotEqual(parse_gcode("G0 X0 Y0\nG1 Y2 Z3"), ([0,0],[0,2],[0,3]))
        self.assertEqual(parse_gcode("G1 X1 Y2\nM2"), ([],[],[]))

if __name__ == "__main__":
    unittest.main()

# Ran 1 test in 0.011s
#
# OK