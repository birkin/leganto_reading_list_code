"""
Usage:
- to run all tests:
    - cd to `prep_reading_list_code` directory
    - $ python3 ./tests.py
- to run one test:
    - cd to `prep_reading_list_code` directory
    - example: $ python3 ./tests.py SomeTest.test_something
"""

import datetime, json, logging, os, unittest

from lib import cdl
from lib import gsheet_prepper
from lib import leganto_final_processor
from lib import readings_processor
from lib.cdl import CDL_Checker
from lib.loaders import OIT_Course_Loader
from lib.readings_processor import check_pdfs


COURSES_FILEPATH: str =  os.environ['LGNT__COURSES_FILEPATH']
SCANNED_DATA_PATH: str = os.environ['LGNT__SCANNED_DATA_JSON_PATH']
LOG_PATH: str = os.environ['LGNT__LOG_PATH']

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)

oit_course_loader = OIT_Course_Loader( COURSES_FILEPATH )  # instantiation loads data from file into list of dicts


class OitCourseCodeTest( unittest.TestCase ):

    """ Checks oit-loader functions. """

    def setUp( self ):
        pass

    def test_grab_oit_course_data__all_good(self):
        """ Checks lookup for known good item. """
        # course_id = 'EAST0402'
        # expected = 'brown.east.0402.2022-fall.s01'
        course_id = 'ANTH0066X'
        expected = 'brown.anth.0066x.2023-spring.s01'
        data: list = oit_course_loader.grab_oit_course_data( course_id )
        assert type(data) == list
        self.assertEqual( expected, data[0]['COURSE_CODE'] )

    def test_grab_oit_course_data__code_part_contains_letter(self):
        """ Checks lookup for item with code-part containing a letter. 
            (Had to lowercase the code-part.) """
        course_id = 'ANTH0066X'
        expected = 'brown.anth.0066x.2023-spring.s01'
        data: list = oit_course_loader.grab_oit_course_data( course_id )
        assert type(data) == list
        self.assertEqual( expected, data[0]['COURSE_CODE'] )


class Leganto_Final_Processor_Test( unittest.TestCase ):
    
    """ Checks leganto-final-processor functions. """

    def setUp( self ):
        pass

    def test_calculate_leganto_citation_source_from_book_data(self):
        """ Checks calculate_leganto_citation_source() using mapped-book-data. """
        inputs_and_expecteds = [
            {   'book_data':  { 'citation_source1': 'CDL link likely: <https://cdl.library.brown.edu/cdl/item/i168901742>', 'citation_source4': '' },
                'expected': 'https://cdl.library.brown.edu/cdl/item/i168901742' },
            {   'book_data':  { 'citation_source1': 'CDL link possibly: <https://cdl.library.brown.edu/cdl/item/i142579956>', 'citation_source4': '' },
                'expected': 'https://cdl.library.brown.edu/cdl/item/i142579956' },
            {   'book_data':  { 'citation_source1': 'no CDL link found', 'citation_source4': '' },
                'expected': '' },
            ]
        for entry in inputs_and_expecteds:
            book_data = entry['book_data']
            expected = entry['expected']
            result = leganto_final_processor.calculate_leganto_citation_source( book_data )
            self.assertEqual( expected, result )

    def test_calculate_leganto_citation_source_from_article_data(self):
        """ Checks calculate_leganto_citation_source() using mapped-article-data. """
        inputs_and_expecteds = [
            {   'article_data':  { 'citation_source1': 'no CDL link found', 'citation_source4': 'https://library.brown.edu/reserves/pdffiles/61925_france_battles_over_whether_to_cancel.pdf' },
                'expected': 'https://library.brown.edu/reserves/pdffiles/61925_france_battles_over_whether_to_cancel.pdf' },
            {   'article_data':  { 'citation_source1': 'no CDL link found', 'citation_source4': 'no_pdf_found' },
                'expected': '' },
            ]
        for entry in inputs_and_expecteds:
            article_data = entry['article_data']
            expected = entry['expected']
            result = leganto_final_processor.calculate_leganto_citation_source( article_data )
            self.assertEqual( expected, result )

    def test_calculate_leganto_citation_source_from_ebook_data(self):
        """ Checks calculate_leganto_citation_source() using mapped-ebook-data. """
        inputs_and_expecteds = [
            {   'ebook_data':  { 'citation_source1': 'CDL link possibly: <https://cdl.library.brown.edu/cdl/item/23267522610006966>', 'citation_source4': 'https://library.brown.edu/reserves/pdffiles/61925_france_battles_over_whether_to_cancel.pdf' },
                'expected': 'https://library.brown.edu/reserves/pdffiles/61925_france_battles_over_whether_to_cancel.pdf',
                'comment': 'tests that pdf trumps cdl' },
            {   'ebook_data':  { 'citation_source1': 'CDL link possibly: <https://cdl.library.brown.edu/cdl/item/23267522610006966>', 'citation_source4': 'no_pdf_found' },
                'expected': 'https://cdl.library.brown.edu/cdl/item/23267522610006966',
                'comment': 'tests that if there is no pdf, use the cdl link' },
            {   'ebook_data':  { 'citation_source1': 'no CDL link found', 'citation_source4': 'no_pdf_found' },
                'expected': '',
                'comment': 'tests that empty result is returned if there is no pdf or cdl info' },
            ]        
        for entry in inputs_and_expecteds:
            ebook_data = entry['ebook_data']
            expected = entry['expected']
            result = leganto_final_processor.calculate_leganto_citation_source( ebook_data )
            self.assertEqual( expected, result )

    def test_calculate_leganto_citation_source_from_website_data(self):
        """ Checks calculate_leganto_citation_source() using mapped-website-data. """
        inputs_and_expecteds = [
            {   'website_data':  { 'citation_source1': 'no CDL link found', 'citation_source2': '', 'citation_source4': 'https://library.brown.edu/reserves/pdffiles/61886_belonging_is_stronger_than_facts__nyt.pdf', 'citation_secondary_type': 'WS' },
                'expected': 'https://library.brown.edu/reserves/pdffiles/61886_belonging_is_stronger_than_facts__nyt.pdf' },
            {   'website_data':  { 'citation_source1': 'no CDL link found', 'citation_source2': 'https://brown.kanopystreaming.com/node/111103', 'citation_source4': 'no_pdf_found', 'citation_secondary_type': 'WS' },
                'expected': 'https://brown.kanopystreaming.com/node/111103' },
            ]
        for entry in inputs_and_expecteds:
            website_data = entry['website_data']
            expected = entry['expected']
            result = leganto_final_processor.calculate_leganto_citation_source( website_data )
            self.assertEqual( expected, result )

    def test_clean_citation_title(self):
        """ Checks cleaned leganto title. """
        self.assertEqual( 'no-title', 
            leganto_final_processor.clean_citation_title( '' ) 
            )
        self.assertEqual( '(EXCERPT)', 
            leganto_final_processor.clean_citation_title( '(EXCERPT) ' ) 
            )
        self.assertEqual( 'Bharatha Natyam-What Are You?', 
            leganto_final_processor.clean_citation_title( '(EXCERPT) "Bharatha Natyam-What Are You?.' ) 
            )
        self.assertEqual( 'Frayed Fabrications: Feminine Mobility, Surrogate Bodies and Robe Usage in Noh Drama', 
            leganto_final_processor.clean_citation_title( '“Frayed Fabrications: Feminine Mobility, Surrogate Bodies and Robe Usage in Noh Drama”' ) 
            )
        self.assertEqual( 'Ritual', 
            leganto_final_processor.clean_citation_title( '"Ritual"' ) 
            )
        self.assertEqual( 'Research, Countertext, Proposal: Considering the Textual Authority of the Dramaturg',
            leganto_final_processor.clean_citation_title( '“Research, Countertext, Proposal: Considering the Textual Authority of the Dramaturg' ) 
            )

    def test_clean_citation_author(self):
        """ Checks cleaned leganto author. """
        self.assertEqual( 'Last, First', 
            leganto_final_processor.clean_citation_author( 'Last, First' ) 
            )
        self.assertEqual( 'Name', 
            leganto_final_processor.clean_citation_author( ',Name' ) 
            )
        self.assertEqual( 'Name', 
            leganto_final_processor.clean_citation_author( 'Name,' ) 
            )
        self.assertEqual( '', 
            leganto_final_processor.clean_citation_author( ', ' ) 
            )

    ## end class Leganto_Final_Processor_Test


class Misc_Test( unittest.TestCase ):

    """ Miscellaneous checks. """

    def setUp(self) -> None:
        self.scanned_data = self.load_scanned_data()

    def load_scanned_data( self ) -> dict:
        scanned_data: dict = {}
        with open( SCANNED_DATA_PATH, encoding='utf-8' ) as file_handler:
            jsn: str = file_handler.read()
            scanned_data = json.loads( jsn )
        return scanned_data

    def test_column_math(self):
        """ Checks calculated end-column. """
        self.assertEqual( 'B', gsheet_prepper.calculate_end_column(2) )
        self.assertEqual( 'AA', gsheet_prepper.calculate_end_column(27) )
        self.assertEqual( 'BO', gsheet_prepper.calculate_end_column( 67 ) )

    # def test_check_pdfs_A(self):
    #     """ Checks for accurate file-name find. """
    #     initial_excerpt_data: dict = {
    #         'amount': 'y',
    #         'art_updated': datetime.datetime(2019, 8, 20, 15, 41, 39),
    #         'art_url': '',
    #         'articleid': 100230,
    #         'assignment': '',
    #         'atitle': 'Quinta Temporada, Los Vendidos, Los Dos Caras del Patroncito',
    #         'aufirst': 'Luis ',
    #         'auinit': '',
    #         'aulast': 'Valdez',
    #         'bibno': '',
    #         'bk_aufirst': 'Luis ',
    #         'bk_auinit': '',
    #         'bk_aulast': 'Valdez',
    #         'classid': 8851,
    #         'classuse': 'y',
    #         'copied_from_id': None,
    #         'date': datetime.date(1990, 1, 1),
    #         'date_due': datetime.date(2019, 9, 17),
    #         'date_printed': datetime.datetime(2019, 8, 20, 8, 22, 54),
    #         'doi': '',
    #         'epage': None,
    #         'ereserve': 'has pdf',
    #         'facnotes': '',
    #         'fairuse': 'none',
    #         'format': 'excerpt',
    #         'fullcit': '',
    #         'fulltext_url': '',
    #         'injosiah': 'dont know',
    #         'isbn': '',
    #         'issn': '',
    #         'issue': '',
    #         'jcallno': '',
    #         'nature': 'y',
    #         'notice': None,
    #         'original': 'y',
    #         'pmid': None,
    #         'printed': 'y',
    #         'publicdomain': 'none',
    #         'publisher': 'Arte Publico',
    #         'reactivateid': '',
    #         'request_date': datetime.datetime(2019, 8, 17, 6, 4, 17),
    #         'requestid': '20190817060417pybarra',
    #         'requests.requestid': '20190817060417pybarra',
    #         'sequence': '',
    #         'sfxlink': '//library.brown.edu/easyarticle/?genre=article&atitle=Quinta '
    #                     'Temporada, Los Vendidos, Los Dos Caras del Patroncito&title=Early '
    #                     'Works&date=1990-01-01&volume=&issue=&spage=18&epage=52&issn=&doi=&aulast=Valdez&aufirst=Luis '
    #                     '&auinit=&__char_set=utf8',
    #         'spage': None,
    #         'staff_intervention_needed': None,
    #         'staffnotes': '',
    #         'status': 'on reserve',
    #         'title': 'Early Works',
    #         'url_desc': '',
    #         'volume': ''
    #         }
    #     expected = 'valdez_early.pdf'
    #     result = check_pdfs( initial_excerpt_data, self.scanned_data )  
    #     self.assertEqual( expected, result )  # course-id is `TAPS1610`
            
    ## end class Misc_Test()


class CDL_Checker_Test( unittest.TestCase ):

    """ Checks cdl-link prep. """

    def setUp(self) -> None:
        self.cdl_checker = CDL_Checker()

    def test_search_cdl(self):
        """ Checks good fuzzy search-result. """
        ocra_search_term = 'Critical Encounters in Secondary English: Teaching Literary Theory to Adolescents'
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

    def test_search_cdl__multiple_results(self):
        """ Checks good fuzzy search-result. """
        ocra_search_term = 'Yi Kwangsu and Modern Korean Literature'
        expected: list = [
            {
            'alma_item_pid': '23328680100006966',
            'alma_mms_id': '991003807939706966',
            'author': 'Lee, Ann Sung-hi.',
            'barcode': '31236019077620',
            'bib_id': '',
            'created': datetime.datetime(2021, 10, 23, 22, 34, 3, 371628),
            'fuzzy_score': 82,
            'id': 2058,
            'item_file': '31236019077620.pdf',
            'item_id': '23328680100006966',
            'modified': datetime.datetime(2021, 10, 25, 14, 0, 39, 828365),
            'num_copies': 2,
            'status': 'ready',
            'title': 'Yi Kwang-su and modern Korean literature, Mujŏng /'
            },
            {
            'alma_item_pid': '23328680070006966',
            'alma_mms_id': '991003807939706966',
            'author': 'Lee, Ann Sung-hi.',
            'barcode': '31236091503212',
            'bib_id': '',
            'created': datetime.datetime(2022, 8, 25, 18, 12, 42, 107910),
            'fuzzy_score': 82,
            'id': 2903,
            'item_file': '31236091503212.pdf',
            'item_id': '23328680070006966',
            'modified': datetime.datetime(2022, 8, 25, 18, 13, 55, 955326),
            'num_copies': 1,
            'status': 'ready',
            'title': 'Yi Kwang-su and modern Korean literature, Mujŏng /'
            }
        ]
        result: list = self.cdl_checker.search_cdl( ocra_search_term )
        self.assertEqual( expected, result )
        ## end def test_search_cdl__multiple_results()

    def test_search_cdl_empty_title(self):
        """ Checks that empty search is handled properly. """
        ocra_search_term = ''
        expected: list = []
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

    def test_prep_cdl_field_text__multiple_results(self):
        source_list = [
            {
            'alma_item_pid': '23328680100006966',
            'alma_mms_id': '991003807939706966',
            'author': 'Lee, Ann Sung-hi.',
            'barcode': '31236019077620',
            'bib_id': '',
            'created': datetime.datetime(2021, 10, 23, 22, 34, 3, 371628),
            'fuzzy_score': 82,
            'id': 2058,
            'item_file': '31236019077620.pdf',
            'item_id': '23328680100006966',
            'modified': datetime.datetime(2021, 10, 25, 14, 0, 39, 828365),
            'num_copies': 2,
            'status': 'ready',
            'title': 'Yi Kwang-su and modern Korean literature, Mujŏng /'
            },
            {
            'alma_item_pid': '23328680070006966',
            'alma_mms_id': '991003807939706966',
            'author': 'Lee, Ann Sung-hi.',
            'barcode': '31236091503212',
            'bib_id': '',
            'created': datetime.datetime(2022, 8, 25, 18, 12, 42, 107910),
            'fuzzy_score': 82,
            'id': 2903,
            'item_file': '31236091503212.pdf',
            'item_id': '23328680070006966',
            'modified': datetime.datetime(2022, 8, 25, 18, 13, 55, 955326),
            'num_copies': 1,
            'status': 'ready',
            'title': 'Yi Kwang-su and modern Korean literature, Mujŏng /'
            }
        ]
        expected = 'Multiple possible CDL links: <https://cdl.library.brown.edu/cdl/item/23328680100006966>, <https://cdl.library.brown.edu/cdl/item/23328680070006966>'
        result: str = self.cdl_checker.prep_cdl_field_text( source_list )
        self.assertEqual( expected, result )
        ## end def test_prep_cdl_field_text__multiple_results()

    def test_run_book_cdl_check_from_book_data(self):
        """ Checks data prepared for citation_source1, from ocra-book-data. 
            Note, since this is a live test, it's possible that the data will change. """
        inputs_and_expecteds = [
            { 'ocra_facnotes_data': 'Ebook on reserve', 'title': ' The Palgrave Handbook Of Mass Dictatorship', 'expected': 'no CDL link found' },
            { 'ocra_facnotes_data': '', 'title': 'Capitalizing on crisis : the political origins of the rise of finance', 'expected': 'no CDL link found' },
            { 'ocra_facnotes_data': 'CDL linked 11/9/2022', 'title': 'Austerity the history of a dangerous idea', 'expected': 'CDL link likely: <https://cdl.library.brown.edu/cdl/item/i168901742>' },
            { 'ocra_facnotes_data': 'CDL linked 10/19/2022', 'title': 'Capital Rules: The Construction of Global Finance', 'expected': 'CDL link possibly: <https://cdl.library.brown.edu/cdl/item/i142579956>' }, 
            { 'ocra_facnotes_data': None, 'title': None, 'expected': 'no CDL link found' }, 
            ]
        for entry in inputs_and_expecteds:
            ocra_facnotes_data = entry['ocra_facnotes_data']
            title = entry['title']
            expected = entry['expected']
            result = cdl.run_book_cdl_check( ocra_facnotes_data, title, self.cdl_checker )
            self.assertEqual( expected, result )

    def test_run_ebook_cdl_check_from_ebook_data(self):
        """ Checks data prepared for citation_source1, from ocra-ebook-data. 
            Note, since this is a live test, it's possible that the data will change. """
        inputs_and_expecteds = [
            { 'ocra_facnotes_data': '', 'ocra_art_url': 'https://ebookcentral-proquest-com.revproxy.brown.edu/lib/brown/detail.action?docID=3117969', 'title': 'The Great Transformation', 
                'expected': 'CDL link possibly: <https://cdl.library.brown.edu/cdl/item/23267522610006966>' },
            { 'ocra_facnotes_data': '', 'ocra_art_url': 'https://cdl.library.brown.edu/cdl/item/b2020176x_i111044777', 'title': 'The Great Crash', 
                'expected': 'CDL link likely: https://cdl.library.brown.edu/cdl/item/b2020176x_i111044777' },
            ]
        for entry in inputs_and_expecteds:
            ocra_facnotes_data = entry['ocra_facnotes_data']
            ocra_art_url = entry['ocra_art_url']
            title = entry['title']
            expected = entry['expected']
            result = cdl.run_ebook_cdl_check( ocra_facnotes_data, ocra_art_url, title, self.cdl_checker )
            self.assertEqual( expected, result )

    ## end classCdlLinkerTest()


class OpenUrlParserTest( unittest.TestCase ):

    """ Checks parsing of openurl data. """

    def setUp( self ):
        self.maxDiff = None
        self.ourls: list = [
            '//library.brown.edu/easyarticle/?genre=article&atitle="If I was not in prison, I would not be famous": Discipline, Choreography, and Mimicry in the Philippines&title=Theatre Journal&date=2011&volume=63&issue=4&spage=607&epage=621&issn=&doi=&aulast=J. Lorenzo&aufirst=Perillo&auinit=&__char_set=utf8',
            'https://login.revproxy.brown.edu/login?url=http://sfx.brown.edu:8888/sfx_local?sid=sfx:citation&genre=article&atitle=The Plot of her Undoing&title=Feminist Art Coalition&date=2020-12-28&volume=&issue=&spage=&epage=&issn=&id=&aulast=Hartman&aufirst=Saidiya&auinit=&__char_set=utf8',
            None
            ]

    def test_parse_openurl(self):
        """ Checks parsing of openurl, including revproxied urls. """
        expected = [
            {'genre': ['article'], 'atitle': ['"If I was not in prison, I would not be famous": Discipline, Choreography, and Mimicry in the Philippines'], 'title': ['Theatre Journal'], 'date': ['2011'], 'volume': ['63'], 'issue': ['4'], 'spage': ['607'], 'epage': ['621'], 'aulast': ['J. Lorenzo'], 'aufirst': ['Perillo'], '__char_set': ['utf8']},
            {'sid': ['sfx:citation'], 'genre': ['article'], 'atitle': ['The Plot of her Undoing'], 'title': ['Feminist Art Coalition'], 'date': ['2020-12-28'], 'aulast': ['Hartman'], 'aufirst': ['Saidiya'], '__char_set': ['utf8']},
            {},
            ]
        for (i, ourl) in enumerate(self.ourls):
            parts: dict = readings_processor.parse_openurl( ourl )
            log.debug( f'parts, ``{parts}``' )
            self.assertEqual( expected[i], parts )

    def test_parse_start_page_from_ourl(self):
        expected = [ '607', '', '']
        for (i, ourl) in enumerate(self.ourls):
            parts: dict = readings_processor.parse_openurl( ourl )
            spage: str = readings_processor.parse_start_page_from_ourl( parts )
            self.assertEqual( expected[i], spage )

    def test_parse_end_page_from_ourl(self):
        expected = [ '621', '', '' ]
        for (i, ourl) in enumerate(self.ourls):
            parts: dict = readings_processor.parse_openurl( ourl )
            epage: str = readings_processor.parse_end_page_from_ourl( parts )
            self.assertEqual( expected[i], epage )

    ## end class OpenUrlParserTest()



class MapperTest( unittest.TestCase ):

    """ Checks mapping of db-resultset data to leganto fields. """

    def setUp( self ):
        self.maxDiff = None

    # def test_map_book_data(self):
    #     initial_book_data: dict = {
    #         'bibno': '',
    #         'bk_author': 'Appleman, Deborah',
    #         'bk_title': 'Critical Encounters in Secondary English: Teaching Literary '
    #                     'Theory to Adolescents ',
    #         'bk_updated': datetime.datetime(2022, 6, 16, 9, 29, 5),
    #         'bk_year': None,
    #         'bookid': 50027,
    #         'bookstore': 'N',
    #         'callno': '-',
    #         'classid': 9342,
    #         'copies': 1,
    #         'date_printed': None,
    #         'ebook_id': 112561,
    #         'edition': '',
    #         'facnotes': 'CDL linked',
    #         'isbn': '',
    #         'libloc': 'Rock',
    #         'libraryhas': 'N',
    #         'loan': '3 hrs',
    #         'needed_by': None,
    #         'personal': 'N',
    #         'printed': 'n',
    #         'publisher': '3rd edition',
    #         'purchase': 'N',
    #         'reactivateid': '20220610163908',
    #         'request_date': datetime.datetime(2020, 5, 5, 17, 24, 3),
    #         'requestid': '20200505172403authID',
    #         'requests.requestid': '20200505172403authID',
    #         'required': 'optional',
    #         'sfxlink': '',
    #         'staffnotes': '',
    #         'status': 'requested as ebook'
    #         }
    #     course_id = 'EDUC2510A'
    #     cdl_checker = CDL_Checker()
    #     mapped_book_data: dict = etl_class_data.map_book( initial_book_data, course_id, cdl_checker )
    #     expected_sorted_keys = [
    #         'citation_author',
    #         'citation_doi',
    #         'citation_end_page',
    #         'citation_isbn',
    #         'citation_issn',
    #         'citation_issue',
    #         'citation_journal_title',
    #         'citation_publication_date',
    #         'citation_secondary_type',
    #         'citation_source1',
    #         'citation_source2',
    #         'citation_source3',
    #         'citation_source4',
    #         'citation_start_page',
    #         'citation_title',
    #         'citation_volume',
    #         'coursecode',
    #         'external_system_id',
    #         'section_id'
    #         ]
    #     self.assertEqual( expected_sorted_keys, sorted(list(mapped_book_data.keys())) )
    #     expected_data = {
    #         'citation_author': 'Appleman, Deborah',
    #         'citation_doi': '',
    #         'citation_end_page': '',
    #         'citation_isbn': '',
    #         'citation_issn': '',
    #         'citation_issue': '',
    #         'citation_publication_date': '',
    #         'citation_secondary_type': 'BK',
    #         # 'citation_source1': 'CDL linked',
    #         'citation_source1': 'CDL link possibly: <https://cdl.library.brown.edu/cdl/item/b90794643>',
    #         'citation_source2': '',
    #         'citation_source3': 'no openurl found',
    #         'citation_source4': '',
    #         'citation_start_page': '',
    #         'citation_title': 'Critical Encounters in Secondary English: Teaching Literary Theory to Adolescents ',
    #         'citation_journal_title': '',
    #         'citation_volume': '',
    #         'coursecode': 'EDUC2510',
    #         'external_system_id': '20200505172403authID',
    #         'section_id': ''
    #         }
    #     self.assertEqual( expected_data, mapped_book_data )
    #     ## end def test_map_book_data()

    # def test_map_article_data(self):
    #     initial_article_data: dict = {
    #         'amount': 'y',
    #         'art_updated': datetime.datetime(2021, 1, 11, 12, 31, 4),
    #         'art_url': 'https://static1.squarespace.com/static/5c805bf0d86cc90a02b81cdc/t/5db8b219a910fa05af05dbf4/1572385305368/NotesOnFeminism-2_SaidiyaHartman.pdf',
    #         'articleid': 109044,
    #         'assignment': '',
    #         'atitle': 'The Plot of her Undoing',
    #         'aufirst': 'Saidiya',
    #         'auinit': '',
    #         'aulast': 'Hartman',
    #         'bibno': '',
    #         'bk_aufirst': '',
    #         'bk_auinit': '',
    #         'bk_aulast': '',
    #         'classid': 9756,
    #         'classuse': 'y',
    #         'copied_from_id': 108626,
    #         'date': datetime.date(2020, 12, 28),
    #         'date_due': None,
    #         'date_printed': None,
    #         'doi': '',
    #         'epage': None,
    #         'ereserve': 'web link',
    #         'facnotes': 'https://static1.squarespace.com/static/5c805bf0d86cc90a02b81cdc/t/5db8b219a910fa05af05dbf4/1572385305368/NotesOnFeminism-2_SaidiyaHartman.pdf',
    #         'fairuse': 'none',
    #         'format': 'article',
    #         'fullcit': '',
    #         'fulltext_url': '',
    #         'injosiah': 'dont know',
    #         'isbn': '',
    #         'issn': '',
    #         'issue': '',
    #         'jcallno': '',
    #         'nature': 'y',
    #         'notice': None,
    #         'original': 'y',
    #         'pmid': None,
    #         'printed': 'n',
    #         'publicdomain': 'none',
    #         'publisher': '',
    #         'reactivateid': '',
    #         'request_date': datetime.datetime(2021, 1, 11, 12, 31, 4),
    #         'requestid': '20210111123104OCRAcopy',
    #         'requests.requestid': '20210111123104OCRAcopy',
    #         'sequence': 'Week 6',
    #         'sfxlink': 'https://login.revproxy.brown.edu/login?url=http://sfx.brown.edu:8888/sfx_local?sid=sfx:citation&genre=article&atitle=The '
    #                     'Plot of her Undoing&title=Feminist Art '
    #                     'Coalition&date=2020-12-28&volume=&issue=&spage=&epage=&issn=&id=&aulast=Hartman&aufirst=Saidiya&auinit=&__char_set=utf8',
    #         'spage': None,
    #         'staff_intervention_needed': None,
    #         'staffnotes': '',
    #         'status': 'on reserve',
    #         'title': 'Feminist Art Coalition',
    #         'url_desc': '',
    #         'volume': ''}
    #     course_id = 'HMAN2401D'
    #     cdl_checker = CDL_Checker()
    #     mapped_article_data: dict = etl_class_data.map_article( initial_article_data, course_id, cdl_checker )
    #     expected_sorted_keys = [
    #         'citation_author',
    #         'citation_doi',
    #         'citation_end_page',
    #         'citation_isbn',
    #         'citation_issn',
    #         'citation_issue',
    #         'citation_journal_title',
    #         'citation_publication_date',
    #         'citation_secondary_type',
    #         'citation_source1',
    #         'citation_source2',
    #         'citation_source3',
    #         'citation_source4',
    #         'citation_start_page',
    #         'citation_title',
    #         'citation_volume',
    #         'coursecode',
    #         'external_system_id',
    #         'section_id'
    #         ]
    #     self.assertEqual( expected_sorted_keys, sorted(list(mapped_article_data.keys())) )
    #     expected_data = {
    #         'citation_author': 'Hartman, Saidiya',
    #         'citation_doi': '',
    #         'citation_end_page': '',
    #         'citation_isbn': '',
    #         'citation_issn': '',
    #         'citation_issue': '',
    #         'citation_journal_title': 'Feminist Art Coalition',
    #         'citation_publication_date': '2020-12-28',
    #         'citation_secondary_type': 'ARTICLE',
    #         'citation_source1': 'https://static1.squarespace.com/static/5c805bf0d86cc90a02b81cdc/t/5db8b219a910fa05af05dbf4/1572385305368/NotesOnFeminism-2_SaidiyaHartman.pdf',
    #         'citation_source2': 'https://static1.squarespace.com/static/5c805bf0d86cc90a02b81cdc/t/5db8b219a910fa05af05dbf4/1572385305368/NotesOnFeminism-2_SaidiyaHartman.pdf',
    #         'citation_source3': 'https://bruknow.library.brown.edu/discovery/openurl?institution=01BU_INST&vid=01BU_INST:BROWN&genre=article&atitle=The+Plot+of+her+Undoing&title=Feminist+Art+Coalition&date=2020-12-28&aulast=Hartman&aufirst=Saidiya&__char_set=utf8',
    #         'citation_source4': 'no_pdf_found',
    #         'citation_start_page': '',
    #         'citation_title': 'The Plot of her Undoing',
    #         'citation_volume': '',
    #         'coursecode': 'HMAN2401',
    #         'external_system_id': '20210111123104OCRAcopy',
    #         'section_id': ''
    #         }
    #     self.assertEqual( expected_data, mapped_article_data )
    #     ## end def test_map_article_data()

    # def test_map_excerpt_data_titles(self):
    #     """ Checks article-title and journal-title excerpt-mapping. """
    #     initial_excerpt_data: dict = { 'articleid': 117436, 'requestid': '20220404173710jdelleca', 'reactivateid': '', 'format': 'excerpt', 'aulast': '', 'aufirst': '', 'auinit': '', 'bk_aulast': 'Felix Guattari', 'bk_aufirst': 'Gilles Deleuze', 'bk_auinit': '', 'ereserve': 'has pdf', 'status': 'on reserve', 'volume': '', 'issue': '', 'publisher': '', 'date': datetime.date(1980, 1, 1), 'issn': '', 'isbn': '', 'spage': None, 'epage': None, 'assignment': '', 'art_url': '', 'url_desc': '', 'doi': '', 'publicdomain': 'none', 'fairuse': 'none', 'classuse': 'y', 'nature': 'y', 'amount': 'y', 'original': 'y', 'notice': None, 'sequence': '', 'date_due': datetime.date(1969, 12, 31), 'facnotes': '', 'staffnotes': '', 'art_updated': datetime.datetime(2022, 4, 4, 17, 45, 2), 'injosiah': 'dont know', 'jcallno': '', 'bibno': '', 'printed': 'n', 'date_printed': None, 'pmid': None, 'fullcit': '', 'fulltext_url': '', 'copied_from_id': None, 'staff_intervention_needed': None, 'requests.requestid': '20220404173710jdelleca', 'classid': 10488, 'request_date': datetime.datetime(2022, 4, 4, 17, 37, 10), 
    #     'atitle': 'Introduction: Rhizome ', 
    #     'title': 'A Thousand Plateaus', 
    #     'sfxlink': '//library.brown.edu/easyarticle/?genre=article&atitle=Introduction: Rhizome &title=A Thousand Plateaus&date=1980-01-01&volume=&issue=&spage=1&epage=25&issn=&doi=&aulast=&aufirst=&auinit=&__char_set=utf8', 
    #     }
    #     course_id = 'FOO'
    #     cdl_checker = CDL_Checker()
    #     mapped_excerpt_data: dict = etl_class_data.map_excerpt( initial_excerpt_data, course_id, cdl_checker )        
    #     self.assertEqual( '(EXCERPT) Introduction: Rhizome', mapped_excerpt_data['citation_title'] )
    #     self.assertEqual( 'A Thousand Plateaus', mapped_excerpt_data['citation_journal_title'] )

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
        self.assertEqual( expected, readings_processor.parse_excerpt_author(excerpt_db_data) )



    def test_parse_ebook_author(self):
        """ Checks parse_excerpt_author() helper's processing of various author fields. """
        ebook_db_data: dict = {
            'articleid': 43842,
            'aufirst': None,
            'auinit': None,
            'aulast': None,
            'bk_aufirst': 'Karl',
            'bk_auinit': '',
            'bk_aulast': 'Polanyi',
            }            
        expected = 'Karl Polanyi'
        self.assertEqual( expected, readings_processor.parse_ebook_author(ebook_db_data) )
        ebook_db_data: dict = { 'articleid': 108130,
            'assignment': '',
            'atitle': '',
            'aufirst': '',
            'auinit': '',
            'aulast': '',
            'bibno': '',
            'bk_aufirst': '',
            'bk_auinit': '',
            'bk_aulast': 'Pauly, Louis',
            }
        expected = 'Pauly, Louis'
        self.assertEqual( expected, readings_processor.parse_ebook_author(ebook_db_data) )


    def test_map_bruknow_openurl_a(self):
        """ Checks transformed bruknow openurl from domain-start. """
        initial_ourl_a = '//library.brown.edu/easyarticle/?genre=article&atitle=3, 4, 6, 14, 16&title=The Senses in Performance&date=2006-01-01&volume=&issue=&spage=&epage=&issn=&doi=&aulast=&aufirst=&auinit=&__char_set=utf8'
        expected = 'https://bruknow.library.brown.edu/discovery/openurl?institution=01BU_INST&vid=01BU_INST:BROWN&genre=article&atitle=3,+4,+6,+14,+16&title=The+Senses+in+Performance&date=2006-01-01&__char_set=utf8'
        self.assertEqual( 
            expected, 
            readings_processor.map_bruknow_openurl( initial_ourl_a ) 
            )

    def test_map_bruknow_openurl_b(self):
        """ Checks transformed bruknow openurl from revproxy-start. """
        initial_ourl_b = 'https://login.revproxy.brown.edu/login?url=http://sfx.brown.edu:8888/sfx_local?sid=sfx:citation&genre=article&atitle=The Plot of her Undoing&title=Feminist Art Coalition&date=2020-12-28&volume=&issue=&spage=&epage=&issn=&id=&aulast=Hartman&aufirst=Saidiya&auinit=&__char_set=utf8'
        expected = 'https://bruknow.library.brown.edu/discovery/openurl?institution=01BU_INST&vid=01BU_INST:BROWN&genre=article&atitle=The+Plot+of+her+Undoing&title=Feminist+Art+Coalition&date=2020-12-28&aulast=Hartman&aufirst=Saidiya&__char_set=utf8'
        self.assertEqual( 
            expected, 
            readings_processor.map_bruknow_openurl( initial_ourl_b ) 
            )

    ## end class MapperTest()


if __name__ == '__main__':
  unittest.main()
