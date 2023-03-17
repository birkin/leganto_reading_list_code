"""
Queries the reserves database for `audiolinks` data, 
    which contains audio data from from `2010-Nov-05` through `2016-Jun-26`.
Can be run as stand-alone file, or called `import make_audiolinks_json_data`
"""

import json, logging, os, pprint, sys

import pymysql  # for type-checking

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


AUDIOLINKS_INITIAL_SQL = os.environ['LGNT__AUDIOLINKS_INITIAL_QUERY_SQL']
AUDIOLINKS_SQL2 = os.environ['LGNT__AUDIOLINKS_SQL2']
AUDIOLINKS_SQL3 = os.environ['LGNT__AUDIOLINKS_SQL3']
AUDIOLINKS_JSON_PATH = os.environ['LGNT__AUDIOLINKS_JSON_PATH']


## make initial query -----------------------------------------------
result_set: list = []
db_connection: pymysql.connections.Connection = db_stuff.get_db_connection()  # connection configured to return rows in dictionary format
with db_connection:
    with db_connection.cursor() as db_cursor:
        db_cursor.execute( AUDIOLINKS_INITIAL_SQL )
        result_set = list( db_cursor.fetchall() )  # list() only needed for pylance type-checking
        assert type(result_set) == list
log.debug( f'result_set[0:20], ``{pprint.pformat(result_set[0:20])}``' )

## add course_id ----------------------------------------------------
db_connection: pymysql.connections.Connection = db_stuff.get_db_connection()
with db_connection.cursor() as db_cursor:
    for entry in result_set:
        row: dict = entry
        classid = row['requests__classid']
        log.debug( f'classid, ``{classid}``' )
        if classid == None:
            row['classes__courseid'] = None
        else:
            q2 = AUDIOLINKS_SQL2.replace( '{classid}', str(classid) )
            log.debug( f'q2, ``{q2}``' )
            r_set2: list = []
            db_cursor.execute( q2 )
            r_set2 = list( db_cursor.fetchall() )  # list() only needed for pylance type-checking
            assert type(r_set2) == list
            log.debug( f'len(r_set2), ``{len(r_set2)}``' )
            r_set2_entry: dict = r_set2[0]
            row['classes__courseid'] = r_set2_entry['courseid']
log.debug( f'result_set[0:20], after course_id lookup, ``{pprint.pformat(result_set[0:20])}``' )

## add course_info --------------------------------------------------
db_connection: pymysql.connections.Connection = db_stuff.get_db_connection()
with db_connection.cursor() as db_cursor:
    for entry in result_set:
        row: dict = entry
        courseid = row['classes__courseid']
        log.debug( f'courseid, ``{courseid}``' )
        classid = row['requests__classid']
        log.debug( f'classid, ``{classid}``' )
        if courseid == None or classid == None:
            row['banner_courses__course_title'] = None
            row['banner_courses__subject'] = None
            row['banner_courses__course'] = None
        else:
            q3 = AUDIOLINKS_SQL3.replace( '{courseid}', str(courseid) ).replace( '{classid}', str(classid) )
            log.debug( f'q3, ``{q3}``' )
            r_set3: list = []
            db_cursor.execute( q3 )
            r_set3 = list( db_cursor.fetchall() )  # list() only needed for pylance type-checking
            assert type(r_set3) == list
            log.debug( f'len(r_set3), ``{len(r_set3)}``' )
            r_set3_entry: dict = r_set3[0]
            row['banner_courses__course_title'] = r_set3_entry['course_title']
            row['banner_courses__subject'] = r_set3_entry['subject']
            row['banner_courses__course'] = r_set3_entry['course']
log.debug( f'result_set[0:20], after course lookup, ``{pprint.pformat(result_set[0:20])}``' )

## re-arrange list into dict ----------------------------------------
audiolinks_data: dict = {}
for entry in result_set:
    row: dict = entry
    classid_key = row['requests__classid']
    if classid_key == None:
        classid_key = 'no_classid'
    else: 
        classid_key: str = str(classid_key)
    if classid_key not in audiolinks_data.keys():
        audiolinks_data[classid_key] = []
    audiolinks_data[classid_key].append( row )
log.debug( f'audiolinks_data, ``{pprint.pformat(audiolinks_data)}``' )
    
## output json ------------------------------------------------------
jsn: str = json.dumps( audiolinks_data, sort_keys=True, indent=2 )
log.debug( f'type(jsn), ``{type(jsn)}``' )
with open( AUDIOLINKS_JSON_PATH, 'w' ) as f_writer:
    f_writer.write( jsn )

## EOF