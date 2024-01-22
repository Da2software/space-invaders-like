import unittest

if __name__ == '__main__':
    # Discover and run all tests in the 'tests' directory and
    # its subdirectories
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('src', pattern='test_*.py')

    # Run the tests
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)
