"""
This script creates a subset of "oit_subset_01.tsv" which will be called "oit_subset_02.tsv".
- it will contain courses from "oit_subset_01.tsv" that are not in the "in_leganto.csv" file.
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
from lib.common.validate_oit_file import is_utf8_encoded, is_tab_separated
from instructor_check_flow import common as instructor_common

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
    assert is_utf8_encoded(ALREADY_IN_LEGANTO_FILEPATH) == True
    assert is_tab_separated(ALREADY_IN_LEGANTO_FILEPATH) == True
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
    if stripped_parts == [
        'Course ID',
        'Course Instructor',
        'Number Of Citations',
        'Course Section',
        'Course Name',
        'Current Course Start Date',
        'Reading List Code',
        'Course Modification Date',
        'Reading List Name',
        'Course Instructor Primary Identifier'    
        ]:
        check_result = True
    # log.debug( f'parts, ``{pprint.pformat(parts)}``' )
    log.debug( f'check_result, ``{check_result}``' )
    return check_result


if __name__ == '__main__':
    main()
    sys.exit(0)
