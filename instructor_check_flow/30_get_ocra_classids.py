"""
- This script iterates through "json_data/oit_data_02.json" OIT-courses.
- It produces the json_file "json_data/oit_data_03.json".
- It adds one element to the data-holder-dict: a list of "ocra_class_ids" for the given course-code.
    - These ocra_class_ids will be used in the subsequent script to extract reading-list data.
"""

import datetime, json, logging, os, pprint, sys

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
# from lib.common.validate_files import is_utf8_encoded, is_tab_separated, columns_are_valid

## grab env vars ----------------------------------------------------
JSON_DATA_DIR_PATH: str = os.environ['LGNT__JSON_DATA_DIR_PATH']
log.debug( f'JSON_DATA_DIR_PATH, ``{JSON_DATA_DIR_PATH}``' )

## constants --------------------------------------------------------
JSON_DATA_SOURCE_PATH = f'{JSON_DATA_DIR_PATH}/oit_data_02.json'
JSON_DATA_OUTPUT_PATH = f'{JSON_DATA_DIR_PATH}/oit_data_03.json'
log.debug( f'JSON_DATA_SOURCE_PATH, ``{JSON_DATA_SOURCE_PATH}``' )
log.debug( f'JSON_DATA_OUTPUT_PATH, ``{JSON_DATA_OUTPUT_PATH}``' )

## controller -------------------------------------------------------

def main():
    """ Controller.
        Called by if __name__ == '__main__' """
    
    ## load source file ---------------------------------------------
    data_holder_dict = {}
    with open( JSON_DATA_SOURCE_PATH, 'r' ) as f:
        data_holder_dict = json.loads( f.read() )

    ## initialize meta ----------------------------------------------
    meta = {
        'datetime_stamp': datetime.datetime.now().isoformat(),
        'description': 'Starts with `oit_data_02.json`. Produces `oit_data_03.json`. Adds `ocra_class_ids` list to each entry. Removes OIT courses that have no OCRA class_ids.',
        'number_of_courses_below': 0,
        'number_of_courses_originally': len( data_holder_dict.items() ) - 1,  # -1 for the '__meta__' entry
        'oit_courses_removed_count': 0,
        'oit_courses_removed_list': [],
        }
    ## get class_ids from ocra --------------------------------------
    for ( i, (course_key, course_data_dict) ) in enumerate( data_holder_dict.items() ):
        log.debug( f'processing course_key, ``{course_key}``')
        if course_key == '__meta__':
            continue
        # log.debug( f'i, ``{i}``')
        # log.debug( f'course_key, ``{course_key}``' )
        # log.debug( f'course_data_dict, ``{pprint.pformat(course_data_dict)}``' )
        course_code = course_key.split( '.' )[0]
        course_number = course_key.split( '.' )[1]
        class_ids: list = get_class_id_entries( course_code, course_number )
        class_ids.sort()
        ## update data_holder_dict with class_ids -------------------
        data_holder_dict[course_key]['ocra_class_ids'] = class_ids
        ## update meta-counts ---------------------------------------
        if len(class_ids) == 0:
            log.debug( f'course_key, ``{course_key}`` has no class_ids' )
            meta['oit_courses_removed_count'] += 1
            meta['oit_courses_removed_list'].append( course_key )
        # if i > 2:
        #     break

    ## remove OIT courses that have no class_ids --------------------
    for course_key in meta['oit_courses_removed_list']:
        del data_holder_dict[course_key]
    meta['number_of_courses_below'] = len( data_holder_dict.items() ) - 1  # -1 for the '__meta__' entry

    ## update meta --------------------------------------------------
    data_holder_dict['__meta__'] = meta

    ## save class_ids data ------------------------------------------
    with open( JSON_DATA_OUTPUT_PATH, 'w' ) as f:
        jsn = json.dumps( data_holder_dict, sort_keys=True, indent=2 )
        f.write( jsn )

    return

    ## end main()


if __name__ == '__main__':
    main()
    sys.exit()
