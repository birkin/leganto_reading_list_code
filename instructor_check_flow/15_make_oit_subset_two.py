"""
This script...
- Starts with subset "oit_subset_01.tsv", which removes courses that aren't the target season/year/section, and have no instructor.
- It creates a data-holder-dict of relevant data from the oit_subset_01.tsv file.
- It looks up the OIT bru-id in OCRA to get the instructor email-address (for the subsequent step to check if the instructor is in Leganto).
    - If no instructor email address is found, the course is eliminated.
    - NOTE: the OCRA lookup implies the need to ssh-tunnel to access the db.
    - NOTE: this takes 10 or 15 minutes to run.
- It saves the output to a json file to be used in the next step.
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
from instructor_check_flow import common as instructor_common
from lib.common import query_ocra
from lib.common import validate_files

## grab env vars ----------------------------------------------------
CSV_OUTPUT_DIR_PATH: str = os.environ['LGNT__CSV_OUTPUT_DIR_PATH']
JSON_DATA_DIR_PATH: str = os.environ['LGNT__JSON_DATA_DIR_PATH']
log.debug( f'CSV_OUTPUT_DIR_PATH, ``{CSV_OUTPUT_DIR_PATH}``' )
log.debug( f'JSON_DATA_DIR_PATH, ``{JSON_DATA_DIR_PATH}``')

## constants --------------------------------------------------------
OIT_SUBSET_01_SOURCE_PATH = f'{CSV_OUTPUT_DIR_PATH}/oit_subset_01.tsv'
STEP_1p5_OUTPUT_PATH = f'{JSON_DATA_DIR_PATH}/oit_data_01b.json'
log.debug( f'OIT_SUBSET_01_SOURCE_PATH, ``{OIT_SUBSET_01_SOURCE_PATH}``' )
log.debug( f'STEP_1p5_OUTPUT_PATH, ``{STEP_1p5_OUTPUT_PATH}``' )

## controller -------------------------------------------------------

def main():
    """ Controller.
        Called by if __name__ == '__main__' """

    ## validate oit-subset-01 file ----------------------------------
    assert validate_files.is_utf8_encoded(OIT_SUBSET_01_SOURCE_PATH) == True
    assert validate_files.is_tab_separated(OIT_SUBSET_01_SOURCE_PATH) == True

    ## load oit-subset-01 file --------------------------------------
    lines = []
    with open( OIT_SUBSET_01_SOURCE_PATH, 'r' ) as f:
        lines = f.readlines()

    ## get heading and data lines -----------------------------------
    new_subset_lines = []
    heading_line = lines[0]
    parts = heading_line.split( '\t' )
    parts = [ part.strip() for part in parts ]
    log.debug( f'parts, ``{pprint.pformat(parts)}``' )
    data_lines = lines[1:]

    ## build course_code.course_number dict -------------------------
    data_holder_dict = build_data_holder_dict( data_lines )

    ## add emails to data_holder_dict -------------------------------
    data_holder_dict = add_emails_to_data_holder_dict( data_holder_dict )

    ## remove entries with no email ---------------------------------
    data_holder_dict = remove_entries_with_no_email( data_holder_dict )

    ## write data-holder-dict to file -------------------------------
    with open( STEP_1p5_OUTPUT_PATH, 'w' ) as f:
        jsn = json.dumps( data_holder_dict, sort_keys=True, indent=2 )
        f.write( jsn )

    ## end def main() 


## helper functions -------------------------------------------------
def remove_entries_with_no_email( data_holder_dict ):
    """ Removes entries from data_holder_dict that have no email.
        Called by main() """
    assert type( data_holder_dict ) == dict
    log.debug( f'len(data_holder_dict), ``{len(data_holder_dict)}``' )
    new_data_holder_dict = {}
    for course_key, course_parts_dict in data_holder_dict.items():
        if course_key == '__meta__':
            new_data_holder_dict[course_key] = course_parts_dict
        else:
        # try:
            if course_parts_dict['oit_email_addresses'] != []:
                new_data_holder_dict[course_key] = course_parts_dict
        # except:
        #     log.debug( f'course_key, ``{course_key}``' )
        #     log.debug( f'course_parts_dict, ``{pprint.pformat(course_parts_dict)}``' )
        #     raise Exception( 'problem with course_parts_dict' )
    log.debug( f'len(new_data_holder_dict), ``{len(new_data_holder_dict)}``' )
    return new_data_holder_dict


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
    log.debug( f'initial data_holder_dict (partial), ``{pprint.pformat(data_holder_dict)[0:500]}...``' )    
    return data_holder_dict

    ## end build_data_holder_dict()


def add_emails_to_data_holder_dict( data_holder_dict: dict ) -> dict:
    """ Adds email-addresses to data_holder_dict.
        Called by main() """
    for i, ( course_key, course_parts_dict ) in enumerate( data_holder_dict.items() ):
        log.debug( f'i, ``{i}``; course_key, ``{course_key}``' )
        # if i >= 10:  # for testing
        #     break
        bru_ids = course_parts_dict['oit_all_instructors']
        log.debug( f'bru_ids, ``{pprint.pformat(bru_ids)}``' )
        email_addresses = []
        email_address_map = {}
        for bru_id in bru_ids:
            email_address = query_ocra.get_email_from_bruid( bru_id )
            log.debug( f'email_address result-set, ``{email_address}``')
            email_address_map[bru_id] = email_address
            if email_address:
                email_addresses.append( email_address )
        course_parts_dict['oit_bruid_to_email_map'] = email_address_map
        course_parts_dict['oit_email_addresses'] = email_addresses
    log.debug( 'end of email lookup' )
    ## update analysis ----------------------------------------------
    meta_dict = {'description': '''Loads data from the oit-subset-01 file, which which removes courses that aren't the target season/year/section, and have no instructor. This step builds this data-holder-dict, adds email-addresses to it by looking up the OIT bru_id in OCRA to get email addresses, and saves it as a json-file.''',
        'number_of_courses_previously': len( data_holder_dict ),
        'number_of_courses_for_which_email_addresses_were_found': 0,
        'number_of_courses_with_multiple_instructors': 0,
        'timestamp': str( datetime.datetime.now() )
    }
    for ( key, data_dict_value ) in data_holder_dict.items():
        if len( data_dict_value.get('oit_all_instructors', []) ) > 1:
            meta_dict['number_of_courses_with_multiple_instructors'] += 1
        if len( data_dict_value.get('oit_email_addresses', []) ) > 0:
            meta_dict['number_of_courses_for_which_email_addresses_were_found'] += 1
    data_holder_dict['__meta__'] = meta_dict
    log.debug( f'data_holder_dict, ``{pprint.pformat(data_holder_dict)}``' )    
    return data_holder_dict

    ## end add_emails_to_data_holder_dict()


if __name__ == '__main__':
    main()
    sys.exit(0)
