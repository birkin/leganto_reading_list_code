"""
- This script iterates through "json_data/oit_data_03.json" OIT-courses.
- It produces the json_file "json_data/oit_data_03b.json".
- It adds OCRA instructor-emails to each OIT-course class_id entry.
- It removes OIT-courses where none of the OIT-instructor-emails match any of the OCRA-instructor-emails.
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
from lib.common import query_ocra 

## grab env vars ----------------------------------------------------
JSON_DATA_DIR_PATH: str = os.environ['LGNT__JSON_DATA_DIR_PATH']
log.debug( f'JSON_DATA_DIR_PATH, ``{JSON_DATA_DIR_PATH}``' )

## constants --------------------------------------------------------
JSON_DATA_SOURCE_PATH = f'{JSON_DATA_DIR_PATH}/oit_data_03.json'
JSON_DATA_OUTPUT_PATH = f'{JSON_DATA_DIR_PATH}/oit_data_03b.json'
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
        'description': 'Starts with `oit_data_03.json`. Produces `oit_data_03.bjson`. Adds ocra-instructor-emails to each course-entry class_id. Removes OIT courses that have no intersection between any oit-instructor and any ocra-instructor.',
        'number_of_courses_below': 0,
        'number_of_courses_originally': len( data_holder_dict.items() ) - 1,  # -1 for the '__meta__' entry
        'oit_courses_removed_count': 0,
        'oit_courses_removed_list': [],  # make this list like { course_key: {'oit_instructors': [], 'ocra_instructors': []}, etc... }
        }
    
    ## get instructor-emails from ocra ------------------------------
    for ( i, (course_key, course_data_dict) ) in enumerate( data_holder_dict.items() ):
        log.debug( f'processing course_key, ``{course_key}``')
        # log.debug( f'i, ``{i}``')
        # log.debug( f'course_key, ``{course_key}``' )
        # log.debug( f'course_data_dict, ``{pprint.pformat(course_data_dict)}``' )
        if course_key == '__meta__':
            continue
        ## get oit email addresses ----------------------------------
        oit_email_addresses = course_data_dict['oit_email_addresses']
        oit_email_addresses = [ email.strip().lower() for email in course_data_dict['oit_email_addresses'] ]
        course_data_dict['oit_email_addresses'] = oit_email_addresses  # storing the lowercased versions
        ## get class_ids --------------------------------------------
        class_ids = course_data_dict['ocra_class_ids']
        ## loop through class_ids -----------------------------------
        class_id_to_ocra_instructor_email_map = {}
        course_data_dict['ocra_class_ids_with_oit_instructor_match'] = []
        for class_id in class_ids:
            ## get instructor-emails from ocra ----------------------
            ocra_instructor_emails = query_ocra.get_ocra_instructor_email_from_classid( class_id )  # probably just one email, but I don't know
            if len( ocra_instructor_emails ) > 1:
                log.warning( f'whoa, more than one ocra_instructor_emails found for class_id, ``{class_id}``' )
            ocra_instructor_email = ocra_instructor_emails[0] if len(ocra_instructor_emails) > 0 else None
            ## create_map -------------------------------------------
            if ocra_instructor_email is not None:
                class_id_to_ocra_instructor_email_map[class_id] = ocra_instructor_email.strip().lower()
        ## update data_holder_dict with instructor-emails -----------
        course_data_dict['ocra_class_id_to_instructor_email_map'] = class_id_to_ocra_instructor_email_map
        ## look for matches -----------------------------------------
        ocra_class_id_to_instructor_email_map_for_matches = {}
        for (class_id, ocra_instructor_email) in class_id_to_ocra_instructor_email_map.items():
            if ocra_instructor_email is None:
                continue
            for oit_email in oit_email_addresses:
                if ocra_instructor_email == oit_email:
                    ocra_class_id_to_instructor_email_map_for_matches[class_id] = ocra_instructor_email
        data_holder_dict[course_key]['ocra_class_id_to_instructor_email_map_for_matches'] = ocra_class_id_to_instructor_email_map_for_matches
        # if i > 2:
        #     break

    ## remove courses that have no matches --------------------------
    filtered_data_holder_dict = {}
    for ( i, (course_key, course_data_dict) ) in enumerate( data_holder_dict.items() ):
        if course_key == '__meta__':
            continue
        ocra_class_id_to_instructor_email_map_for_matches = course_data_dict['ocra_class_id_to_instructor_email_map_for_matches']
        if len(ocra_class_id_to_instructor_email_map_for_matches) > 0:
            filtered_data_holder_dict[course_key] = course_data_dict
        else:
            removal_dict = { course_key: course_data_dict }
            meta['oit_courses_removed_list'].append( removal_dict )
            meta['oit_courses_removed_count'] += 1
        # if i > 2:
        #     break

    ## update meta --------------------------------------------------
    meta['number_of_courses_originally'] = len( data_holder_dict.items() ) - 1  # -1 for the '__meta__' entry
    meta['number_of_courses_below'] = len( filtered_data_holder_dict.items() )  # meta hasn't been added yet
    filtered_data_holder_dict['__meta__'] = meta

    ## save class_ids data ------------------------------------------
    with open( JSON_DATA_OUTPUT_PATH, 'w' ) as f:
        jsn = json.dumps( filtered_data_holder_dict, sort_keys=True, indent=2 )
        f.write( jsn )

    return

    ## end main()


if __name__ == '__main__':
    main()
    sys.exit()


## scratch-pad... ---------------------------------------------------

# for email in instructor_emails:
#     if email not in course_data_dict['ocra_unique_instructor_emails']:
#         course_data_dict['ocra_unique_instructor_emails'].append( email )
