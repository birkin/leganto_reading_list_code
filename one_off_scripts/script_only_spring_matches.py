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
    ## load settings ------------------------------------------------
    settings: dict = load_initial_settings()
    assert type(settings) == dict
    ## load OIT all-spring-only course-data -------------------------
    all_spring_courses_lines = []
    # input_filepath = settings['ALL_SPRING_COURSES_FILEPATH']
    input_filepath = f'{settings["OIT_COURSES_DIRPATH"]}/spring_courses_ALL.csv'
    with open( input_filepath, 'r' ) as f:
        all_spring_courses_lines = f.readlines()
    ## load tracker.json --------------------------------------------
    tracker_data = {}
    tracker_filepath = settings['TRACKER_JSON_FILEPATH']
    with open( tracker_filepath, 'r' ) as f:
        tracker_data = json.load(f)
    ## iterate through OIT spring-only course-data for matches ------
    match_lines = []
    for i, line in enumerate( all_spring_courses_lines ):
        assert type(line) == str, type(line)
        if i == 0:  # skip header
            match_lines.append( line )
        else:
            parts = line.split( '\t' )
            oit_course_code_part = parts[0]
            tracker_course_data = tracker_data['oit_courses_processed'][oit_course_code_part]
            assert type( tracker_course_data ) == dict
            status = tracker_course_data['status']
            if 'NO-OCRA-BOOKS/ARTICLES/EXCERPTS-FOUND' in status:
                pass
            else:
                match_lines.append( line )
    ## save new file -----------------------------------------------
    oit_spring_matches_filepath = f'{settings["OIT_COURSES_DIRPATH"]}/oit_spring_MATCHES.tsv'
    with open( oit_spring_matches_filepath, 'w' ) as f:
        f.writelines( match_lines )
    log.debug( 'ending make_file_of_existing_spring_courses()' )
    return
    
    ## end def make_file_of_existing_spring_courses()


def load_initial_settings() -> dict:
    """ Loads envar settings.
        Called by manage_build_reading_list() """
    settings = {
        'OIT_COURSES_DIRPATH': os.environ['LGNT__OIT_COURSES_DIRPATH'],
        'TRACKER_JSON_FILEPATH': os.environ['LGNT__TRACKER_JSON_FILEPATH'],
    }
    log.debug( f'settings-keys, ``{pprint.pformat( sorted(list(settings.keys())) )}``' )
    return settings


if __name__ == '__main__':
    log.debug( 'starting if()' )
    # manage_extract_all_springs()
    # manage_extract_initial_springs()
    make_file_of_existing_spring_courses()