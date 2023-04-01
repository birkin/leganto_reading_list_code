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
    data_holder_dict = {}
    with open( STEP_1p5_SOURCE_PATH, 'r' ) as f:
        data_holder_dict = json.loads( f.read() )

    ## initialize _meta_ data ----------------------------------------
    meta = {
        'description': 'Removes courses from "oit_data_01b.json" if the course is already in Leganto with the same instructor. Saves result as "oit_data_02.json".',
        'number_of_courses_below': 0,
        'OIT_courses_removed_count': 0,
        'OIT_courses_removed_list': [],
        }

    ## get already-in-leganto lines ---------------------------------
    already_in_leganto_lines = load_already_in_leganto_lines()
    already_in_leganto_dict_lines = load_already_in_leganto_dict_lines( already_in_leganto_lines )


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


def load_already_in_leganto_dict_lines( already_in_leganto_lines ) -> list:
    """ Returns list of dicts, one for each line in already_in_leganto_lines. 
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
    for i in range( 0, 5 ):
        log.debug( f'a few already_in_leganto_dict_lines[{i}], ``{already_in_leganto_dict_lines[i]}``' )
    return already_in_leganto_dict_lines

    ## end def load_already_in_leganto_dict_lines()


## entry point ------------------------------------------------------

if __name__ == '__main__':
    main()
    sys.exit(0)
