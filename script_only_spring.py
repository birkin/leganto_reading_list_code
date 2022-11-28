"""
Main manager file to produce reading-list file of only Spring OIT-entries.
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


def make_file_of_all_spring_courses() -> None:
    """ Opens original OIT file, iterates through data, and saves only the spring courses to a new file. 
        Called by if...main: """
    log.debug( 'starting make_file_of_all_spring_courses()' )
    ## settings -----------------------------------------------------
    settings: dict = load_initial_settings()
    assert type(settings) == dict
    ## load OIT course-data -----------------------------------------
    new_file_lines = []
    input_filepath = settings['COURSES_FILEPATH']
    with open( input_filepath, 'r' ) as f:
        lines = f.readlines()
        for i, line in enumerate( lines ):
            if i == 0:
                new_file_lines.append( line )
            else:
                parts = line.split( '\t' )
                oit_course_code_part = parts[0]
                if 'spring' in oit_course_code_part:
                    new_file_lines.append( line )
    ## save new file ---------------------------------------------
    output_filepath = f'{settings["SPRING_COURSES_OUTPUT_DIRPATH"]}/spring_courses_ALL.csv'
    with open( output_filepath, 'w' ) as f:
        f.writelines( new_file_lines )
    log.debug( 'new file saved' )
    return
    
    ## end def make_file_of_all_spring_courses()


def manage_extract_all_springs() -> list:
    """ Manages extracting all spring-only courses. 
        Called by if...main: """
    log.debug( 'starting manage_extract_all_springs()' )
    ## settings -----------------------------------------------------
    settings: dict = load_initial_settings()
    assert type(settings) == dict
    ## load OIT course-data -----------------------------------------
    oit_course_loader = OIT_Course_Loader( settings['COURSES_FILEPATH'] )
    all_oit_courses = oit_course_loader.OIT_course_data
    log.debug( f'count of all_oit_courses, ``{len(all_oit_courses)}``' )
    assert type( all_oit_courses ) == list
    ## filter for spring-only courses -------------------------------
    spring_courses = []
    for course in all_oit_courses:
        assert type(course) == dict
        # log.debug( f'course, ``{pprint.pformat(course)}``' )
        if 'spring' in course['COURSE_CODE']:
            spring_courses.append( course )
    ## sort spring courses ------------------------------------------
    spring_courses.sort( key=lambda x: x['COURSE_CODE'] )
    assert type( spring_courses ) == list
    log.debug( f'count of spring_courses, ``{len(spring_courses)}``' )
    log.debug( f'sorted spring_courses (3), ``{pprint.pformat(spring_courses[0:3])}``' )
    for i, course in enumerate( spring_courses ):
        log.debug( f'course_code, ``{course["COURSE_CODE"]}``' )
        if i > 50:
            break
    return spring_courses

    ## end def manage_extract_all_springs() 


def manage_extract_initial_springs():
    """ Manages extracting unique spring-only courses (ignoring sections). 
        Called by if...main: """
    ## settings -----------------------------------------------------
    settings: dict = load_initial_settings()
    assert type(settings) == dict
    ## grab all spring courses --------------------------------------
    spring_courses = manage_extract_all_springs()
    assert type(spring_courses) == list
    ## filter for unique courses ------------------------------------
    unique_spring_courses = []
    previous_simple_course_code = 'init'
    for course in spring_courses:
        assert type(course) == dict
        oit_course_code = course['COURSE_CODE']
        log.debug( f'cour   se_code, ``{oit_course_code}``' )
        ## make simple_course_code ----------------------------------
        parts: list = oit_course_code.split('.')
        new_simple_course_code: str = parts[1].upper() + parts[2].upper()
        assert type(new_simple_course_code) == str
        # log.debug(msg=f'new_simple_course_code, ``{new_simple_course_code}``')
        if new_simple_course_code != previous_simple_course_code:
            log.debug( 'found new course' )
            unique_spring_courses.append( course )
            previous_simple_course_code = new_simple_course_code
        else:
            continue
    log.debug( '-' * 70 )
    log.debug( f'count of unique_spring_courses, ``{len(unique_spring_courses)}``' )
    log.debug( '-' * 70 )
    for i, course in enumerate( unique_spring_courses ):
        log.debug( f'course_code, ``{course["COURSE_CODE"]}``' )
        # if i > 50:
        #     break
    log.debug( '-' * 70 )
    log.debug( 'end' )
    ## prep for output ----------------------------------------------
    spring_courses_coursecodes = []
    for crs in spring_courses:
        assert type(crs) == dict
        coursecode = crs['COURSE_CODE']
        assert type(coursecode) == str
        spring_courses_coursecodes.append( coursecode )
    initial_spring_courses_coursecodes = []
    for crs in unique_spring_courses:
        assert type(crs) == dict
        coursecode = crs['COURSE_CODE']
        assert type(coursecode) == str
        initial_spring_courses_coursecodes.append( coursecode )
    jdct = {
        'meta': {
            'count_spring_courses_ALL': len(spring_courses_coursecodes),
            'count_spring_courses_UNIQUE': len(initial_spring_courses_coursecodes),
        },
        'spring_courses_ALL': spring_courses_coursecodes,
        'spring_courses_UNIQUE': initial_spring_courses_coursecodes
        }
    jsn = json.dumps( jdct, sort_keys=True, indent=2 )
    output_filepath = f'{settings["SPRING_COURSES_OUTPUT_DIRPATH"]}/spring_courses.json'
    with open( output_filepath, 'w' ) as f:
        f.write( jsn )
    return unique_spring_courses

    ## end def manage_extract_initial_springs()


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
    make_file_of_all_spring_courses()