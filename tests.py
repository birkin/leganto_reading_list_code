"""
Usage:
- to run all tests:
    - cd to `prep_reading_list_code` directory
    - $ python3 ./tests.py
- to run one test:
    - cd to `prep_reading_list_code` directory
    - example: $ python3 ./tests.py SomeTest.test_something
"""

import datetime, logging, os, sys, unittest

import etl_class_data

# sys.path.append( os.environ['(enclosing-project-path)'] )


# LOG_PATH: str = os.environ['LGNT__LOG_PATH']

logging.basicConfig(
    # filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'test-logging ready' )


class MapperTest( unittest.TestCase ):

    def setUp( self ):
        pass

    def test_map_book_data(self):
        initial_book_data: dict = {
            'bibno': '',
            'bk_author': 'Appleman, Deborah',
            'bk_title': 'Critical Encounters in Secondary English: Teaching Literary '
                        'Theory to Adolescents ',
            'bk_updated': datetime.datetime(2022, 6, 16, 9, 29, 5),
            'bk_year': None,
            'bookid': 50027,
            'bookstore': 'N',
            'callno': '-',
            'classid': 9342,
            'copies': 1,
            'date_printed': None,
            'ebook_id': 112561,
            'edition': '',
            'facnotes': 'CDL linked',
            'isbn': '',
            'libloc': 'Rock',
            'libraryhas': 'N',
            'loan': '3 hrs',
            'needed_by': None,
            'personal': 'N',
            'printed': 'n',
            'publisher': '3rd edition',
            'purchase': 'N',
            'reactivateid': '20220610163908',
            'request_date': datetime.datetime(2020, 5, 5, 17, 24, 3),
            'requestid': '20200505172403authID',
            'requests.requestid': '20200505172403authID',
            'required': 'optional',
            'sfxlink': '',
            'staffnotes': '',
            'status': 'requested as ebook'
            }
        
        course_id = 'EDUC2510A'
        mapped_book_data: dict = etl_class_data.map_book( initial_book_data, course_id )
        self.assertEqual( [ 'key_a', 'key_b' ], sorted(list(mapped_book_data.keys())) )
        self.assertEqual( 'foo', mapped_book_data )


if __name__ == '__main__':
  unittest.main()





# book, ``{'bookid': 50031, 'requestid': '20200505172840authID', 'reactivateid': '20220610163908', 'bk_title': 'Next steps with academic conversations', 'callno': '--', 'libloc': 'Rock', 'bk_author': 'Zwiers, Jeff', 'publisher': '2019', 'isbn': '', 'bk_year': None, 'edition': '', 'sfxlink': '', 'libraryhas': 'N', 'copies': 1, 'personal': 'N', 'purchase': 'N', 'loan': '3 hrs', 'bookstore': 'N', 'required': 'optional', 'facnotes': 'Ebook on reserve', 'staffnotes': '', 'status': 'requested as ebook', 'bk_updated': datetime.datetime(2022, 6, 16, 9, 29, 25), 'printed': 'n', 'date_printed': None, 'ebook_id': 112235, 'bibno': '', 'needed_by': None, 'requests.requestid': '20200505172840authID', 'classid': 9342, 'request_date': datetime.datetime(2020, 5, 5, 17, 28, 40)}``
