"""
Main manager file to produce reading lists.
"""

import argparse, datetime, json, logging, os, pprint, sys

from lib import loaders


LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


def manage_build_reading_list( raw_course_id: str, update_ss: bool, force: bool ):
    """ Manages db-querying, assembling, and posting to gsheet. 
        Called by if...main: """
    log.debug( f'raw course_id, ``{raw_course_id}``; update_ss, ``{update_ss}``; force, ``{force}``')
    ## update dependencies if necessary -----------------------------
    err: dict = loaders.rebuild_pdf_data_if_necessary( {'days': 30} )  
    # update_OIT_course_data_if_necessary( {'days': 30} )
    # prepare_data_for_staff()
    # prepare_data_for_leganto()
    # update_spreadsheet()
    # output_csv()

    ## end manage_build_reading_list()






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
