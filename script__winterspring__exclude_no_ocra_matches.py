"""
Creates filtered OIT course-file.
- Start with complete OIT course-file.
- Select courses for winter-session or spring-session.
- Exclude from these courses that had no matches with OCRA (from the tracker.json file).
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
    settings = load_settings()
    oit_complete_filepath = f"{settings['OIT_COURSES_DIRPATH']}/leganto-course-data_20221129001455.txt"
    log.debug( f'oit_complete_filepath, ``{oit_complete_filepath}``' )

    return




def load_settings() -> dict:
    """ Loads envar settings.
        Called by manage_build_reading_list() """
    settings = {
        'OIT_COURSES_DIRPATH': os.environ['LGNT__OIT_COURSES_DIRPATH'],
        'TRACKER_JSON_FILEPATH': os.environ['LGNT__TRACKER_JSON_FILEPATH'],
    }
    log.debug( f'settings-keys, ``{pprint.pformat( sorted(list(settings.keys())) )}``' )
    return settings


if __name__ == '__main__':
    log.debug( 'starting if()' )
    make_filtered_oit_file()