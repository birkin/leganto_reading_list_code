"""
Main manager file to produce reading lists.
"""

import argparse, datetime, json, logging, os, pprint, sys

import gspread, pymysql
from lib import loaders
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
    # prepare_data_for_staff() 
    # prepare_data_for_leganto()
    # update_spreadsheet()
    # output_csv()

    ## end manage_build_reading_list()


def load_initial_settings() -> dict:
    """ Loads envar settings.
        Called by manage_build_reading_list() """
    settings = {
        'COURSES_FILEPATH': os.environ['LGNT__COURSES_FILEPATH'],
        'PDF_OLDER_THAN_DAYS': 30,
        ## gspread settings ---------------------
        'CREDENTIALS': json.loads( os.environ['LGNT__SHEET_CREDENTIALS_JSON'] ),
        'SPREADSHEET_NAME': os.environ['LGNT__SHEET_NAME']
    }
    settings_keys: list = list( settings.keys() )  # just for logging
    log.debug( f'settings-keys, ``{pprint.pformat( settings_keys )}``' )
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
    log.debug( f'course_id_list from spreadsheet, ``{pprint.pformat(course_id_list)}``' )
    return course_id_list





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
