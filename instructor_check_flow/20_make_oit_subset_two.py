"""
This script:
- loads the "oit_data_01b.json" into a data-holder-dict.
- produces a subset of the data-holder-dict -- "oit_subset_02.tsv" -- which will be used to create reading-lists.

The logic...
- If there is an OIT course with OIT-instructor-X -- and that OIT course is not in Leganto -- I _WILL_ try to create an OCRA reading-list.
- If there is an OIT course with OIT-instructor-X -- and that OIT course is in Leganto (one or more times), but none of the Leganto course-entries are with instructor-X -- I _WILL_ try to create an OCRA reading-list.
- If there is an OIT course with OIT-instructor-X and that OIT course is in Leganto with instructor-X -- I _WILL-NOT_ try to create an OCRA reading-list.

Another way of saying this...
The new subset file will remove courses from the original subset file if the course is already in Leganto with the same instructor.
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
from lib.common import validate_files

## grab env vars ----------------------------------------------------
JSON_DATA_DIR_PATH: str = os.environ['LGNT__JSON_DATA_DIR_PATH']
ALREADY_IN_LEGANTO_FILEPATH: str = os.environ['LGNT__ALREADY_IN_LEGANTO_FILEPATH']
log.debug( f'JSON_DATA_DIR_PATH, ``{JSON_DATA_DIR_PATH}``')
log.debug( f'ALREADY_IN_LEGANTO_FILEPATH, ``{ALREADY_IN_LEGANTO_FILEPATH}``')

## constants --------------------------------------------------------
STEP_1p5_SOURCE_PATH = f'{JSON_DATA_DIR_PATH}/oit_data_01b.json'
STEP_2p0_OUTPUT_PATH = f'{JSON_DATA_DIR_PATH}/oit_data_02.json'
log.debug( f'STEP_1p5_SOURCE_PATH, ``{STEP_1p5_SOURCE_PATH}``' )
log.debug( f'STEP_2p0_OUTPUT_PATH, ``{STEP_2p0_OUTPUT_PATH}``' )


## controller -------------------------------------------------------

def main():
    """ Controller.
        Called by if __name__ == '__main__' """

    ## validate already-in-leganto file -----------------------------
    assert validate_files.is_utf8_encoded( ALREADY_IN_LEGANTO_FILEPATH ) == True
    # assert validate_files.is_tab_separated( ALREADY_IN_LEGANTO_FILEPATH ) == True  # TODO
    assert validate_files.already_in_leganto_columns_valid( ALREADY_IN_LEGANTO_FILEPATH ) == True

    ## load "oit_data_01b.json" file --------------------------------
    source_data_holder_dict = {}
    with open( STEP_1p5_SOURCE_PATH, 'r' ) as f:
        source_data_holder_dict = json.loads( f.read() )

    ## initialize _meta_ data ----------------------------------------
    meta = {
        'description': 'Removes courses from "oit_data_01b.json" if the course is already in Leganto with the same instructor. Saves result as "oit_data_02.json".',
        'number_of_courses_below': 0,
        'number_of_already_in_leganto_courses': 0,
        'number_of_already_in_leganto_courses_without_email': 0,
        'OIT_courses_removed_count': 0,
        'OIT_courses_removed_list': [],
        }

    ## prepare already-in-leganto data for comparison ---------------
    already_in_leganto_lines = load_already_in_leganto_lines()
    already_in_leganto_dict_lines = prep_already_in_leganto_dict_lines( already_in_leganto_lines )
    update_meta_with_already_in_leganto_data( already_in_leganto_dict_lines, meta )
    # log.debug( f'meta, ``{pprint.pformat(meta)}``' )

    ## run comparison ------------------------------------------------
    post_instructor_check_data_holder_dict = {}
    for i, ( oit_course_code_key, data_value ) in enumerate( source_data_holder_dict.items() ):
        if i < 5:
            log.debug( f'oit_course_code_key, ``{oit_course_code_key}``' )
            log.debug( f'data_value, ``{data_value}``' )
        if oit_course_code_key == '__meta__':
            log.debug( 'skipping `__meta__`' )
            continue
        ## get oit email-list ----------------------------------------
        oit_email_list = data_value['oit_email_addresses']
        ## check each OIT email-and-course against leganto data -----
        match_found = False
        for oit_email in oit_email_list:
            match_found = check_for_match( oit_course_code_key, oit_email, already_in_leganto_dict_lines )
            if match_found == True:
                meta['OIT_courses_removed_count'] += 1
                meta['OIT_courses_removed_list'].append( oit_course_code_key )
                break
        if match_found == True:
            log.debug( 'continuing' )
            continue
        else:
            log.debug( f'no match found, so adding course, ``{oit_course_code_key}`` -- to post_instructor_check_data_holder_dict' )
            post_instructor_check_data_holder_dict[oit_course_code_key] = data_value
    post_instructor_check_data_holder_dict['__meta__'] = meta
    log.debug( f'post_instructor_check_data_holder_dict, ``{pprint.pformat(post_instructor_check_data_holder_dict)}``' )


    1/0


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


def load_already_in_leganto_lines() -> list:
    already_in_leganto_lines = []
    with open( ALREADY_IN_LEGANTO_FILEPATH, 'r' ) as f:
        for line in f:
            already_in_leganto_lines.append( line.lower() )
        # already_in_leganto_lines = f.readlines()
    for i in range( 0, 5 ):
        log.debug( f'a few already_in_leganto_lines[{i}], ``{already_in_leganto_lines[i]}``' )
    return already_in_leganto_lines


def prep_already_in_leganto_dict_lines( already_in_leganto_lines ) -> list:
    """ Returns list of dicts, one for each line in already_in_leganto_lines. 
        Makes it easier to work with the data.
        Called by main(). """
    keys = [
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
        ]
    already_in_leganto_dict_lines = []
    for ( i, line ) in enumerate( already_in_leganto_lines ):
        # log.debug( f'i, ``{i}``; line, ``{line}``' )
        if i == 0:
            continue
        line_dict = {}
        ## split line into parts ------------------------------------
        parts = line.split( '\t' )
        # log.debug( f'parts, ``{parts}``' )
        assert len( parts ) == len( keys ), len( parts )
        stripped_parts = [ part.strip() for part in parts ]
        assert len( stripped_parts ) == len( keys ), len( stripped_parts )
        ## build line-dict ------------------------------------------
        for j, key in enumerate( keys ):
            line_dict[keys[j]] = stripped_parts[j]
        ## append line-dict to list ---------------------------------
        already_in_leganto_dict_lines.append( line_dict )
    for line_dct in already_in_leganto_dict_lines:
        email_string = line_dct['Course Instructor Preferred Email']
        emails: list = email_string.split( ';' )
        stripped_emails = [ eml.strip() for eml in emails ]
        line_dct['email_list'] = stripped_emails
    for i in range( 0, 5 ):
        log.debug( f'a few already_in_leganto_dict_lines[{i}], ``{already_in_leganto_dict_lines[i]}``' )
    # log.debug( f'already_in_leganto_dict_lines, ``{pprint.pformat(already_in_leganto_dict_lines)}``' )
    return already_in_leganto_dict_lines

    ## end def load_already_in_leganto_dict_lines()


def update_meta_with_already_in_leganto_data( already_in_leganto_dict_lines: list, meta: dict ) -> None:
    """ Updates meta-dict with data from already_in_leganto_dict_lines.
        Keeps main() cleaner by doing this here.
        Called by main(). """
    meta['number_of_already_in_leganto_courses'] = len( already_in_leganto_dict_lines )
    for item in already_in_leganto_dict_lines:
        if item['email_list'] == ['']:
            meta['number_of_already_in_leganto_courses_without_email'] += 1
    return
    # log.debug( f'meta, ``{pprint.pformat(meta)}``' )


def check_for_match( oit_course_code_key, oit_email, already_in_leganto_dict_lines ):
    """ Returns True if match found, else False.
        Called by main(). """
    dept_part = oit_course_code_key.split( '.' )[0]
    num_part = oit_course_code_key.split( '.' )[1]
    match_try_1 = f'%s.%s' % ( dept_part, num_part )
    match_try_2 = f'%s %s' % ( dept_part, num_part )
    match_try_3 = f'%s%s' % ( dept_part, num_part )
    course_code_and_instructor_match_found_result = False
    for leganto_item in already_in_leganto_dict_lines:
        course_code_match_found = False
        if match_try_1 in leganto_item['Reading List Code'] or match_try_1 in leganto_item['Reading List Name'] or match_try_1 in leganto_item['Course Code']:
            course_code_match_found = True
        elif match_try_2 in leganto_item['Reading List Code'] or match_try_2 in leganto_item['Reading List Name'] or match_try_2 in leganto_item['Course Code']:
            course_code_match_found = True
        elif match_try_3 in leganto_item['Reading List Code'] or match_try_3 in leganto_item['Reading List Name'] or match_try_3 in leganto_item['Course Code']:
            course_code_match_found = True
        if course_code_match_found:
            leganto_email_addresses = leganto_item['email_list']
            if oit_email in leganto_email_addresses:
                course_code_and_instructor_match_found_result = True
                break
    log.debug( f'course_code_and_instructor_match_found_result, ``{course_code_and_instructor_match_found_result}``' )
    return course_code_and_instructor_match_found_result

## entry point ------------------------------------------------------

if __name__ == '__main__':
    main()
    sys.exit(0)
