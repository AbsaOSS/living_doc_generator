import unittest
import sys
sys.path.append('scripts')  # Adjust path to include the directory where hello.py is located
from hello import hello_world


class TestHelloWorld(unittest.TestCase):
    def test_hello_world(self):
        """Test the output of the hello_world function."""
        expected = "Hello, World!"
        result = hello_world()
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
