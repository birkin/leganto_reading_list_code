import argparse, datetime, json, logging, os, pprint, sys
import urllib.parse

import gspread
import pymysql
import pymysql.cursors
from fuzzywuzzy import fuzz


LOG_PATH: str = os.environ['LGNT__LOG_PATH']

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)


HOST = os.environ['LGNT__DB_HOST']
USERNAME = os.environ['LGNT__DB_USERNAME']
PASSWORD = os.environ['LGNT__DB_PASSWORD']
DB = os.environ['LGNT__DB_DATABASE_NAME']
#
CDL_USERNAME = os.environ['LGNT__CDL_DB_USERNAME']
CDL_PASSWORD = os.environ['LGNT__CDL_DB_PASSWORD']
CDL_DB = os.environ['LGNT__CDL_DB_DATABASE_NAME']


LEGANTO_HEADINGS: dict = {
    'coursecode': '',
    'section_id': '',
    'citation_secondary_type': '',
    'citation_title': '',
    'citation_author': '',
    'citation_publication_date': '',
    'citation_doi': '',
    'citation_isbn': '',
    'citation_issn': '',
    'citation_volume': '',
    'citation_issue': '',
    'citation_start_page': '',
    'citation_end_page': '',
    'citation_source1': '',
    'citation_source2': '',
    'external_system_id': ''
}

CREDENTIALS: dict = json.loads( os.environ['LGNT__SHEET_CREDENTIALS_JSON'] )
SPREADSHEET_NAME = os.environ['LGNT__SHEET_NAME']

LAST_CHECKED_PATH: str = os.environ['LGNT__LAST_CHECKED_JSON_PATH']


def manage_build_reading_list( raw_course_id: str, force: bool ):
    """ Manages db-querying, assembling, and posting to gsheet. 
        Called by if...main: """
    log.debug( f'raw course_id, ``{raw_course_id}``; force, ``{force}``')
    ## setup --------------------------------------------------------
    all_results: list = []
    courses_and_classes: list = []
    course_id_list = []
    cdl_checker = CDL_Checker()
    ## make course-id list ------------------------------------------
    if raw_course_id == 'SPREADSHEET':
        course_id_list: list = get_list_from_spreadsheet()
        if force:
            log.debug( 'skipping recent-updates check' )
        else:
            ## check for recent updates ---------------------------------
            recent_updates: bool = check_for_updates( course_id_list )
            if recent_updates == False:
                log.debug( 'no recent updates; quitting' )
                return        
            else:
                log.debug( 'recent updates found' )
    else:
        course_id_list: list = raw_course_id.split( ',' )
    for course_id_entry in course_id_list:
        class_id: str = get_class_id( course_id_entry )
        class_id_dict: dict = { 'course_id': course_id_entry, 'class_id': class_id }
        courses_and_classes.append( class_id_dict )
    ## process class-id-list ----------------------------------------
    for class_id_entry in courses_and_classes:
        assert type(class_id_entry) == dict
        log.debug( f'class_id_entry, ``{class_id_entry}``' )
        class_id: str = class_id_entry['class_id']
        course_id: str = class_id_entry['course_id']
        if class_id:
            book_results: list = get_book_readings( class_id )
            article_results: list = get_article_readings( class_id )

            log.debug( '--- starting excerpt query ---' )
            excerpt_results: list = get_excerpt_readings( class_id )  # only logging this for now
            log.debug( f'excerpt_results, ``{pprint.pformat(excerpt_results)}``' )
            log.debug( '--- end excerpt query ---' )

            leg_books: list = map_books( book_results, course_id, cdl_checker )
            leg_articles: list = map_articles( article_results, course_id, cdl_checker )

            leg_excerpts: list = map_excerpts( excerpt_results, course_id, cdl_checker )

            all_course_results: list = leg_books + leg_articles + leg_excerpts
            if all_course_results == []:
                all_course_results: list = [ map_empty(course_id) ]
        else:
            all_course_results: list = [ map_empty(course_id) ]
        log.debug( f'all_course_results, ``{all_course_results}``' )
        all_results = all_results + all_course_results
        log.debug( f'all_results, ``{pprint.pformat(all_results)}``' )
    ## post to google-sheet -----------------------------------------
    update_gsheet( all_results )
    ## end manage_build_reading_list()


## helpers ----------------------------------------------------------


def check_for_updates( course_id_list ) -> bool:
    """ Checks if there have been new updates.
        Can't calculate this by checking `sheet.lastUpdateTime`, because any run _will_ create a recent spreadsheet update.
        So, plan is to look at the root-page columns and compare it agains a saved json file.
        Called by manage_build_reading_list() """
    log.debug( 'course_id_list, ``{pprint.pformat(course_id_list)}``' )
    last_saved_list = []
    new_updates = False
    ## load last-saved file -----------------------------------------
    last_saved_list = []
    with open( LAST_CHECKED_PATH, 'r' ) as f_reader:
        jsn_list = f_reader.read()
        last_saved_list = json.loads( jsn_list )
        log.debug( f'last_saved_list from disk, ``{pprint.pformat(last_saved_list)}``' )
    if last_saved_list == course_id_list:
        log.debug( f'was _not_ recently updated')
    else:
        new_updates = True
        jsn = json.dumps( course_id_list, indent=2 )
        with open( LAST_CHECKED_PATH, 'w' ) as f_writer:
            f_writer.write( jsn )
        log.debug( 'new updates found and saved' )
    log.debug( f'new_updates, ``{new_updates}``' )
    return new_updates


def get_list_from_spreadsheet() -> list:
    """ Builds course-id-list from spreadsheet.
        Called by manage_build_reading_list() """
    credentialed_connection = gspread.service_account_from_dict( CREDENTIALS )
    sheet = credentialed_connection.open( SPREADSHEET_NAME )
    wrksheet = sheet.worksheet( 'course_ids_to_check' )
    list_of_dicts: list = wrksheet.get_all_records()
    log.debug( f'list_of_dicts, ``{pprint.pformat(list_of_dicts)}``' )
    course_id_list: list = []
    for dct in list_of_dicts:
        course_id: str = dct['course_id']
        course_id_list.append( course_id )
    return course_id_list


def get_class_id( course_id: str ) -> str:
    """ Finds class_id from given course_id.
        Called by manage_build_reading_list() """
    class_id: str = 'init'
    ## split the id -------------------------------------------------
    db_connection = get_db_connection()
    split_position: int = 0
    for ( i, character ) in enumerate( course_id ): 
        if character.isalpha():
            pass
        else:
            split_position = i
            break
    ( subject_code, course_code ) = ( course_id[0:split_position], course_id[split_position:] ) 
    log.debug( f'subject_code, ``{subject_code}``; course_code, ``{course_code}``' )
    ## run query to get class_id ------------------------------------
    sql = f"SELECT * FROM `banner_courses` WHERE `subject` LIKE '{subject_code}' AND `course` LIKE '{course_code}' ORDER BY `banner_courses`.`term` DESC"
    log.debug( f'sql, ``{sql}``' )
    result_set: list = []
    with db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor.execute( sql )
            result_set = list( db_cursor.fetchall() )  # list() only needed for pylance type-checking
            assert type(result_set) == list
    log.debug( f'result_set, ``{result_set}``' )
    if result_set:
        recent_row = result_set[0]
        class_id = str( recent_row['classid'] )
    else:
        class_id = ''
    log.debug( f'class_id, ``{class_id}``' )
    return class_id


def get_book_readings( class_id: str ) -> list:
    db_connection = get_db_connection()
    sql = f"SELECT * FROM reserves.books, reserves.requests WHERE books.requestid = requests.requestid AND classid = {int(class_id)} ORDER BY `books`.`bk_title` ASC"
    log.debug( f'sql, ``{sql}``' )
    result_set: list = []
    with db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor.execute( sql )
            result_set = list( db_cursor.fetchall() )
            assert type(result_set) == list
    log.debug( '\n\n----------\nbooks\n----------' )
    for entry in result_set:
        log.debug( f'\n\nbook, ``{entry}``')
    log.debug( '\n\n----------' )
    return result_set


def get_article_readings( class_id: str ) -> list:
    db_connection = get_db_connection()
    sql = f"SELECT * FROM reserves.articles, reserves.requests WHERE articles.requestid = requests.requestid AND classid = {int(class_id)} AND format = 'article' AND articles.requestid = requests.requestid AND articles.status != 'volume on reserve' AND articles.status != 'purchase requested' ORDER BY `articles`.`atitle` ASC"
    log.debug( f'sql, ``{sql}``' )
    result_set: list = []
    with db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor.execute( sql )
            result_set = list( db_cursor.fetchall() )
            assert type(result_set) == list
    log.debug( '\n\n----------\narticles\n----------' )
    for entry in result_set:
        log.debug( f'\n\narticle, ``{entry}``')
        if entry['doi'][0:1] == ' ':
            log.debug( 'cleaning doi' )
            entry['doi'] = entry['doi'].strip()
    log.debug( '\n\n----------' )
    return result_set


def get_excerpt_readings( class_id: str ) -> list:
    db_connection = get_db_connection()
    sql = f"SELECT * FROM reserves.articles, reserves.requests WHERE requests.classid = {int(class_id)} AND format = 'excerpt' AND articles.requestid = requests.requestid AND articles.status != 'volume on reserve' AND articles.status != 'purchase requested' ORDER BY `articles`.`atitle` ASC;"
    log.debug( f'sql, ``{sql}``' )
    result_set: list = []
    with db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor.execute( sql )
            result_set = list( db_cursor.fetchall() )
            assert type(result_set) == list
    log.debug( '\n\n----------\nexcerpts\n----------' )
    for entry in result_set:
        log.debug( f'\n\nexcerpt, ``{entry}``')
    log.debug( '\n\n----------' )
    return result_set


## mappers and parsers ----------------------------------------------


def map_books( book_results: list, course_id: str, cdl_checker ) -> list:
    mapped_books = []
    for book_result in book_results:
        mapped_book: dict = map_book( book_result, course_id, cdl_checker )
        mapped_books.append( mapped_book )
    return mapped_books


def map_book( initial_book_data: dict, course_id: str, cdl_checker ) -> dict:
    log.debug( f'initial_book_data, ``{initial_book_data}``' )
    mapped_book_data = LEGANTO_HEADINGS.copy()
    mapped_book_data['citation_author'] = initial_book_data['bk_author']
    mapped_book_data['citation_isbn'] = initial_book_data['isbn']
    mapped_book_data['citation_publication_date'] = str(initial_book_data['bk_year']) if initial_book_data['bk_year'] else ''
    mapped_book_data['citation_secondary_type'] = 'BK'
    # mapped_book_data['citation_source1'] = initial_book_data['facnotes']  # sometimes 'CDL Linked', 'Ebook on reserve', ''
    mapped_book_data['citation_source1'] = run_book_cdl_check( initial_book_data['facnotes'], initial_book_data['bk_title'], cdl_checker )
    mapped_book_data['citation_title'] = initial_book_data['bk_title']
    mapped_book_data['coursecode'] = f'{course_id[0:8]}'
    mapped_book_data['external_system_id'] = initial_book_data['requests.requestid']
    mapped_book_data['section_id'] = course_id[8:] if len(course_id) > 8 else ''
    log.debug( f'mapped_book_data, ``{pprint.pformat(mapped_book_data)}``' )
    return mapped_book_data


def map_empty( course_id: str ) -> dict:
    mapped_book_data = LEGANTO_HEADINGS.copy()
    mapped_book_data['coursecode'] = f'{course_id[0:8]}'
    mapped_book_data['section_id'] = course_id[8:] if len(course_id) > 8 else ''
    return mapped_book_data


def map_articles( article_results: list, course_id: str, cdl_checker ) -> list:
    mapped_articles = []
    for article_result in article_results:
        mapped_article: dict = map_article( article_result, course_id, cdl_checker )
        mapped_articles.append( mapped_article )
    return mapped_articles


def map_article( initial_article_data: dict, course_id: str, cdl_checker ) -> dict:
    log.debug( f'initial_article_data, ``{pprint.pformat(initial_article_data)}``' )
    mapped_article_data = LEGANTO_HEADINGS.copy()
    ourl_parts: dict = parse_openurl( initial_article_data['sfxlink'] )
    mapped_article_data['citation_author'] = f'{initial_article_data["aulast"]}, {initial_article_data["aufirst"]}'
    mapped_article_data['citation_doi'] = initial_article_data['doi']
    mapped_article_data['citation_end_page'] = str(initial_article_data['epage']) if initial_article_data['epage'] else parse_end_page_from_ourl( ourl_parts )
    mapped_article_data['citation_issn'] = initial_article_data['issn']
    mapped_article_data['citation_issue'] = initial_article_data['issue']
    mapped_article_data['citation_publication_date'] = str( initial_article_data['date'] )
    mapped_article_data['citation_secondary_type'] = 'ARTICLE'  # guess
    mapped_article_data['citation_source1'] = run_article_cdl_check( initial_article_data['facnotes'], initial_article_data['atitle'], cdl_checker )
    mapped_article_data['citation_source2'] = initial_article_data['art_url']  
    mapped_article_data['citation_start_page'] = str(initial_article_data['spage']) if initial_article_data['spage'] else parse_start_page_from_ourl( ourl_parts )
    mapped_article_data['citation_title'] = initial_article_data['title']
    mapped_article_data['citation_volume'] = initial_article_data['volume']
    mapped_article_data['coursecode'] = f'{course_id[0:8]}'
    mapped_article_data['external_system_id'] = initial_article_data['requests.requestid']
    mapped_article_data['section_id'] = course_id[8:] if len(course_id) > 8 else ''
    log.debug( f'mapped_article_data, ``{pprint.pformat(mapped_article_data)}``' )
    return mapped_article_data




def map_excerpts( excerpt_results: list, course_id: str, cdl_checker ) -> list:
    mapped_articles = []
    for excerpt_result in excerpt_results:
        mapped_excerpt: dict = map_excerpt( excerpt_result, course_id, cdl_checker )
        mapped_articles.append( mapped_excerpt )
    return mapped_articles



def map_excerpt( initial_excerpt_data: dict, course_id: str, cdl_checker ) -> dict:
    log.debug( f'initial_excerpt_data, ``{pprint.pformat(initial_excerpt_data)}``' )
    mapped_excerpt_data = LEGANTO_HEADINGS.copy()
    ourl_parts: dict = parse_openurl( initial_excerpt_data['sfxlink'] )
    # mapped_excerpt_data['citation_author'] = f'{initial_excerpt_data["aulast"]}, {initial_excerpt_data["aufirst"]}'
    mapped_excerpt_data['citation_author'] = parse_excerpt_author( initial_excerpt_data )
    mapped_excerpt_data['citation_doi'] = initial_excerpt_data['doi']
    mapped_excerpt_data['citation_end_page'] = str(initial_excerpt_data['epage']) if initial_excerpt_data['epage'] else parse_end_page_from_ourl( ourl_parts )
    mapped_excerpt_data['citation_issn'] = initial_excerpt_data['issn']
    mapped_excerpt_data['citation_issue'] = initial_excerpt_data['issue']
    mapped_excerpt_data['citation_publication_date'] = str( initial_excerpt_data['date'] )
    mapped_excerpt_data['citation_secondary_type'] = 'ARTICLE'  # guess
    mapped_excerpt_data['citation_source1'] = run_article_cdl_check( initial_excerpt_data['facnotes'], initial_excerpt_data['atitle'], cdl_checker )
    mapped_excerpt_data['citation_source2'] = initial_excerpt_data['art_url']  
    mapped_excerpt_data['citation_start_page'] = str(initial_excerpt_data['spage']) if initial_excerpt_data['spage'] else parse_start_page_from_ourl( ourl_parts )
    mapped_excerpt_data['citation_title'] = f'(EXCERPT) %s' % initial_excerpt_data['title']
    mapped_excerpt_data['citation_volume'] = initial_excerpt_data['volume']
    mapped_excerpt_data['coursecode'] = f'{course_id[0:8]}'
    mapped_excerpt_data['external_system_id'] = initial_excerpt_data['requests.requestid']
    mapped_excerpt_data['section_id'] = course_id[8:] if len(course_id) > 8 else ''
    log.debug( f'mapped_excerpt_data, ``{pprint.pformat(mapped_excerpt_data)}``' )
    return mapped_excerpt_data


def parse_excerpt_author( initial_excerpt_data: dict ) -> str:
    """ Checks multiple possible fields for author info.
        Exceprts seem to have author info in multiple places; this function handles that.
        Called by map_excerpt() """
    first: str = initial_excerpt_data.get( 'aufirst', '' )
    if first == '':
        first = initial_excerpt_data.get( 'bk_aufirst', '' )
    last: str = initial_excerpt_data.get( 'aulst', '' )
    if last == '':
        last = initial_excerpt_data.get( 'bk_aulast', '' )
    name = f'{last}, {first}'
    if name.strip() == ',':
        name = 'author_not_found'
    log.debug( f'name, ``{name}``' )
    return name



def parse_openurl( raw_ourl: str ) -> dict:
    """ Returns fielded openurl elements.
        Called by map_article() """
    log.debug( f'raw_ourl, ``{raw_ourl}``' )
    ourl_dct = {}
    if raw_ourl[0:43] == 'https://login.revproxy.brown.edu/login?url=':
        log.debug( 'removing proxy ' )
        ourl = raw_ourl[43:]
        log.debug( f'updated ourl, ``{ourl}``' )
    else:
        ourl = raw_ourl
    ourl_section: str = ourl.split( '?' )[1]
    ourl_dct: dict = urllib.parse.parse_qs( ourl_section )
    log.debug( f'ourl_dct, ``{pprint.pformat(ourl_dct)}``' )
    return ourl_dct


def parse_start_page_from_ourl( parts: dict ):
    try:
        spage = parts['spage'][0]
    except:
        spage = ''
    log.debug( f'spage, ``{spage}``' )
    return spage


def parse_end_page_from_ourl( parts: dict ):
    try:
        epage = parts['epage'][0]
    except:
        epage = ''
    log.debug( f'epage, ``{epage}``' )
    return epage


## cdl-checking -----------------------------------------------------


def run_book_cdl_check( ocra_facnotes_data: str, ocra_title: str, cdl_checker  ) -> str:
    """ Sees if data contains a CDL reference, and, if so, see if I can find one.
        Called by map_book() and map_article(). """
    field_text: str = ocra_facnotes_data
    if 'cdl' in ocra_facnotes_data.lower():
        results: list = cdl_checker.search_cdl( ocra_title )
        field_text: str = cdl_checker.prep_cdl_field_text( results )
    else:
        results: list = cdl_checker.search_cdl( ocra_title )
        field_text: str = cdl_checker.prep_cdl_field_text( results )
        log.debug( f'ADDITIONAL BOOK-CDL CHECK WOULD HAVE FOUND..., ``{field_text}``' )
    log.debug( f'field_text, ``{field_text}``' )
    return field_text


def run_article_cdl_check( ocra_facnotes_data: str, ocra_title: str, cdl_checker  ) -> str:
    """ Sees if data contains a CDL reference, and, if so, see if I can find one.
        Called by map_book() and map_article(). """
    field_text: str = ocra_facnotes_data
    if ocra_facnotes_data == '':
        results: list = cdl_checker.search_cdl( ocra_title )
        field_text: str = cdl_checker.prep_cdl_field_text( results )
        log.debug( f'ARTICLE CDL-CHECK RESULT, ``{field_text}``' )
    log.debug( f'field_text, ``{field_text}``' )
    return field_text


class CDL_Checker(object):

    def __init__( self ):
        self.CDL_TITLES: list = []

    def populate_cdl_titles( self ) -> list:
        db_connection = get_CDL_db_connection()
        sql = "SELECT * FROM `cdl_app_item` ORDER BY `title` ASC"
        log.debug( f'sql, ``{sql}``' )
        result_set: list = []
        with db_connection:
            with db_connection.cursor() as db_cursor:
                db_cursor.execute( sql )
                result_set = list( db_cursor.fetchall() )
                assert type(result_set) == list
        return result_set


    def search_cdl( self, search_title: str ) -> list:
        """ Fuzzy-searches cdl-titles, returns back score and file_name. """
        if self.CDL_TITLES == []:
            log.debug( 'populating CDL_TITLES' )
            self.CDL_TITLES = self.populate_cdl_titles()
            # log.debug( f'CDL_TITLES, ``{pprint.pformat(CDL_TITLES)}``' )
            log.debug( f'len(self.CDL_TITLES), ``{len(self.CDL_TITLES)}``' )
        matches = []
        for entry in self.CDL_TITLES:
            assert type(entry) == dict
            score: int = fuzz.ratio( search_title, entry['title'] )
            if score > 80:
                entry['fuzzy_score'] = score
                matches.append( entry )
        log.debug( f'matches, ``{pprint.pformat(matches)}``' )
        return matches

    def prep_cdl_field_text( self, entries: list ) -> str:
        result = 'no CDL link found'
        if len( entries ) == 1:
            entry = entries[0]
            if entry['fuzzy_score'] > 97:
                result = f'CDL link likely: <https://cdl.library.brown.edu/cdl/item/{entry["item_id"]}>'
            else:
                result = f'CDL link possibly: <https://cdl.library.brown.edu/cdl/item/{entry["item_id"]}>'
        elif len( entries ) > 1:
            result = 'TODO -- handle multiple possible results'
        log.debug( f'result, ``{result}``' )
        return result

    ## end class CDL_Checker()


## gsheet code ------------------------------------------------------


def update_gsheet( all_results: list ) -> None:
    """ Writes data to gsheet, then...
        - sorts the worksheets so the most recent check appears first in the worksheet list.
        - deletes checks older than the curent and previous checks.
        Called by check_bibs() """
    ## access spreadsheet -------------------------------------------
    log.debug( f'all_results, ``{pprint.pformat(all_results)}``' )
    credentialed_connection = gspread.service_account_from_dict( CREDENTIALS )
    sheet = credentialed_connection.open( SPREADSHEET_NAME )
    log.debug( f'last-updated, ``{sheet.lastUpdateTime}``' )  # not needed now, but will use it later
    ## create new worksheet ----------------------------------------
    title: str = f'check_results_{datetime.datetime.now()}'
    worksheet = sheet.add_worksheet(
        title=title, rows=100, cols=20
        )
    ## prepare range ------------------------------------------------
    headers = [
        'coursecode',
        'section_id',
        'citation_secondary_type',
        'citation_title',
        'citation_author',
        'citation_publication_date',
        'citation_doi',
        'citation_isbn',
        'citation_issn',
        'citation_volume',
        'citation_issue',
        'citation_start_page',
        'citation_end_page',
        'citation_source1',
        'citation_source2',
        'external_system_id'
        ]
    end_range_column = 'P'
    header_end_range = 'P1'
    num_entries = len( all_results )
    data_end_range: str = f'{end_range_column}{num_entries + 1}'  # the plus-1 is for the header-row
    ## prepare data -------------------------------------------------
    data_values = []
    for entry in all_results:
        row = [
            entry['coursecode'],
            entry['section_id'],
            entry['citation_secondary_type'],
            entry['citation_title'],
            entry['citation_author'],
            entry['citation_publication_date'],
            entry['citation_doi'],
            entry['citation_isbn'],
            entry['citation_issn'],
            entry['citation_volume'],
            entry['citation_issue'],
            entry['citation_start_page'],
            entry['citation_end_page'],
            entry['citation_source1'],
            entry['citation_source2'],
            entry['external_system_id']
            ]
        data_values.append( row )
    log.debug( f'data_values, ``{data_values}``' )
    log.debug( f'data_end_range, ``{data_end_range}``' )
    new_data = [
        { 
            'range': f'A1:{header_end_range}',
            'values': [ headers ]
        },
        {
            'range': f'A2:{data_end_range}',
            'values': data_values
        }

    ]
    log.debug( f'new_data, ``{pprint.pformat(new_data)}``' )
    ## update values ------------------------------------------------
    1/0
    worksheet.batch_update( new_data, value_input_option='raw' )
    # worksheet.batch_update( new_data, value_input_option='USER_ENTERED' )
    ## update formatting --------------------------------------------
    worksheet.format( f'A1:{end_range_column}1', {'textFormat': {'bold': True}} )
    worksheet.freeze( rows=1, cols=None )
    ## re-order worksheets so most recent is 2nd --------------------
    wrkshts: list = sheet.worksheets()
    log.debug( f'wrkshts, ``{wrkshts}``' )
    reordered_wrkshts: list = [ wrkshts[0], wrkshts[-1] ]
    log.debug( f'reordered_wrkshts, ``{reordered_wrkshts}``' )
    sheet.reorder_worksheets( reordered_wrkshts )
    ## delete old checks (keeps current and previous) ---------------
    num_wrkshts: int = len( wrkshts )
    log.debug( f'num_wrkshts, ``{num_wrkshts}``' )
    if num_wrkshts > 3:  # keep requested_checks, and two recent checks
        wrkshts: list = sheet.worksheets()
        wrkshts_to_delete = wrkshts[3:]
        for wrksht in wrkshts_to_delete:
            sheet.del_worksheet( wrksht )
    return

    ## end def update_gsheet()


## -- misc helpers --------------------------------------------------


def get_db_connection():
    db_connection = pymysql.connect(  ## the with auto-closes the connection on any problem
            host=HOST,
            user=USERNAME,
            password=PASSWORD,
            database=DB,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor )  # DictCursor means results will be dictionaries (yay!)
    log.debug( f'made db_connection with PyMySQL.connect(), ``{db_connection}``' )
    return db_connection


def get_CDL_db_connection():  # yes, yes, i should obviously refactor these two
    db_connection = pymysql.connect(  ## the with auto-closes the connection on any problem
            host=HOST,
            user=CDL_USERNAME,
            password=CDL_PASSWORD,
            database=CDL_DB,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor )  # DictCursor means results will be dictionaries (yay!)
    log.debug( f'made db_connection with PyMySQL.connect(), ``{db_connection}``' )
    return db_connection


## -- script-caller helpers -----------------------------------------


def parse_args() -> dict:
    """ Parses arguments when module called via __main__ """
    parser = argparse.ArgumentParser( description='Required: a `course_id` like `EDUC1234` (accepts multiples like `EDUC1234,HIST1234`)' )
    parser.add_argument( '--course_id', help='typically like: `EDUC1234` -- or `SPREADSHEET` to get sources from google-sheet', required=True )
    parser.add_argument( '--force', help='takes boolean False or True, used to skip spreadsheet recently-updated check', required=False )
    args: dict = vars( parser.parse_args() )
    if args == {'course_id': None, 'class_id': None}:
        parser.print_help()
        sys.exit()
    return args

if __name__ == '__main__':
    args: dict = parse_args()
    log.info( f'\n\nstarting args, ```{args}```' )
    course_id: str  = args['course_id']
    log.debug( f'course_id, ``{course_id}``' )
    force: bool = args.get( 'force', False )
    manage_build_reading_list( course_id, force )


## EOF