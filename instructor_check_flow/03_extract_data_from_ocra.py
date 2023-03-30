"""
This script iterates through "oit_subset_02.tsv" courses, and will produce the json_file "ocra_data_for_step_03.json".
- It will contain reading-list data for each of the courses in "oit_subset_02.tsv".
"""

import json, logging, os, pprint, sys

## setup logging ----------------------------------------------------
LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )

## update sys.path for project imports  -----------------------------
PROJECT_CODE_DIR = os.environ['LGNT__PROJECT_CODE_DIR']
sys.path.append( PROJECT_CODE_DIR )

## additional imports -----------------------------------------------
from lib.common.validate_oit_file import is_utf8_encoded, is_tab_separated, columns_are_valid

## grab env vars ----------------------------------------------------
CSV_OUTPUT_DIR_PATH: str = os.environ['LGNT__CSV_OUTPUT_DIR_PATH']
JSON_DATA_DIR_PATH: str = os.environ['LGNT__JSON_DATA_DIR_PATH']
# TRACKER_FILEPATH: str = os.environ['LGNT__TRACKER_FILEPATH']
log.debug( f'CSV_OUTPUT_DIR_PATH, ``{CSV_OUTPUT_DIR_PATH}``' )
log.debug( f'JSON_DATA_DIR_PATH, ``{JSON_DATA_DIR_PATH}``' )
# log.debug( f'TRACKER_FILEPATH, ``{TRACKER_FILEPATH}``' )

## constants --------------------------------------------------------
OIT_SUBSET_02_SOURCE_PATH = f'{CSV_OUTPUT_DIR_PATH}/oit_subset_02.tsv'
JSON_DATA_OUTPUT_PATH = f'{JSON_DATA_DIR_PATH}/ocra_data_for_step_03.json'
log.debug( f'OIT_SUBSET_02_SOURCE_PATH, ``{OIT_SUBSET_02_SOURCE_PATH}``' )
log.debug( f'JSON_DATA_OUTPUT_PATH, ``{JSON_DATA_OUTPUT_PATH}``' )

## controller -------------------------------------------------------

def main():
    """ Controller.
        Called by if __name__ == '__main__' """
    
    ## validate source-file -----------------------------------------
    assert is_utf8_encoded(OIT_SUBSET_02_SOURCE_PATH) == True
    assert is_tab_separated(OIT_SUBSET_02_SOURCE_PATH) == True
    assert columns_are_valid(OIT_SUBSET_02_SOURCE_PATH) == True

    ## load oit-subset-02 file --------------------------------------
    lines = []
    with open( OIT_SUBSET_02_SOURCE_PATH, 'r' ) as f:
        lines = f.readlines()

    ## get heading and data lines -----------------------------------
    heading_line = lines[0]
    parts = heading_line.split( '\t' )
    data_lines = lines[1:]

    ## build course_code.couse_number dict ---------------------------
    data_holder_dict = {}
    for line in data_lines:
        parts = line.split( '\t' )
        parts = [ part.strip() for part in parts ]
        # log.debug( f'parts, ``{pprint.pformat(parts)}``' )
        course_id = parts[0]                                # eg 'brown.anth.0850.2023-summer.s01'
        course_id_segment = course_id.split( '-' )[0]       # 'brown.anth.0850.2023'
        course_id_parts = course_id_segment.split( '.' )
        course_code = course_id_parts[1]                    # 'anth'
        course_number = course_id_parts[2]                  # '0850'
        course_key = f'{course_code}.{course_number}'
        all_instructors_string: list = parts[27]            # 'ALL_INSTRUCTORS'
        log.debug( f'all_instructors_string, ``{all_instructors_string}``' )
        all_instructors: list = all_instructors_string.split( ',' )
        if len( all_instructors ) > 1:
            log.debug( f'found multiple instructors for course {course_id}' )
        course_parts_dict = {
            'oit_course_id': course_id,
            'oit_course_title': parts[1],                   # 'COURSE_TITLE'
            'oit_all_instructors': all_instructors
        }
        data_holder_dict[course_key] = course_parts_dict
    log.debug( f'data_holder_dict, ``{pprint.pformat(data_holder_dict)}``' )    

    1/0

    ## get class_ids from ocra --------------------------------------
    ocra_data = {}

    ## with class_ids, get reading-list data ------------------------

    ## filter out invalid ocra instructors --------------------------

    ## save ocra_data -----------------------------------------------
    json_filepath = f'{CSV_OUTPUT_DIR_PATH}/ocra_data_for_step_03.json'
    with open( json_filepath, 'w' ) as f:
        json.dump( ocra_data, f, indent=2 )
    log.debug( f'json_filepath, ``{json_filepath}``' )

    return


if __name__ == '__main__':
    main()
    sys.exit()
