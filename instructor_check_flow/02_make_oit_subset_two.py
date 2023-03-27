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
# OIT_COURSE_LIST_PATH: str = os.environ['LGNT__COURSES_FILEPATH']
# TARGET_SEASON: str = os.environ['LGNT__SEASON']
# TARGET_YEAR: str = os.environ['LGNT__YEAR']
# LEGIT_SECTIONS: str = json.loads( os.environ['LGNT__LEGIT_SECTIONS_JSON'] )
# OIT_SUBSET_01_OUTPUT_PATH: str = '%s/oit_subset_01.tsv' % os.environ['LGNT__CSV_OUTPUT_DIR_PATH']
# log.debug( f'OIT_COURSE_LIST_PATH, ``{OIT_COURSE_LIST_PATH}``' )
# log.debug( f'TARGET_SEASON, ``{TARGET_SEASON}``' )
# log.debug( f'TARGET_YEAR, ``{TARGET_YEAR}``' )
# log.debug( f'LEGIT_SECTIONS, ``{LEGIT_SECTIONS}``' )
# log.debug( f'OIT_SUBSET_01_OUTPUT_PATH, ``{OIT_SUBSET_01_OUTPUT_PATH}``' )

## constants --------------------------------------------------------
OIT_SUBSET_01_SOURCE_PATH = f'{CSV_OUTPUT_DIR_PATH}/oit_subset_01.tsv'
OIT_SUBSET_02_OUTPUT_PATH = f'{CSV_OUTPUT_DIR_PATH}/oit_subset_02.tsv'

## controller -------------------------------------------------------

def main():
    """ Controller.
        Called by if __name__ == '__main__' """

    ## validate already-in-leganto file -----------------------------
    assert is_utf8_encoded(ALREADY_IN_LEGANTO_FILEPATH) == True
    assert is_tab_separated(ALREADY_IN_LEGANTO_FILEPATH) == True
    assert already_in_leganto_columuns_are_valid(ALREADY_IN_LEGANTO_FILEPATH) == True

    ## load oit-subset-01 file --------------------------------------
    with open( OIT_SUBSET_01_SOURCE_PATH, 'r' ) as f:
        lines = f.readlines()

    ## get heading and data lines -----------------------------------
    new_subset_lines = []
    heading_line = lines[0]
    new_subset_lines.append( heading_line )
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
        line_dict = instructor_common.parse_line( data_line, heading_line, i )
        course_code_dict = instructor_common.parse_course_code( data_line, i )
        match_try_1 = f'%s.%s' % ( course_code_dict['course_code_department'], course_code_dict['course_code_number'] )
        match_try_2 = f'%s %s' % ( course_code_dict['course_code_department'], course_code_dict['course_code_number'] )
        if i < 5:
            log.debug( f'processing data_line, ``{data_line}``' )
            log.debug( f'match_try_1, ``{match_try_1}``' )
            log.debug( f'match_try_2, ``{match_try_2}``' )


        log.debug( 'HEREZZ' )
        break



    1/0


    # ## make subset --------------------------------------
    # skipped_due_to_no_instructor = []
    # skipped_sections = []
    # subset_lines = []
    # for i, data_line in enumerate( data_lines ):
    #     data_ok = False
    #     if i < 5:
    #         log.debug( f'processing data_line, ``{data_line}``' )
    #     line_dict = parse_line( data_line, heading_line, i )
    #     course_code_dict = parse_course_code( data_line, i )
    #     if course_code_dict['course_code_year'] == TARGET_YEAR:
    #         log.debug( 'passed year check' )
    #         if course_code_dict['course_code_term'] == TARGET_SEASON:
    #             log.debug( 'passed season check' )
    #             if course_code_dict['course_code_section'] in LEGIT_SECTIONS:
    #                 log.debug( 'passed section check' )
    #                 data_ok = True
    #             else:
    #                 skipped_sections.append( course_code_dict['course_code_section'] )
    #             if data_ok == True and len( line_dict['ALL_INSTRUCTORS'].strip() ) > 0:
    #                 log.debug( 'passed instructor check' )
    #                 subset_lines.append( data_line )
    #                 log.debug( 'added to subset_lines' )
    #             else:
    #                 log.debug( 'skipped due to no instructor' )
    #                 skipped_due_to_no_instructor.append( data_line )
    # # log.debug( f'subset_lines, ``{pprint.pformat(subset_lines)}``' )
    # # log.debug( f'len(subset_lines), ``{len(subset_lines)}``' )
    # # log.debug( f'skipped_due_to_no_instructor, ``{pprint.pformat(skipped_due_to_no_instructor)}``' )
    # # log.debug( f'len(skipped_due_to_no_instructor), ``{len(skipped_due_to_no_instructor)}``' )

    # ## populate course-parts buckets --------------------------------
    # buckets_dict: dict  = make_buckets()  # returns dict like: ```( course_code_institutions': {'all_values': [], 'unique_values': []}, etc... }```
    # for i, summer_line in enumerate( subset_lines ):
    #     if i < 5:
    #         log.debug( f'processing summer-line, ``{summer_line}``' )
    #     course_code_dict = parse_course_code( summer_line, i )
    #     buckets_dict: dict = populate_buckets( course_code_dict, buckets_dict )
    # buckets_dict['skipped_sections_for_target_year_and_season']['all_values'] = skipped_sections
    # # log.debug( f'buckets_dict, ``{pprint.pformat(buckets_dict)}``' )

    # ## prepare bucket counts ----------------------------------------
    # buckets_dict: dict = add_counts( buckets_dict )
    # log.debug( f'updated_buckets_dict, ``{pprint.pformat(buckets_dict)}``' )

    # ## prep easyview output -----------------------------------------
    # # easyview_output = make_easyview_output( buckets_dict )
    # easyview_output = make_easyview_output( buckets_dict, skipped_due_to_no_instructor )
    # log.debug( f'easyview_output, ``{pprint.pformat(easyview_output)}``' )

    # ## write summer-2023 subset to file -----------------------------
    # with open( OIT_SUBSET_01_OUTPUT_PATH, 'w' ) as f:
    #     f.write( heading_line )
    #     for line in subset_lines:
    #         f.write( line )
        
    ## end main()


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




# def make_easyview_output( buckets_dict: dict, skipped_due_to_no_instructor: list ) -> dict:
#     """ Prepares easyview output.
#         Called by main() """
#     assert type(buckets_dict) == dict
#     output_dict = {}
#     for key in buckets_dict.keys():
#         unsorted_unique_values = buckets_dict[key]['unique_values']
#         # sorted_unique_values = sorted( unsorted_unique_values, key=lambda x: x[1], reverse=True )
#         ## sort by count and then by string
#         # sorted_unique_values = sorted( unsorted_unique_values, key=lambda x: (x[1], x[0]), reverse=True )
#         ## sort by count-descending, and then by string-ascending
#         sorted_unique_values = sorted( unsorted_unique_values, key=lambda x: (-x[1], x[0]) )        
#         output_dict[key] = sorted_unique_values
#     output_dict['skipped_instructor_count_for_target_year_and_season_and_section'] = len( skipped_due_to_no_instructor )
#     # jsn = json.dumps( output_dict, indent=2 )
#     # with open( './output.json', 'w' ) as f:
#     #     f.write( jsn )
#     return output_dict


# def add_counts( buckets_dict: dict ) -> dict:
#     """ Updates 'unique_set': {'count': 0, 'unique_values': []} """
#     assert type(buckets_dict) == dict
#     for key in buckets_dict.keys():
#         log.debug( f'key, ``{key}``' ) 
#         unique_values_from_set = list( set( buckets_dict[key]['all_values'] ) )
#         unique_tuple_list = [ (value, buckets_dict[key]['all_values'].count(value)) for value in unique_values_from_set ]
#         log.debug( f'unique_tuple_list, ``{unique_tuple_list}``' )
#         buckets_dict[key]['unique_values'] = unique_tuple_list
#     # log.debug( f'buckets_dict, ``{pprint.pformat(buckets_dict)}``' )
#     return buckets_dict


# def populate_buckets( course_code_dict: dict, buckets_dict: dict ) -> dict:
#     """ Populates buckets. """
#     assert type(course_code_dict) == dict
#     assert type(buckets_dict) == dict
#     for key in course_code_dict.keys():
#         if key == 'course_code_institution':
#             buckets_dict['subset_institutions']['all_values'].append( course_code_dict[key] )
#         elif key == 'course_code_department':
#             buckets_dict['subset_departments']['all_values'].append( course_code_dict[key] )
#         elif key == 'course_code_year':
#             buckets_dict['subset_years']['all_values'].append( course_code_dict[key] )
#         elif key == 'course_code_term':
#             buckets_dict['subset_terms']['all_values'].append( course_code_dict[key] )
#         elif key == 'course_code_section':
#             buckets_dict['subset_sections']['all_values'].append( course_code_dict[key] )
#     return buckets_dict


# def make_buckets() -> dict:
#     """ Returns dict of buckets. """
#     buckets_dict = {
#         'subset_institutions': { 
#             'all_values': [], 
#             'unique_values': [] },
#         'subset_departments': { 
#             'all_values': [], 
#             'unique_values': [] },
#         'subset_years': { 
#             'all_values': [], 
#             'unique_values': [] },
#         'subset_terms': { 
#             'all_values': [], 
#             'unique_values': [] },
#         'subset_sections': { 
#             'all_values': [], 
#             'unique_values': [] },
#         'skipped_sections_for_target_year_and_season': { 
#             'all_values': [], 
#             'unique_values': [] },
#         }
#     log.debug( f'initialized buckets_dict, ``{pprint.pformat(buckets_dict)}``' )
#     return buckets_dict


