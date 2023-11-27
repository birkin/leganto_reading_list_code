"""
Usage:
- to run all tests:
    - cd to `/leganto_reading_list_code/` directory
    - $ python3 ./instructor_check_flow/tests_instructor_check.py
- to run one test:
    - cd to `/leganto_reading_list_code/` directory
    - example: $ python3 ./instructor_check_flow/tests_instructor_check.py SomeClass.some_method
"""

import datetime, importlib, json, logging, os, unittest

make_oit_subset_two = importlib.import_module( '20_make_oit_subset_two' )  # required because modules shouldn't start wit numbers


class MiscTest( unittest.TestCase ):

    """ Checks TODO functions. """

    def setUp( self ):
        pass

    def test_check_for_match(self):
        """ Checks match between OIT data and already-in-leganto data. 
            Note email-case difference. """
        oit_course_code_key = 'afri.0090'
        oit_email = 'First_Last@brown.edu'
        already_in_leganto_dict_lines = [ {
            'Course Code': 'brown.afri.0090.2023-fall.s01',
            'Reading List Code': 'brown.afri.0090.2023-fall.s01',
            'Reading List Name': 'an intro to africana studies',
            'email_list': ['first_last@brown.edu']
            },
        ]
        expected = True
        result = make_oit_subset_two.check_for_match( oit_course_code_key, oit_email, already_in_leganto_dict_lines )
        # result = common.parse_course_code( 'foo', 1 )
        self.assertEqual( expected, result )


if __name__ == '__main__':
  unittest.main()
