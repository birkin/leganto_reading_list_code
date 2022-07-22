import logging, os, pathlib

LOG_PATH: str = os.environ['LGNT__LOG_PATH']
WEB_DIR_PATH: str = os.environ['LGNT__WEB_DIRECTORY_PATH']

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)


spreadsheet_courses: list = [ 'BIOL1234A', 'ENVR2345B', 'HIST3456C', 'ITAL4567D' ]

## create directories ---------------------------

for course in spreadsheet_courses:
    desired_path: str = f'{WEB_DIR_PATH}/{course}'
    path_obj = pathlib.Path( desired_path )
    path_obj.mkdir( parents=True, exist_ok=True )

## create shib-conf file ------------------------

