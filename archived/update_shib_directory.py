"""
Archived.
- Created shib-protection for each course, allowing only members of that course to access the file.
- Archived because decision was made not to use the reserves-file webapp.
"""

import logging, os, pathlib

## setup ------------------------------------------------------------

LOG_PATH: str = os.environ['LGNT__LOG_PATH']
WEB_DIR_PATH: str = os.environ['LGNT__WEB_DIRECTORY_PATH']
WEB_DIR_URL_PATH: str = '/url/path/to/reserves_readings'  # will load from env

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)

spreadsheet_courses = [ 'BIOL1234A', 'ENVR2345B', 'HIST3456C', 'ITAL4567D' ]  # would come from spreadsheet

## create directories -----------------------------------------------

for course in spreadsheet_courses:
    desired_path: str = f'{WEB_DIR_PATH}/{course}'
    path_obj = pathlib.Path( desired_path )
    path_obj.mkdir( parents=True, exist_ok=True )

## create shib-conf file --------------------------------------------

shib_output_path = f'{WEB_DIR_PATH}/shib.conf'  # may be an .htaccess file; will check with J.M. or Y.F.

TEMPLATE = '''

# -------------------------------------
# course-reserves entry for {COURSE_ID}
# -------------------------------------
<Location {READINGS_PATH}>
  AuthType shibboleth
  ShibRequireSession on
  ShibUseHeaders on
  require shib-attr Shibboleth-isMemberOf {COURSE_GROUPER_ENTRY}
  require shib-attr Shibboleth-isMemberOf BROWN:DEPARTMENT:LIBRARY
</Location>
'''

shib_entries: list = []
for course in spreadsheet_courses:
    READINGS_PATH = f'{WEB_DIR_URL_PATH}/{course}'
    course_characters = course[0:4]
    course_numerals = course[4:]
    COURSE_GROUPER_ENTRY = f'COURSE:{course_characters}:{course_numerals}:2022-Fall:S01:All'
    shib_entry: str = TEMPLATE.replace( '{COURSE_ID}', course ).replace( '{READINGS_PATH}', READINGS_PATH ). replace( '{COURSE_GROUPER_ENTRY}', COURSE_GROUPER_ENTRY )
    # log.debug( f'shib_entry, ```{shib_entry}```' )
    shib_entries.append( shib_entry )

with open( shib_output_path, 'w', encoding='utf-8' ) as filehandler:
    filehandler.writelines( shib_entries )

## EOF  