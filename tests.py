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


class OpenUrlParserTest( unittest.TestCase ):

    """ Checks parsing of openurl data. """

    def setUp( self ):
        self.maxDiff = None
        self.ourls: list = [
            '//library.brown.edu/easyarticle/?genre=article&atitle="If I was not in prison, I would not be famous": Discipline, Choreography, and Mimicry in the Philippines&title=Theatre Journal&date=2011&volume=63&issue=4&spage=607&epage=621&issn=&doi=&aulast=J. Lorenzo&aufirst=Perillo&auinit=&__char_set=utf8',
            'https://login.revproxy.brown.edu/login?url=http://sfx.brown.edu:8888/sfx_local?sid=sfx:citation&genre=article&atitle=The Plot of her Undoing&title=Feminist Art Coalition&date=2020-12-28&volume=&issue=&spage=&epage=&issn=&id=&aulast=Hartman&aufirst=Saidiya&auinit=&__char_set=utf8'
            ]

    def test_parse_end_page(self):
        parsed_end_pages: list = []
        for ourl in self.ourls:
            epage = etl_class_data.parse_end_page( ourl )
            parsed_end_pages.append( epage )
        expected = [ 'foo', 'bar' ]
        self.assertEquals( expected, parsed_end_pages )

    ## end class OpenUrlParserTest()



class MapperTest( unittest.TestCase ):

    """ Checks mapping of db-resultset data to leganto fields. """

    def setUp( self ):
        self.maxDiff = None

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
        expected_sorted_keys = [
            'citation_author',
            'citation_doi',
            'citation_end_page',
            'citation_isbn',
            'citation_issn',
            'citation_publication_date',
            'citation_secondary_type',
            'citation_source1',
            'citation_source2',
            'citation_start_page',
            'citation_title',
            'coursecode',
            'external_system_id',
            'section_id'
            ]
        self.assertEqual( expected_sorted_keys, sorted(list(mapped_book_data.keys())) )
        expected_data = {
            'citation_author': 'Appleman, Deborah',
            'citation_doi': '',
            'citation_end_page': '',
            'citation_isbn': '',
            'citation_issn': '',
            'citation_publication_date': '',
            'citation_secondary_type': 'BK',
            'citation_source1': 'CDL linked',
            'citation_source2': '',
            'citation_start_page': '',
            'citation_title': 'Critical Encounters in Secondary English: Teaching Literary Theory to Adolescents ',
            'coursecode': 'EDUC2510',
            'external_system_id': '20200505172403authID',
            'section_id': 'A'
            }
        self.assertEqual( expected_data, mapped_book_data )
        ## end def test_map_book_data()

    def test_map_article_data(self):
        initial_article_data: dict = {
            'amount': 'y',
            'art_updated': datetime.datetime(2021, 1, 11, 12, 31, 4),
            'art_url': 'https://static1.squarespace.com/static/5c805bf0d86cc90a02b81cdc/t/5db8b219a910fa05af05dbf4/1572385305368/NotesOnFeminism-2_SaidiyaHartman.pdf',
            'articleid': 109044,
            'assignment': '',
            'atitle': 'The Plot of her Undoing',
            'aufirst': 'Saidiya',
            'auinit': '',
            'aulast': 'Hartman',
            'bibno': '',
            'bk_aufirst': '',
            'bk_auinit': '',
            'bk_aulast': '',
            'classid': 9756,
            'classuse': 'y',
            'copied_from_id': 108626,
            'date': datetime.date(2020, 12, 28),
            'date_due': None,
            'date_printed': None,
            'doi': '',
            'epage': None,
            'ereserve': 'web link',
            'facnotes': 'https://static1.squarespace.com/static/5c805bf0d86cc90a02b81cdc/t/5db8b219a910fa05af05dbf4/1572385305368/NotesOnFeminism-2_SaidiyaHartman.pdf',
            'fairuse': 'none',
            'format': 'article',
            'fullcit': '',
            'fulltext_url': '',
            'injosiah': 'dont know',
            'isbn': '',
            'issn': '',
            'issue': '',
            'jcallno': '',
            'nature': 'y',
            'notice': None,
            'original': 'y',
            'pmid': None,
            'printed': 'n',
            'publicdomain': 'none',
            'publisher': '',
            'reactivateid': '',
            'request_date': datetime.datetime(2021, 1, 11, 12, 31, 4),
            'requestid': '20210111123104OCRAcopy',
            'requests.requestid': '20210111123104OCRAcopy',
            'sequence': 'Week 6',
            'sfxlink': 'https://login.revproxy.brown.edu/login?url=http://sfx.brown.edu:8888/sfx_local?sid=sfx:citation&genre=article&atitle=The '
                        'Plot of her Undoing&title=Feminist Art '
                        'Coalition&date=2020-12-28&volume=&issue=&spage=&epage=&issn=&id=&aulast=Hartman&aufirst=Saidiya&auinit=&__char_set=utf8',
            'spage': None,
            'staff_intervention_needed': None,
            'staffnotes': '',
            'status': 'on reserve',
            'title': 'Feminist Art Coalition',
            'url_desc': '',
            'volume': ''}
        course_id = 'HMAN2401D'
        mapped_article_data: dict = etl_class_data.map_article( initial_article_data, course_id )
        expected_sorted_keys = [
            'citation_author',
            'citation_doi',
            'citation_end_page',
            'citation_isbn',
            'citation_issn',
            'citation_publication_date',
            'citation_secondary_type',
            'citation_source1',
            'citation_source2',
            'citation_start_page',
            'citation_title',
            'coursecode',
            'external_system_id',
            'section_id'
            ]
        self.assertEqual( expected_sorted_keys, sorted(list(mapped_article_data.keys())) )
        expected_data = {
            'citation_author': 'Hartman, Saidiya',
            'citation_doi': '',
            'citation_end_page': '',
            'citation_isbn': '',
            'citation_issn': '',
            'citation_publication_date': '',
            'citation_secondary_type': 'ARTICLE',
            'citation_source1': 'https://static1.squarespace.com/static/5c805bf0d86cc90a02b81cdc/t/5db8b219a910fa05af05dbf4/1572385305368/NotesOnFeminism-2_SaidiyaHartman.pdf',
            'citation_source2': 'https://static1.squarespace.com/static/5c805bf0d86cc90a02b81cdc/t/5db8b219a910fa05af05dbf4/1572385305368/NotesOnFeminism-2_SaidiyaHartman.pdf',
            'citation_start_page': '',
            'citation_title': 'Feminist Art Coalition',
            'coursecode': 'HMAN2401',
            'external_system_id': '20210111123104OCRAcopy',
            'section_id': 'D'
            }
        self.assertEqual( expected_data, mapped_article_data )
        ## end def test_map_article_data()

    ## end class MapperTest()


if __name__ == '__main__':
  unittest.main()





# book, ``{'bookid': 50031, 'requestid': '20200505172840authID', 'reactivateid': '20220610163908', 'bk_title': 'Next steps with academic conversations', 'callno': '--', 'libloc': 'Rock', 'bk_author': 'Zwiers, Jeff', 'publisher': '2019', 'isbn': '', 'bk_year': None, 'edition': '', 'sfxlink': '', 'libraryhas': 'N', 'copies': 1, 'personal': 'N', 'purchase': 'N', 'loan': '3 hrs', 'bookstore': 'N', 'required': 'optional', 'facnotes': 'Ebook on reserve', 'staffnotes': '', 'status': 'requested as ebook', 'bk_updated': datetime.datetime(2022, 6, 16, 9, 29, 25), 'printed': 'n', 'date_printed': None, 'ebook_id': 112235, 'bibno': '', 'needed_by': None, 'requests.requestid': '20200505172840authID', 'classid': 9342, 'request_date': datetime.datetime(2020, 5, 5, 17, 28, 40)}``
