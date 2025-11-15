import unittest
from src.wacom_driver import pressure_scale  # Extract function

class TestPressure(unittest.TestCase):
    def test_scaling(self):
        self.assertGreater(pressure_scale(100), 50)
        self.assertEqual(pressure_scale(0), 0)

if __name__ == '__main__':
    unittest.main()
