import logging, os

import pymysql
import pymysql.cursors

log = logging.getLogger(__name__)

HOST = os.environ['LGNT__DB_HOST']

USERNAME = os.environ['LGNT__DB_USERNAME']
PASSWORD = os.environ['LGNT__DB_PASSWORD']
DB = os.environ['LGNT__DB_DATABASE_NAME']

CDL_USERNAME = os.environ['LGNT__CDL_DB_USERNAME']
CDL_PASSWORD = os.environ['LGNT__CDL_DB_PASSWORD']
CDL_DB = os.environ['LGNT__CDL_DB_DATABASE_NAME']


def get_db_connection() -> pymysql.connections.Connection:
    """ Returns a connection to the database. """
    try:
        db_connection: pymysql.connections.Connection = pymysql.connect(  ## the with auto-closes the connection on any problem
                host=HOST,
                user=USERNAME,
                password=PASSWORD,
                database=DB,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor )  # DictCursor means results will be dictionaries (yay!)
        log.debug( f'made db_connection with PyMySQL.connect(), ``{db_connection}``' )
    except:
        log.exception( f'PyMySQL.connect() failed; traceback follows...' )
        raise   ## re-raise the exception
    return db_connection


def get_CDL_db_connection():  # yes, yes, i should obviously refactor these two
    db_connection = pymysql.connect(  ## the with auto-closes the connection on any problem
            host=HOST,
            user=CDL_USERNAME,
            password=CDL_PASSWORD,
            database=CDL_DB,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor )  # DictCursor means results will be dictionaries (yay!)
    log.debug( f'made db_connection with PyMySQL.connect(), ``{db_connection}``' )
    return db_connection
