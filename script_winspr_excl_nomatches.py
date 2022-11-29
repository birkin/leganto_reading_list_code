"""
Creates filtered OIT course-file.
- Start with complete OIT course-file.
- For each course-entry...  
    - Select course for winter-session or spring-session.
    - Exclude course if it has no OCRA match (from the tracker.json file).
"""


import json, logging, os, pprint, sys


LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


def make_filtered_oit_file() -> None:
    """ Manages new file-creation. """

    ## setup --------------------------------------------------------
    settings = load_settings()
    oit_complete_filepath = f"{settings['OIT_COURSES_DIRPATH']}/leganto-course-data_20221129001455.txt"
    tracker_filepath = settings['TRACKER_JSON_FILEPATH']
    oit_filtered_filepath = f"{settings['OIT_COURSES_DIRPATH']}/oit_winter_&_spring_exlcuding_no_matches.txt"

    ## load complete oit-course-file --------------------------------
    with open( oit_complete_filepath, 'r' ) as f:
        oit_complete_course_data: list = f.readlines()
    log.debug( f'len(oit_complete_course_data), ``{len(oit_complete_course_data)}``' )

    ## load tracker-file --------------------------------------------
    with open( tracker_filepath, 'r' ) as f:
        tracker_data: dict = json.loads( f.read() )

    ## make filtered oit-course-file data-holder  -------------------
    new_file_lines: list = []

    ## loop through complete oit-course-file ------------------------
    for i, line in enumerate(oit_complete_course_data):
        ## get course-code ------------------------------------------
        oit_course_code_part: str = ''
        if i == 0:
            new_file_lines.append( line )
        else:
            parts = line.split( '\t' )
            oit_course_code_part = parts[0]
            ## check if course-code is part of desired session ------
            ok_strings = [ '2023-winter', '2023-spring' ]
            if any( ok_string in oit_course_code_part for ok_string in ok_strings ):
                ## check course-code against tracker-file ------------
                tracker_entry = tracker_data['oit_courses_processed'].get( oit_course_code_part, None )
                if tracker_entry:
                    if 'NO-OCRA-BOOKS/ARTICLES/EXCERPTS-FOUND' not in tracker_entry['status']:
                        new_file_lines.append( line )
                else:
                    log.debug( f'no tracker-entry for oit_course_code_part, ``{oit_course_code_part}``' )
    log.debug(msg=f'len(new_file_lines), ``{len(new_file_lines)}``')

    ## write filtered oit-course-file -------------------------------
    with open( oit_filtered_filepath, 'w' ) as f:
        f.writelines( new_file_lines )
    return


def load_settings() -> dict:
    """ Loads envar settings.
        Called by make_filtered_oit_file() """
    settings = {
        'OIT_COURSES_DIRPATH': os.environ['LGNT__OIT_COURSES_DIRPATH'],
        'TRACKER_JSON_FILEPATH': os.environ['LGNT__TRACKER_JSON_FILEPATH'],
    }
    return settings


if __name__ == '__main__':
    log.debug( 'starting if()' )
    make_filtered_oit_file()