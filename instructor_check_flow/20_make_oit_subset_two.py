"""
This script creates a subset of "oit_subset_01.tsv" which will be called "oit_subset_02.tsv".
- it will contain courses from "oit_subset_01.tsv" that are not in the "in_leganto.tsv" file.
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
from instructor_check_flow import common as instructor_common
from lib.common import query_ocra
from lib.common import validate_oit_file

## grab env vars ----------------------------------------------------
CSV_OUTPUT_DIR_PATH: str = os.environ['LGNT__CSV_OUTPUT_DIR_PATH']
ALREADY_IN_LEGANTO_FILEPATH: str = os.environ['LGNT__ALREADY_IN_LEGANTO_FILEPATH']
log.debug( f'CSV_OUTPUT_DIR_PATH, ``{CSV_OUTPUT_DIR_PATH}``' )
log.debug( f'ALREADY_IN_LEGANTO_FILEPATH, ``{ALREADY_IN_LEGANTO_FILEPATH}``')

## constants --------------------------------------------------------
OIT_SUBSET_01_SOURCE_PATH = f'{CSV_OUTPUT_DIR_PATH}/oit_subset_01.tsv'
OIT_SUBSET_02_OUTPUT_PATH = f'{CSV_OUTPUT_DIR_PATH}/oit_subset_02.tsv'
log.debug( f'OIT_SUBSET_01_SOURCE_PATH, ``{OIT_SUBSET_01_SOURCE_PATH}``' )
log.debug( f'OIT_SUBSET_02_OUTPUT_PATH, ``{OIT_SUBSET_02_OUTPUT_PATH}``' )

## controller -------------------------------------------------------

def main():
    """ Controller.
        Called by if __name__ == '__main__' """

    ## validate already-in-leganto file -----------------------------
    assert validate_oit_file.is_utf8_encoded(ALREADY_IN_LEGANTO_FILEPATH) == True
    assert validate_oit_file.is_tab_separated(ALREADY_IN_LEGANTO_FILEPATH) == True
    assert already_in_leganto_columuns_are_valid(ALREADY_IN_LEGANTO_FILEPATH) == True

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


    1/0


    ## get already-in-leganto lines ---------------------------------
    already_in_leganto_lines = []
    with open( ALREADY_IN_LEGANTO_FILEPATH, 'r' ) as f:
        for line in f:
            already_in_leganto_lines.append( line.lower().strip() )
        # already_in_leganto_lines = f.readlines()
    for i in range( 0, 5 ):
        log.debug( f'already_in_leganto_lines[{i}], ``{already_in_leganto_lines[i]}``' )

    ## make subset --------------------------------------------------
    for i, data_line in enumerate( data_lines ):
        course_code_dict = instructor_common.parse_course_code( data_line, i )
        match_try_1 = f'%s.%s' % ( course_code_dict['course_code_department'], course_code_dict['course_code_number'] )
        match_try_2 = f'%s %s' % ( course_code_dict['course_code_department'], course_code_dict['course_code_number'] )
        # log.debug( f'processing data_line, ``{data_line}``' )
        # log.debug( f'match_try_1, ``{match_try_1}``' )
        # log.debug( f'match_try_2, ``{match_try_2}``' )
        ## check if course is already in leganto --------------------
        match_found = False
        for leganto_line in already_in_leganto_lines:
            # log.debug( f'checking leganto_line, ``{leganto_line}`` on match_tries ``{match_try_1}`` and ``{match_try_2}``' )
            if match_try_1 in leganto_line:
                log.debug( f'found match on ``{match_try_1}`` for leganto_line, ``{leganto_line}``' )
                match_found = True
                break
            elif match_try_2 in leganto_line:
                log.debug( f'found match on ``{match_try_2}`` for leganto_line, ``{leganto_line}``' )
                match_found = True
                break
        if match_found == False:
            new_subset_lines.append( data_line )
    # log.debug( f'new_subset_lines, ``{pprint.pformat(new_subset_lines)}``' )
    log.debug( f'len(original subset lines), ``{len(lines)}``' )
    log.debug( f'len(new_subset_lines), ``{len(new_subset_lines)}``' )

    ## write oit_subset_02 to file -----------------------------
    with open( OIT_SUBSET_02_OUTPUT_PATH, 'w' ) as f:
        f.write( heading_line )
        for line in new_subset_lines:
            f.write( line )

    ## end def main() 


## helper functions -------------------------------------------------


def already_in_leganto_columuns_are_valid( filepath: str ) -> bool:
    """ Ensures tsv file is as expected.
        Called by main() """
    check_result = False
    line = ''
    with open( filepath, 'r' ) as f:
        line = f.readline()
    parts = line.split( '\t' )
    stripped_parts = [ part.strip() for part in parts ]
    log.debug( f'stripped_parts, ``{stripped_parts}``' )
    if stripped_parts == [
        'Reading List Id', 
        'Reading List Owner', 
        'Academic Department', 
        'Reading List Code',                        # when good, like: "brown.pols.1420.2023-spring.s01"
        'Reading List Name',                        # sometimes contains strings, eg: "HIST 1120" or "ENVS1232"
        'Course Code',                              # sometimes contains the `Reading List Code` value, or a string-segment like "EAST 0141"
        'Course Section', 
        'Course Name', 
        'Course Instructor', 
        'Course Instructor Identifier', 
        'Course Instructor With Primary Identifier', 
        'Course Instructor Preferred Email'         # if not empty, contains one email-address, or multiple email-addresses, separated by a semi-colon.
        ]:
        check_result = True
    log.debug( f'check_result, ``{check_result}``' )
    return check_result


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
    meta_dict = {
        'number_of_courses': len( data_holder_dict ),
        'number_of_courses_with_multiple_instructors': 0,
        'number_of_courses_for_which_email_addresses_were_found': 0,
    }
    for ( key, data_dict_value ) in data_holder_dict.items():
        if len( data_dict_value.get('oit_all_instructors', []) ) > 1:
            meta_dict['number_of_courses_with_multiple_instructors'] += 1
        if len( data_dict_value.get('oit_email_addresses', []) ) > 0:
            meta_dict['number_of_courses_for_which_email_addresses_were_found'] += 1
    data_holder_dict['__meta__'] = meta_dict
    log.debug( f'data_holder_dict, ``{pprint.pformat(data_holder_dict)}``' )    
    return data_holder_dict


# def get_email_address( bru_id: str ) -> str:
#     """ Returns email-address for instructor.
#         Called by add_emails_to_data_holder_dict() """
#     email_address = ''
#     log.debug( f'email_address, ``{email_address}``' )
#     return email_address

    ## end get_email_address()


if __name__ == '__main__':
    main()
    sys.exit(0)
