"""
Queries the reserves database for `audiolinks` data, 
    which contains audio data from from `2010-Nov-05` through `2016-Jun-26`.
Can be run as stand-alone file, or called `import make_audiolinks_json_data`
"""

import logging, os, sys

PROJECT_CODE_DIR = os.environ['LGNT__PROJECT_CODE_DIR']
sys.path.append( PROJECT_CODE_DIR )

from lib import db_stuff


LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'make_audiolinks_json_data logging ready' )


## setup paths ------------------------------------------------------


# # fast-reconcile
# PROJECT_DIR = os.path.dirname( CONFIG_DIR )  
# #print "PROJECT_DIR =" + PROJECT_DIR

# # dir enclosing fast-reconcile
# PROJECT_STUFF_DIR = os.path.dirname( PROJECT_DIR )  
# #print "PROJECT_STUFF_DIR =" + PROJECT_STUFF_DIR

# # allows statements like `from fast-reconcile.the_app import...`
# sys.path.append( PROJECT_DIR )


## get db connection ------------------------------------------------
# db_connection: pymysql.connections.Connection = db_stuff.get_db_connection()  # connection configured to return rows in dictionary format
db_connection = db_stuff.get_mysqlclient_db_connection()  # connection configured to return rows in dictionary format


1/0






# """
# Queries the reserves database for past PDF file-data.
# Can be run as stand-alone file, or is also called by loaders.rebuild_pdf_data_if_necessary()
# """

# import datetime, json, logging, os, pprint

# import pymysql
# from lib import db_stuff

# PDF_SQL: str = os.environ['LGNT__PDF_SQL']
# PDF_JSON_PATH: str = os.environ['LGNT__PDF_JSON_PATH']
# LOG_PATH: str = os.environ['LGNT__LOG_PATH']

# logging.basicConfig(
#     filename=LOG_PATH,
#     level=logging.DEBUG,
#     format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
#     datefmt='%d/%b/%Y %H:%M:%S' )
# log = logging.getLogger(__name__)
# log.debug( 'logging ready' )


# ## get db connection ------------------------------------------------
# db_connection: pymysql.connections.Connection = db_stuff.get_db_connection()  # connection configured to return rows in dictionary format

# ## run query --------------------------------------------------------
# start_time = datetime.datetime.now()
# result_set: list = []
# with db_connection:
#     with db_connection.cursor() as db_cursor:
#         db_cursor.execute( PDF_SQL )
#         result_set = list( db_cursor.fetchall() )  # list() only needed for pylance type-checking
#         assert type(result_set) == list
# record: dict = result_set[0]
# assert type(record) == dict
# log.debug( f'record, ``{record}``' )
# log.debug( f'result_set, ``{pprint.pformat(result_set[0:5])}``' )
# end_time = datetime.datetime.now()
# elapsed: str = str( end_time - start_time )
# log.debug( f'query took, ``{elapsed}``' )

# ## parse results ----------------------------------------------------


# pdf_data: dict = {}
# for entry in result_set:
#     result: dict = entry
#     rqst_id = result.get( 'requestid', '' )
#     if rqst_id:
#         key = result['requestid']
#         val = {
#             'articleid': result.get( 'articleid', '' ),
#             'atitle': result.get( 'atitle', '' ),
#             'filename': result.get( 'filename', '' ),
#             'pdfid': result.get( 'pdfid', '' ),
#             'title': result.get( 'title', '' )
#         }
#         pdf_data[key] = val 

# ## save data --------------------------------------------------------
# # jsn: str = json.dumps( result_set, sort_keys=True, indent=2 )
# jsn: str = json.dumps( pdf_data, sort_keys=True, indent=2 )
# log.debug( f'type(jsn), ``{type(jsn)}``' )
# with open( PDF_JSON_PATH, 'w' ) as f_writer:
#     f_writer.write( jsn )

# ## EOF