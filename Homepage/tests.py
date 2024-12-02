import unittest
import calc


class TestCalc(unittest.TestCase):
    def test_add(self):
        result = calc.app(10, 5)
        print(result)

if __name__ == '__main__':
    unittest.main()