import datetime, json, logging, os, pprint

import pymysql
from lib import db_stuff

PDF_SQL: str = os.environ['LGNT__PDF_SQL']
PDF_JSON_PATH: str = os.environ['LGNT__PDF_JSON_PATH']
LOG_PATH: str = os.environ['LGNT__LOG_PATH']

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


## get db connection ------------------------------------------------
db_connection: pymysql.connections.Connection = db_stuff.get_db_connection()  # connection configured to return rows in dictionary format

## run query --------------------------------------------------------
start_time = datetime.datetime.now()
result_set: list = []
with db_connection:
    with db_connection.cursor() as db_cursor:
        db_cursor.execute( PDF_SQL )
        result_set = list( db_cursor.fetchall() )  # list() only needed for pylance type-checking
        assert type(result_set) == list
record: dict = result_set[0]
assert type(record) == dict
log.debug( f'record, ``{record}``' )
end_time = datetime.datetime.now()
elapsed: str = str( end_time - start_time )
log.debug( f'query took, ``{elapsed}``' )

## parse results ----------------------------------------------------
# TODO if necessary

## save data --------------------------------------------------------
jsn: str = json.dumps( result_set, sort_keys=True, indect=2 )
with open( PDF_JSON_PATH, 'w' ) as f_writer:
    f_writer.write( jsn )

## EOF