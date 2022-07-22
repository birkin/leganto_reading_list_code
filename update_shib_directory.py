import logging, os, pathlib

LOG_PATH: str = os.environ['LGNT__LOG_PATH']
WEB_DIR_PATH: str = os.environ['LGNT__WEB_DIRECTORY_PATH']

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)


spreadsheet_courses: list = [ 'BIOL1234A', 'ENVR2345B', 'HIST3456C', 'ITAL4567D' ]  # would come from spreadsheet

## create directories ---------------------------

for course in spreadsheet_courses:
    desired_path: str = f'{WEB_DIR_PATH}/{course}'
    path_obj = pathlib.Path( desired_path )
    path_obj.mkdir( parents=True, exist_ok=True )

## create shib-conf file ------------------------

TEMPLATE: str = '''

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

for course in spreadsheet_courses:
    READINGS_PATH: str = f'{WEB_DIR_PATH}/{course}'
    course_characters = course[0:4]
    course_numerals = course[4:]
    COURSE_GROUPER_ENTRY: str = f'COURSE:{course_characters}:{course_numerals}:2022-Fall:S01:All'
    shib_entry: str = TEMPLATE.replace( '{COURSE_ID}', course ).replace( '{READINGS_PATH}', READINGS_PATH ). replace( '{COURSE_GROUPER_ENTRY}', COURSE_GROUPER_ENTRY )

    log.debug( f'shib_entry, ```{shib_entry}```' )
