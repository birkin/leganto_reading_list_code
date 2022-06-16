import argparse, logging, os, pprint, sys

import pymysql
import pymysql.cursors


# LOG_PATH: str = os.environ['LGNT__LOG_PATH']

logging.basicConfig(
    # filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.info( 'logging ready' )


TEST_SELECT_QUERY = 'SELECT * FROM `books` LIMIT 10'

HOST = os.environ['LGNT__DB_HOST']
USERNAME = os.environ['LGNT__DB_USERNAME']
PASSWORD = os.environ['LGNT__DB_PASSWORD']
DB = os.environ['LGNT__DB_DATABASE_NAME']


def manage_build_reading_list( course_id: str, class_id: str ):
    """ Manages db-querying, assembling, and posting to gsheet. 
        Called by if...main: """
    log.debug( f'course_id, ``{course_id}``')
    log.debug( f'class_id, ``{class_id}``')

    ## if course_id, get class_id -----------------------------------
    if course_id and not class_id:
        found_class_id: str = get_class_id( course_id )
        log.debug( f'found_class_id, ``{found_class_id}``' )
        class_id = found_class_id

    ## get books ----------------------------------------------------
    book_results = get_book_readings( class_id )

    ## get articles -------------------------------------------------
    article_results = get_article_readings( class_id )

    ## get excerpts -------------------------------------------------
    excerpt_results = get_excerpt_readings( class_id )

    ## post to google-sheet -----------------------------------------

    ## end manage_build_reading_list()


def get_class_id( course_id: str ) -> str:
    """ Finds class_id from given course_id.
        Called by manage_build_reading_list() """
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
    recent_row = result_set[0]
    class_id: str = str( recent_row['classid'] )
    log.debug( f'class_id, ``{class_id}``' )
    return class_id


def get_book_readings( class_id: str ):
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


def get_article_readings( class_id: str ):
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


def get_excerpt_readings( class_id: str ):
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
    parser = argparse.ArgumentParser( description='Required: either a `course_id` like EDUC1234, or a `class_id`' )
    parser.add_argument( '--course_id', help='typically like: EDUC1234', required=False )
    parser.add_argument( '--class_id', help='', required=False )
    args: dict = vars( parser.parse_args() )
    if args == {'course_id': None, 'class_id': None}:
        parser.print_help()
        sys.exit()
    return args

if __name__ == '__main__':
    args: dict = parse_args()
    log.info( f'starting args, ```{args}```' )
    course_id: str = args['course_id']
    class_id: str = args['class_id']
    manage_build_reading_list( course_id, class_id )




# try:
#     with pymysql.connect(  ## the with auto-closes the connection on any problem
#         host=HOST,
#         user=USERNAME,
#         password=PASSWORD,
#         database=DB,
#         charset='utf8mb4',
#         cursorclass=pymysql.cursors.DictCursor ) as db_connection:  # DictCursor means results will be dictionaries (yay!)
#         print( f'made db_connection with PyMySQL.connect(), ``{db_connection}``' )
#         db_cursor = db_connection.cursor()

#         # db_cursor.execute( TEST_SELECT_QUERY )
#         db_cursor.execute( "SELECT * FROM `banner_courses` WHERE `subject` LIKE 'EDUC' AND `course` LIKE '2510A' ORDER BY `banner_courses`.`term` DESC" )
#         result_set = db_cursor.fetchall()
#         for x in result_set:
#             assert type( x ) == dict
#             print( f'entry, ``{x}``' )

# except Exception as e:
#     # log.exception( 'problem somewhere; traceback follows' )
#     print( f'could not make db_connection with PyMySQL.connect(); error, ``{e}``' )


## EOF