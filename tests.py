"""
Usage:
- to run all tests:
    - cd to `prep_reading_list_code` directory
    - $ python3 ./tests.py
- to run one test:
    - cd to `prep_reading_list_code` directory
    - example: $ python3 ./tests.py SomeTest.test_something
"""

import datetime, logging, os, unittest

import etl_class_data
from etl_class_data import CDL_Checker


LOG_PATH: str = os.environ['LGNT__LOG_PATH']

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)


class CDL_Checker_Test( unittest.TestCase ):

    """ Checks cdl-link prep. """

    def setUp(self) -> None:
        self.cdl_checker = etl_class_data.CDL_Checker()

    def test_search_cdl(self):
        """ Checks good fuzzy search-result. """
        ocra_search_term = 'Critical Encounters in Secondary English: Teaching Literary Theory to Adolescents'
        expected: list = [ {'score': 32, 'file_name': 'foo'} ]
        expected: list = [
            {'alma_item_pid': None,
            'alma_mms_id': '991006299729706966',
            'author': '',
            'barcode': None,
            'bib_id': 'b90794643',
            'created': datetime.datetime(2021, 6, 24, 19, 38, 39, 946705),
            'fuzzy_score': 93,
            'id': 1523,
            'item_file': 'b90794643_b90794643.pdf',
            'item_id': 'b90794643',
            'modified': datetime.datetime(2021, 8, 23, 20, 49, 45, 623634),
            'num_copies': 1,
            'status': 'ready',
            'title': 'Critical encounters in Secondary English : teaching literary theory to adolescents'}
            ]
        result: list = self.cdl_checker.search_cdl( ocra_search_term )
        self.assertEqual( expected, result )

    def test_prep_cdl_field_text(self):
        source_list = [
            {'alma_item_pid': None,
            'alma_mms_id': '991006299729706966',
            'author': '',
            'barcode': None,
            'bib_id': 'b90794643',
            'created': datetime.datetime(2021, 6, 24, 19, 38, 39, 946705),
            'fuzzy_score': 93,
            'id': 1523,
            'item_file': 'b90794643_b90794643.pdf',
            'item_id': 'b90794643',
            'modified': datetime.datetime(2021, 8, 23, 20, 49, 45, 623634),
            'num_copies': 1,
            'status': 'ready',
            'title': 'Critical encounters in Secondary English : teaching literary theory to adolescents'}
            ]
        expected = 'CDL link possibly: <https://cdl.library.brown.edu/cdl/item/b90794643>'
        result: str = self.cdl_checker.prep_cdl_field_text( source_list )
        self.assertEqual( expected, result )

    ## end classCdlLinkerTest()


class OpenUrlParserTest( unittest.TestCase ):

    """ Checks parsing of openurl data. """

    def setUp( self ):
        self.maxDiff = None
        self.ourls: list = [
            '//library.brown.edu/easyarticle/?genre=article&atitle="If I was not in prison, I would not be famous": Discipline, Choreography, and Mimicry in the Philippines&title=Theatre Journal&date=2011&volume=63&issue=4&spage=607&epage=621&issn=&doi=&aulast=J. Lorenzo&aufirst=Perillo&auinit=&__char_set=utf8',
            'https://login.revproxy.brown.edu/login?url=http://sfx.brown.edu:8888/sfx_local?sid=sfx:citation&genre=article&atitle=The Plot of her Undoing&title=Feminist Art Coalition&date=2020-12-28&volume=&issue=&spage=&epage=&issn=&id=&aulast=Hartman&aufirst=Saidiya&auinit=&__char_set=utf8',
            ]

    def test_parse_openurl(self):
        """ Checks parsing of openurl, including revproxied urls. """
        expected = [
            {'genre': ['article'], 'atitle': ['"If I was not in prison, I would not be famous": Discipline, Choreography, and Mimicry in the Philippines'], 'title': ['Theatre Journal'], 'date': ['2011'], 'volume': ['63'], 'issue': ['4'], 'spage': ['607'], 'epage': ['621'], 'aulast': ['J. Lorenzo'], 'aufirst': ['Perillo'], '__char_set': ['utf8']},
            {'sid': ['sfx:citation'], 'genre': ['article'], 'atitle': ['The Plot of her Undoing'], 'title': ['Feminist Art Coalition'], 'date': ['2020-12-28'], 'aulast': ['Hartman'], 'aufirst': ['Saidiya'], '__char_set': ['utf8']},
            ]
        for (i, ourl) in enumerate(self.ourls):
            parts: dict = etl_class_data.parse_openurl( ourl )
            log.debug( f'parts, ``{parts}``' )
            self.assertEqual( expected[i], parts )
        
    def test_parse_start_page_from_ourl(self):
        expected = [ '607', '' ]
        for (i, ourl) in enumerate(self.ourls):
            parts: dict = etl_class_data.parse_openurl( ourl )
            spage: str = etl_class_data.parse_start_page_from_ourl( parts )
            self.assertEqual( expected[i], spage )

    def test_parse_end_page_from_ourl(self):
        expected = [ '621', '' ]
        for (i, ourl) in enumerate(self.ourls):
            parts: dict = etl_class_data.parse_openurl( ourl )
            epage: str = etl_class_data.parse_end_page_from_ourl( parts )
            self.assertEqual( expected[i], epage )

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
        cdl_checker = CDL_Checker()
        mapped_book_data: dict = etl_class_data.map_book( initial_book_data, course_id, cdl_checker )
        expected_sorted_keys = [
            'citation_author',
            'citation_doi',
            'citation_end_page',
            'citation_isbn',
            'citation_issn',
            'citation_issue',
            'citation_publication_date',
            'citation_secondary_type',
            'citation_source1',
            'citation_source2',
            'citation_start_page',
            'citation_title',
            'citation_volume',
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
            'citation_issue': '',
            'citation_publication_date': '',
            'citation_secondary_type': 'BK',
            # 'citation_source1': 'CDL linked',
            'citation_source1': 'CDL link possibly: <https://cdl.library.brown.edu/cdl/item/b90794643>',
            'citation_source2': '',
            'citation_start_page': '',
            'citation_title': 'Critical Encounters in Secondary English: Teaching Literary Theory to Adolescents ',
            'citation_volume': '',
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
        cdl_checker = CDL_Checker()
        mapped_article_data: dict = etl_class_data.map_article( initial_article_data, course_id, cdl_checker )
        expected_sorted_keys = [
            'citation_author',
            'citation_doi',
            'citation_end_page',
            'citation_isbn',
            'citation_issn',
            'citation_issue',
            'citation_publication_date',
            'citation_secondary_type',
            'citation_source1',
            'citation_source2',
            'citation_start_page',
            'citation_title',
            'citation_volume',
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
            'citation_issue': '',
            'citation_publication_date': '2020-12-28',
            'citation_secondary_type': 'ARTICLE',
            'citation_source1': 'https://static1.squarespace.com/static/5c805bf0d86cc90a02b81cdc/t/5db8b219a910fa05af05dbf4/1572385305368/NotesOnFeminism-2_SaidiyaHartman.pdf',
            'citation_source2': 'https://static1.squarespace.com/static/5c805bf0d86cc90a02b81cdc/t/5db8b219a910fa05af05dbf4/1572385305368/NotesOnFeminism-2_SaidiyaHartman.pdf',
            'citation_start_page': '',
            'citation_title': 'Feminist Art Coalition',
            'citation_volume': '',
            'coursecode': 'HMAN2401',
            'external_system_id': '20210111123104OCRAcopy',
            'section_id': 'D'
            }
        self.assertEqual( expected_data, mapped_article_data )
        ## end def test_map_article_data()

    def test_parse_excerpt_author(self):
        """ Checks parse_excerpt_author() helper's processing of various author fields. """
        excerpt_db_data: dict = { 'articleid': 117436, 'requestid': '20220404173710jdelleca', 'reactivateid': '', 'format': 'excerpt', 'atitle': 'Introduction: Rhizome ', 'title': 'A Thousand Plateaus', 
        'aulast': '', 
        'aufirst': '', 
        'auinit': '', 
        'bk_aulast': 'Felix Guattari', 
        'bk_aufirst': 'Gilles Deleuze', 
        'bk_auinit': '', 
        'sfxlink': '//library.brown.edu/easyarticle/?genre=article&atitle=Introduction: Rhizome &title=A Thousand Plateaus&date=1980-01-01&volume=&issue=&spage=1&epage=25&issn=&doi=&aulast=&aufirst=&auinit=&__char_set=utf8', 
        'ereserve': 'has pdf', 'status': 'on reserve', 'volume': '', 'issue': '', 'publisher': '', 'date': datetime.date(1980, 1, 1), 'issn': '', 'isbn': '', 'spage': None, 'epage': None, 'assignment': '', 'art_url': '', 'url_desc': '', 'doi': '', 'publicdomain': 'none', 'fairuse': 'none', 'classuse': 'y', 'nature': 'y', 'amount': 'y', 'original': 'y', 'notice': None, 'sequence': '', 'date_due': datetime.date(1969, 12, 31), 'facnotes': '', 'staffnotes': '', 'art_updated': datetime.datetime(2022, 4, 4, 17, 45, 2), 'injosiah': 'dont know', 'jcallno': '', 'bibno': '', 'printed': 'n', 'date_printed': None, 'pmid': None, 'fullcit': '', 'fulltext_url': '', 'copied_from_id': None, 'staff_intervention_needed': None, 'requests.requestid': '20220404173710jdelleca', 'classid': 10488, 'request_date': datetime.datetime(2022, 4, 4, 17, 37, 10) }
        expected = 'Felix Guattari, Gilles Deleuze'
        self.assertEqual( expected, etl_class_data.parse_excerpt_author(excerpt_db_data) )

    ## end class MapperTest()


if __name__ == '__main__':
  unittest.main()
