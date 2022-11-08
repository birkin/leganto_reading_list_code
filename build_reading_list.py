"""
Main manager file to produce reading lists.
"""

import argparse, datetime, json, logging, os, pprint, sys

import gspread, pymysql
from lib import db_stuff
from lib import loaders
from lib import readings_extractor
from lib.loaders import OIT_Course_Loader


LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


def manage_build_reading_list( course_id_input: str, update_ss: bool, force: bool ):
    """ Manages db-querying, assembling, and posting to gsheet. 
        Called by if...main: """
    log.debug( f'raw course_id, ``{course_id_input}``; update_ss, ``{update_ss}``; force, ``{force}``')
    ## settings -----------------------------------------------------
    settings: dict = load_initial_settings()
    ## load/prep necessary data -------------------------------------
    err: dict = loaders.rebuild_pdf_data_if_necessary( {'days': settings["PDF_OLDER_THAN_DAYS"]} )
    if err:
        raise Exception( f'problem rebuilding pdf-json, error-logged, ``{err["err"]}``' )  
    oit_course_loader = OIT_Course_Loader( settings['COURSES_FILEPATH'] )
    ## prep course_id_list ------------------------------------------
    course_id_list: list = prep_course_id_list( course_id_input, settings )
    ## prep class-info-dicts ----------------------------------------
    classes_info: list = prep_classes_info( course_id_list, oit_course_loader )
    ## prep basic data ----------------------------------------------
    basic_data: list = prep_basic_data( classes_info )
    # prepare_data_for_staff() 
    # prepare_data_for_leganto()
    # update_spreadsheet()
    # output_csv()

    ## end manage_build_reading_list()



def prep_basic_data( classes_info: list ) -> list:
    """ Queries OCRA and builds initial data.
        Called by manage_build_reading_list() """
    for class_info_entry in classes_info:
        assert type(class_info_entry) == dict
        log.debug( f'class_info_entry, ``{class_info_entry}``' )
        class_id: str = class_info_entry['class_id']
        course_id: str = class_info_entry['course_id']
        leganto_course_id: str = class_info_entry['leganto_course_id']
        leganto_section_id: str = class_info_entry['leganto_section_code']
        leganto_course_title: str = class_info_entry['leganto_course_title']
        if class_id:
            ## ocra book data ---------------------------------------
            # book_results: list = get_book_readings( class_id )
            book_results: list = readings_extractor.get_book_readings( class_id )
            ## ocra article data ------------------------------------
            article_results: list = readings_extractor.get_article_readings( class_id )
            ## ocra excerpt data ------------------------------------
            excerpt_results: list = readings_extractor.get_excerpt_readings( class_id )
            ## leganto book data ------------------------------------            
            leg_books: list = map_books( book_results, leganto_course_id, leganto_section_id, leganto_course_title, cdl_checker )
            ## leganto article data ---------------------------------
            leg_articles: list = map_articles( article_results, course_id, leganto_course_id, cdl_checker, leganto_section_id, leganto_course_title )
            ## leganto excerpt data ---------------------------------
            leg_excerpts: list = map_excerpts( excerpt_results, course_id, leganto_course_id, cdl_checker, leganto_section_id, leganto_course_title )
            ## leganto combined data --------------------------------
            all_course_results: list = leg_books + leg_articles + leg_excerpts
            if all_course_results == []:
                all_course_results: list = [ map_empty(leganto_course_id, leganto_section_id, leganto_course_title) ]
        else:
            all_course_results: list = [ map_empty(leganto_course_id, leganto_section_id, leganto_course_title) ]
        log.debug( f'all_course_results, ``{all_course_results}``' )
        all_results = all_results + all_course_results
        log.debug( f'all_results, ``{pprint.pformat(all_results)}``' )
    log.info( f'all_results, ``{pprint.pformat(all_results)}``' )
    return all_results






def load_initial_settings() -> dict:
    """ Loads envar settings.
        Called by manage_build_reading_list() """
    settings = {
        'COURSES_FILEPATH': os.environ['LGNT__COURSES_FILEPATH'],                   # path to OIT course-data
        'PDF_OLDER_THAN_DAYS': 30,                                                  # to ascertain whether to requery OCRA for pdf-data
        'CREDENTIALS': json.loads( os.environ['LGNT__SHEET_CREDENTIALS_JSON'] ),    # gspread setting
        'SPREADSHEET_NAME': os.environ['LGNT__SHEET_NAME'],                         # gspread setting
        'LAST_CHECKED_PATH': os.environ['LGNT__LAST_CHECKED_JSON_PATH']             # contains last-run spreadsheet course-IDs
    }
    log.debug( f'settings-keys, ``{pprint.pformat( sorted(list(settings.keys())) )}``' )
    return settings


def prep_course_id_list( course_id_input: str, settings: dict ) -> list:
    """ Prepares list of courses to process from course_id_input.
        Called by manage_build_reading_list() """
    log.debug( f'course_id_input, ``{course_id_input}``' )
    course_id_list = []
    if course_id_input == 'SPREADSHEET':
        course_id_list: list = get_list_from_spreadsheet( settings )
        if force:
            log.info( 'skipping recent-updates check' )
        else:
            ## check for recent updates -----------------------------
            recent_updates: bool = check_for_updates( course_id_list, settings )
            if recent_updates == False:
                log.info( 'no recent updates' )
                course_id_list = []
            else:
                log.info( 'recent updates found' )
    else:
        course_id_list: list = course_id_input.split( ',' )
    log.debug( f'course_id_list, ``{pprint.pformat(course_id_list)}``' )
    return course_id_list


def get_list_from_spreadsheet( settings: dict ) -> list:
    """ Builds course-id-list from spreadsheet.
        Called by prep_course_id_list() """
    credentialed_connection = gspread.service_account_from_dict( settings['CREDENTIALS'] )
    sheet = credentialed_connection.open( settings['SPREADSHEET_NAME'] )
    wrksheet = sheet.worksheet( 'course_ids_to_check' )
    list_of_dicts: list = wrksheet.get_all_records()
    log.debug( f'list_of_dicts, ``{pprint.pformat(list_of_dicts)}``' )
    course_id_list: list = []
    for dct in list_of_dicts:
        # course_id: str = dct['course_id']
        course_id: str = str( dct.get('course_id', '') )
        course_id_list.append( course_id )
    course_id_list.sort()
    log.debug( f'course_id_list from spreadsheet, ``{pprint.pformat(course_id_list)}``' )
    return course_id_list


def check_for_updates( course_id_list: list, settings: dict ) -> bool:
    """ Checks if there have been new updates.
        Can't calculate this by checking `sheet.lastUpdateTime`, because any run _will_ create a recent spreadsheet update.
        So, plan is to look at the root-page columns and compare it agains a saved json file.
        Called by prep_course_id_list() """
    log.debug( f'course_id_list, ``{pprint.pformat(course_id_list)}``' )
    last_saved_list = []
    new_updates_exist = False
    ## load last-saved file -----------------------------------------
    last_saved_list = []
    with open( settings['LAST_CHECKED_PATH'], 'r' ) as f_reader:
        jsn_list = f_reader.read()
        last_saved_list: list = json.loads( jsn_list )
        log.debug( f'last_saved_list, ``{last_saved_list}``' )

        last_saved_list: list = sorted( json.loads(jsn_list) )
        log.debug( f'sorted-last_saved_list, ``{last_saved_list}``' )
        # log.debug( f'last_saved_list from disk, ``{pprint.pformat( sorted(last_saved_list) )}``' )
    if last_saved_list == course_id_list:
        log.debug( f'was _not_ recently updated')
    else:
        new_updates_exist = True
        jsn = json.dumps( course_id_list, indent=2 )
        with open( settings['LAST_CHECKED_PATH'], 'w' ) as f_writer:
            f_writer.write( jsn )
        log.debug( 'new updates found and saved' )
    log.debug( f'new_updates_exist, ``{new_updates_exist}``' )
    return new_updates_exist


def prep_classes_info( course_id_list: list, oit_course_loader: OIT_Course_Loader ) -> list:
    """ Takes list of course_ids and adds required minimal info using OIT data.
        Called by manage_build_reading_list() """
    log.debug( f'(temp) course_id_list, ``{pprint.pformat( course_id_list )}``' )
    classes_info = []
    for course_id_entry in course_id_list:  # now that we have the spreadsheet course_id_list, get necessary OIT data
        course_id_entry: str = course_id_entry
        log.debug( f'course_id_entry, ``{course_id_entry}``' )
        oit_course_data: dict = oit_course_loader.grab_oit_course_data( course_id_entry )
        log.debug( f'oit_course_data, ``{oit_course_data}``' )
        leganto_course_id: str = oit_course_data['COURSE_CODE'] if oit_course_data else f'oit_course_code_not_found_for__{course_id_entry}'
        leganto_course_title: str = oit_course_data['COURSE_TITLE'] if oit_course_data else ''
        leganto_section_code: str = oit_course_data['SECTION_ID'] if oit_course_data else ''
        class_id: str = get_class_id( course_id_entry )  # gets class-id used for db lookups.
        class_info_dict: dict = { 
            'course_id': course_id_entry, 
            'class_id': class_id, 
            'leganto_course_id': leganto_course_id,
            'leganto_course_title': leganto_course_title,
            'leganto_section_code': leganto_section_code }
        classes_info.append( class_info_dict )
    log.debug( f'classes_info, ``{pprint.pformat(classes_info)}``' )
    return classes_info


def get_class_id( course_id: str ) -> str:
    """ Finds class_id from given course_id.
        Called by manage_build_reading_list() -> prep_classes_info() """
    class_id: str = 'init'
    ## split the id -------------------------------------------------
    # db_connection = get_db_connection()
    db_connection: pymysql.connections.Connection = db_stuff.get_db_connection()  # connection configured to return rows in dictionary format
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


## -- script-caller helpers -----------------------------------------


def parse_args() -> dict:
    """ Parses arguments when module called via __main__ """
    parser = argparse.ArgumentParser( description='Required: a `course_id` like `EDUC1234` (accepts multiples like `EDUC1234,HIST1234`) -- and confirmation that the spreadsheet should actually be updated with prepared data.' )
    parser.add_argument( '-course_id', help='(required) typically like: `EDUC1234` -- or `SPREADSHEET` to get sources from google-sheet', required=True )
    parser.add_argument( '-update_ss', help='(required) takes boolean `false` or `true`, used to specify whether spreadsheet should be updated with prepared data', required=True )
    parser.add_argument( '-force', help='(optional) takes boolean `false` or `true`, used to skip spreadsheet recently-updated check', required=False )
    args: dict = vars( parser.parse_args() )
    log.info( f'\n\nSTARTING script; perceived args, ```{args}```' )
    ## do a bit of validation ---------------------------------------
    fail_check = False
    if args['course_id'] == None or len(args['course_id']) < 8:
        fail_check = True
    if args['update_ss'] == None:
        fail_check = True
    try: 
        json.loads( args['update_ss'] )
    except:
        log.exception( 'json-load of `update_ss` failed' )
        fail_check = True
    if args['force']:
        try:
            json.loads( args['force'] )
        except:
            log.exception( 'json-load of `force` failed' )
    if fail_check == True:
        parser.print_help()
        sys.exit()
    return args


if __name__ == '__main__':
    args: dict = parse_args()
    course_id: str  = args['course_id']
    update_ss: bool = json.loads( args['update_ss'] )
    force: bool = json.loads( args['force'] ) if args['force'] else False
    manage_build_reading_list( course_id, update_ss, force )
