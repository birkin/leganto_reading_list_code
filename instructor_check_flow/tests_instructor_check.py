"""
Usage:
- to run all tests:
    - cd to `/leganto_reading_list_code/` directory
    - $ python3 ./instructor_check_flow/tests_instructor_check.py
- to run one test:
    - cd to `/leganto_reading_list_code/` directory
    - example: $ python3 ./instructor_check_flow/tests_instructor_check.py SomeClass.some_method
"""

import datetime, json, logging, os, unittest

class MiscTest( unittest.TestCase ):

    """ Checks TODO functions. """

    def setUp( self ):
        pass

    def test_foo(self):
        """ Checks TODO. """
        self.assertEqual( 1, 2 )




if __name__ == '__main__':
  unittest.main()
