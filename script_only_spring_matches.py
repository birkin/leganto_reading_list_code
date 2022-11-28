"""
Main manager file to produce reading-list file 
of only Spring OIT-entries that had matches in a recent tracker.json file.
"""

import argparse, datetime, json, logging, os, pprint, sys

import gspread, pymysql
from lib import csv_maker
from lib import db_stuff
from lib import gsheet_prepper
from lib import leganto_final_processor
from lib import loaders
from lib import readings_extractor
from lib import readings_processor
# from lib.cdl import CDL_Checker
from lib.loaders import OIT_Course_Loader


LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


def make_file_of_existing_spring_courses() -> None:
    """ Opens OIT file of only-spring-courses, iterates through data, and for each...
        - looks up course in tracker.json
        - if entry was processed, saves course to new file.
        Called by if...main: """
    log.debug( 'starting make_file_of_existing_spring_courses()' )
    ## settings -----------------------------------------------------
    settings: dict = load_initial_settings()
    assert type(settings) == dict
    ## load OIT spring-only course-data -----------------------------
    all_spring_courses_lines = []
    input_filepath = settings['SPRING_COURSES_FILEPATH']
    with open( input_filepath, 'r' ) as f:
        all_spring_courses_lines = f.readlines()
    ## load tracker.json --------------------------------------------
    tracker_data = {}
    tracker_filepath = settings['TRACKER_FILEPATH']
    with open( tracker_filepath, 'r' ) as f:
        tracker_data = json.load(f)
    ## iterate through OIT spring-only course-data for matches ------
    for line in all_spring_courses_lines:



    return
    
    ## end def make_file_of_existing_spring_courses()


def load_initial_settings() -> dict:
    """ Loads envar settings.
        Called by manage_build_reading_list() """
    settings = {
        'COURSES_FILEPATH': os.environ['LGNT__COURSES_FILEPATH'],                   # path to OIT course-data
        'SPRING_COURSES_OUTPUT_DIRPATH': os.environ['LGNT__CSV_OUTPUT_DIR_PATH'],
        # 'PDF_OLDER_THAN_DAYS': 30,                                                  # to ascertain whether to requery OCRA for pdf-data
        # 'CREDENTIALS': json.loads( os.environ['LGNT__SHEET_CREDENTIALS_JSON'] ),    # gspread setting
        # 'SPREADSHEET_NAME': os.environ['LGNT__SHEET_NAME'],                         # gspread setting
        # 'LAST_CHECKED_PATH': os.environ['LGNT__LAST_CHECKED_JSON_PATH'],            # contains last-run spreadsheet course-IDs
        # 'PDF_JSON_PATH': os.environ['LGNT__PDF_JSON_PATH'],                         # pre-extracted pdf data
        # 'FILES_URL_PATTERN': os.environ['LGNT__FILES_URL_PATTERN'],                 # pdf-url
        # 'TRACKER_JSON_FILEPATH': os.environ['LGNT__TRACKER_JSON_FILEPATH'],         # json-tracker filepath
    }
    log.debug( f'settings-keys, ``{pprint.pformat( sorted(list(settings.keys())) )}``' )
    return settings


if __name__ == '__main__':
    log.debug( 'starting if()' )
    # manage_extract_all_springs()
    # manage_extract_initial_springs()
    make_file_of_existing_spring_courses()