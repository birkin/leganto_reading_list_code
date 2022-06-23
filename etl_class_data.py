import argparse, datetime, json, logging, os, pprint, sys

import gspread
import pymysql
import pymysql.cursors


LOG_PATH: str = os.environ['LGNT__LOG_PATH']

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.info( 'logging ready' )


HOST = os.environ['LGNT__DB_HOST']
USERNAME = os.environ['LGNT__DB_USERNAME']
PASSWORD = os.environ['LGNT__DB_PASSWORD']
DB = os.environ['LGNT__DB_DATABASE_NAME']

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
    'citation_start_page': '',
    'citation_end_page': '',
    'citation_source1': '',
    'citation_source2': '',
    'external_system_id': ''
}

CREDENTIALS: dict = json.loads( os.environ['LGNT__SHEET_CREDENTIALS_JSON'] )
SPREADSHEET_NAME = os.environ['LGNT__SHEET_NAME']


def manage_build_reading_list( raw_course_id: str ):
    """ Manages db-querying, assembling, and posting to gsheet. 
        Called by if...main: """
    log.debug( f'raw course_id, ``{raw_course_id}``')
    ## setup --------------------------------------------------------
    all_results: list = []
    courses_and_classes: list = []
    ## make course-id list ------------------------------------------
    if raw_course_id == 'SPREADSHEET':
        course_id_list: list = get_list_from_spreadsheet()
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
            leg_books: list = map_books( book_results, course_id )
            leg_articles: list = map_articles( article_results, course_id )
            all_course_results: list = leg_books + leg_articles
        else:
            all_course_results: list = [ map_empty(course_id) ]
        all_results = all_results + all_course_results
    ## post to google-sheet -----------------------------------------
    update_gsheet( all_results )
    ## end manage_build_reading_list()


## helpers ----------------------------------------------------------


def get_list_from_spreadsheet() -> list:
    """ Builds course-id-list from spreadsheet.
        Called by manage_build_reading_list() """
    return ['coming']


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


## mappers ----------------------------------------------------------


def map_books( book_results: list, course_id: str ) -> list:
    mapped_books = []
    for book_result in book_results:
        mapped_book: dict = map_book( book_result, course_id )
        mapped_books.append( mapped_book )
    return mapped_books


def map_book( initial_book_data: dict, course_id: str ) -> dict:
    log.debug( f'initial_book_data, ``{initial_book_data}``' )
    mapped_book_data = LEGANTO_HEADINGS.copy()
    mapped_book_data['citation_author'] = initial_book_data['bk_author']
    mapped_book_data['citation_isbn'] = initial_book_data['isbn']
    mapped_book_data['citation_publication_date'] = str(initial_book_data['bk_year']) if initial_book_data['bk_year'] else ''
    mapped_book_data['citation_secondary_type'] = 'BK'
    mapped_book_data['citation_source1'] = initial_book_data['facnotes']  # sometimes 'CDL Linked', 'Ebook on reserve', ''
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


def map_articles( article_results: list, course_id: str ) -> list:
    mapped_articles = []
    for article_result in article_results:
        mapped_article: dict = map_article( article_result, course_id )
        mapped_articles.append( mapped_article )
    return mapped_articles


def map_article( initial_article_data: dict, course_id: str ) -> dict:
    log.debug( f'initial_article_data, ``{initial_article_data}``' )
    mapped_article_data = LEGANTO_HEADINGS.copy()

    mapped_article_data['citation_author'] = f'{initial_article_data["aulast"]}, {initial_article_data["aufirst"]}'
    mapped_article_data['citation_doi'] = initial_article_data['doi']
    mapped_article_data['citation_end_page'] = str(initial_article_data['epage']) if initial_article_data['epage'] else ''
    mapped_article_data['citation_issn'] = initial_article_data['issn']
    # mapped_article_data['citation_publication_date'] = ''  # odd; articles don't show publication-date
    mapped_article_data['citation_secondary_type'] = 'ARTICLE'  # guess
    mapped_article_data['citation_source1'] = initial_article_data['facnotes']  # sometimes 'CDL Linked', 'Ebook on reserve', ''
    mapped_article_data['citation_source2'] = initial_article_data['art_url']  
    mapped_article_data['citation_start_page'] = str(initial_article_data['spage']) if initial_article_data['spage'] else ''
    mapped_article_data['citation_title'] = initial_article_data['title']
    mapped_article_data['coursecode'] = f'{course_id[0:8]}'
    mapped_article_data['external_system_id'] = initial_article_data['requests.requestid']
    mapped_article_data['section_id'] = course_id[8:] if len(course_id) > 8 else ''
    log.debug( f'mapped_article_data, ``{pprint.pformat(mapped_article_data)}``' )
    return mapped_article_data


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
        'citation_start_page',
        'citation_end_page',
        'citation_source1',
        'citation_source2',
        'external_system_id'
        ]
    end_range_column = 'N'
    header_end_range = 'N1'
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
    
    ## update values ------------------------------------------------
    worksheet.batch_update( new_data, value_input_option='raw' )
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


# def update_gsheet( leg_books: list, leg_articles: list ) -> None:
#     """ Writes data to gsheet, then...
#         - sorts the worksheets so the most recent check appears first in the worksheet list.
#         - deletes checks older than the curent and previous checks.
#         Called by check_bibs() """
#     log.debug( f'gsheet starting leg_books, ``{leg_books}``' )
#     log.debug( f'gsheet starting leg_articles, ``{leg_articles}``' )
#     all_results = leg_books + leg_articles
#     ## access spreadsheet -------------------------------------------
#     credentialed_connection = gspread.service_account_from_dict( CREDENTIALS )
#     sheet = credentialed_connection.open( SPREADSHEET_NAME )
#     log.debug( f'last-updated, ``{sheet.lastUpdateTime}``' )  # not needed now, but will use it later
#     ## create new worksheet ----------------------------------------
#     title: str = f'check_results_{datetime.datetime.now()}'
#     worksheet = sheet.add_worksheet(
#         title=title, rows=100, cols=20
#         )
#     ## prepare range ------------------------------------------------
#     headers = [
#         'coursecode',
#         'section_id',
#         'citation_secondary_type',
#         'citation_title',
#         'citation_author',
#         'citation_publication_date',
#         'citation_doi',
#         'citation_isbn',
#         'citation_issn',
#         'citation_start_page',
#         'citation_end_page',
#         'citation_source1',
#         'citation_source2',
#         'external_system_id'
#         ]
#     end_range_column = 'N'
#     header_end_range = 'N1'
#     num_entries = len( all_results )
#     data_end_range: str = f'{end_range_column}{num_entries + 1}'  # the plus-1 is for the header-row
#     ## prepare data -------------------------------------------------
#     data_values = []
#     for entry in all_results:
#         row = [
#             entry['coursecode'],
#             entry['section_id'],
#             entry['citation_secondary_type'],
#             entry['citation_title'],
#             entry['citation_author'],
#             entry['citation_publication_date'],
#             entry['citation_doi'],
#             entry['citation_isbn'],
#             entry['citation_issn'],
#             entry['citation_start_page'],
#             entry['citation_end_page'],
#             entry['citation_source1'],
#             entry['citation_source2'],
#             entry['external_system_id']
#             ]
#         data_values.append( row )
#     log.debug( f'data_values, ``{data_values}``' )
#     log.debug( f'data_end_range, ``{data_end_range}``' )
#     new_data = [
#         { 
#             'range': f'A1:{header_end_range}',
#             'values': [ headers ]
#         },
#         {
#             'range': f'A2:{data_end_range}',
#             'values': data_values
#         }

#     ]
    
#     ## update values ------------------------------------------------
#     worksheet.batch_update( new_data, value_input_option='raw' )
#     ## update formatting --------------------------------------------
#     worksheet.format( f'A1:{end_range_column}1', {'textFormat': {'bold': True}} )
#     worksheet.freeze( rows=1, cols=None )
#     ## re-order worksheets so most recent is 2nd --------------------
#     wrkshts: list = sheet.worksheets()
#     log.debug( f'wrkshts, ``{wrkshts}``' )
#     reordered_wrkshts: list = [ wrkshts[0], wrkshts[-1] ]
#     log.debug( f'reordered_wrkshts, ``{reordered_wrkshts}``' )
#     sheet.reorder_worksheets( reordered_wrkshts )
#     ## delete old checks (keeps current and previous) ---------------
#     num_wrkshts: int = len( wrkshts )
#     log.debug( f'num_wrkshts, ``{num_wrkshts}``' )
#     if num_wrkshts > 3:  # keep requested_checks, and two recent checks
#         wrkshts: list = sheet.worksheets()
#         wrkshts_to_delete = wrkshts[3:]
#         for wrksht in wrkshts_to_delete:
#             sheet.del_worksheet( wrksht )
#     return

#     ## end def update_gsheet()


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


## -- script-caller helpers -----------------------------------------


def parse_args() -> dict:
    """ Parses arguments when module called via __main__ """
    parser = argparse.ArgumentParser( description='Required: a `course_id` like `EDUC1234` (accepts multiples like `EDUC1234,HIST1234`)' )
    parser.add_argument( '--course_id', help='typically like: EDUC1234', required=True )
    args: dict = vars( parser.parse_args() )
    if args == {'course_id': None, 'class_id': None}:
        parser.print_help()
        sys.exit()
    return args

if __name__ == '__main__':
    args: dict = parse_args()
    log.info( f'starting args, ```{args}```' )
    course_id  = args['course_id']
    log.debug( f'course_id, ``{course_id}``' )
    manage_build_reading_list( course_id )


## EOF