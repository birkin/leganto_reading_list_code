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
from lib.common.query_ocra import get_class_id_entries
from lib.common.validate_files import is_utf8_encoded, is_tab_separated, columns_are_valid

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

    ## build course_code.course_number dict -------------------------
    data_holder_dict = build_data_holder_dict( data_lines )

    ## get class_ids from ocra --------------------------------------
    count_items = len( data_holder_dict.items() )
    oit_courses_processed = 0  
    count_ocra_courses_with_classes = 0
    count_ocra_courses_without_classes = 0
    list_of_found_oit_courses = []
    for ( i, (course_key, course_data_dict) ) in enumerate( data_holder_dict.items() ):
        log.debug( f'processing course_key, ``{course_key}``')
        # log.debug( f'i, ``{i}``')
        # log.debug( f'course_key, ``{course_key}``' )
        # log.debug( f'course_data_dict, ``{pprint.pformat(course_data_dict)}``' )
        course_code = course_key.split( '.' )[0]
        course_number = course_key.split( '.' )[1]
        class_ids: list = get_class_id_entries( course_code, course_number )
        class_ids.sort()
        ## update data_holder_dict with class_ids -------------------
        data_holder_dict[course_key]['ocra_class_ids'] = class_ids
        ## update analyses ------------------------------------------
        if len(class_ids) > 0:
            count_ocra_courses_with_classes += 1
            list_of_found_oit_courses.append( course_key )
        else:
            count_ocra_courses_without_classes += 1
        oit_courses_processed += 1
        # if i > 2:
        #     break
    log.debug( f'data_holder_dict after class_ids update, ``{pprint.pformat(data_holder_dict)}``' )
    log.debug( f'count_ocra_courses_with_classes, ``{count_ocra_courses_with_classes}``' )
    log.debug( f'count_ocra_courses_without_classes, ``{count_ocra_courses_without_classes}``' )
    log.debug( f'oit_courses_processed, ``{oit_courses_processed}``')
    log.debug( f'list_of_found_oit_courses, ``{pprint.pformat(list_of_found_oit_courses)}``' )
    assert count_ocra_courses_with_classes + count_ocra_courses_without_classes == oit_courses_processed

    ## save class_ids data ------------------------------------------
    json_filepath = f'{JSON_DATA_DIR_PATH}/ocra_data_for_step_03.json'
    log.debug( f'json_filepath, ``{json_filepath}``' )
    with open( json_filepath, 'w' ) as f:
        jsn = json.dumps( data_holder_dict, sort_keys=True, indent=2 )
        f.write( jsn )

    return

    ## end main()


## helper functions -------------------------------------------------

def build_data_holder_dict( data_lines ):
    """ Builds a dict of course_code.course_number keys , with a value-dict containing some oit data.
        Example content: 
        {
            'anth.0530': {
                'oit_all_instructors': ['140454042'],
                'oit_course_id': 'brown.anth.0530.2023-summer.s01',
                'oit_course_title': 'Arch. Psychoactive Substances'
            },
            etc...
        }
        Called by main() """
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
        all_instructors_string: str = parts[27]            # 'ALL_INSTRUCTORS'
        # log.debug( f'all_instructors_string, ``{all_instructors_string}``' )
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
    return data_holder_dict

    ## end build_data_holder_dict()


if __name__ == '__main__':
    main()
    sys.exit()
