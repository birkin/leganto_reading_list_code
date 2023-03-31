import logging, os

import pymysql
from lib import db_stuff

## setup logging ----------------------------------------------------
LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


def get_email_from_bruid( bru_id: str ) -> str:
    """ Returns email address for given bru_id.
        Called by... ZZ"""
    ## make modified bru_id -----------------------------------------
    modified_bru_id = ''
    if bru_id[0] == '0':
        modified_bru_id = bru_id[1:]  # seems most of the ocra bru_ids are missing the leading zero
    ## run query to get email address -------------------------------
    db_connection: pymysql.connections.Connection = db_stuff.get_db_connection()  # connection configured to return rows in dictionary format
    if modified_bru_id:
        # sql = f"SELECT * FROM `banner_dump` WHERE (`inst_bruid` = '{modified_bru_id}' OR `inst_bruid` = '{bru_id}')"
        sql = f"SELECT `inst_email`, `inst_bruid` FROM `banner_dump` WHERE (`inst_bruid` = '{modified_bru_id}' OR `inst_bruid` = '{bru_id}')"
    else:
        # sql = f"SELECT * FROM `banner_dump` WHERE `inst_bruid` = '{bru_id}'"
        sql = f"SELECT `inst_email`, `inst_bruid` FROM `banner_dump` WHERE `inst_bruid` = '{bru_id}'"
    log.debug( f'sql, ``{sql}``' )
    result_set: list = []
    with db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor.execute( sql )
            result_set = list( db_cursor.fetchall() )  # list() only needed for pylance type-checking
            assert type(result_set) == list
    log.debug( f'result_set, ``{result_set}``' )
    email = ''
    if result_set:
        email = result_set[0].get( 'email', None )
    log.debug( f'email, ``{email}``' )
    return email


def get_class_id_entries( course_department_code: str, course_number: str ) -> list:
    """ Finds one or more class_id entries from given course_id.
        Example course_department_code, 'BIOL'; example course_number, '1234a'.
        Called by manage_build_reading_list() -> prep_classes_info() """
    class_id_list = []
    ## run query to get class_id entries ----------------------------
    db_connection: pymysql.connections.Connection = db_stuff.get_db_connection()  # connection configured to return rows in dictionary format
    sql = f"SELECT * FROM `banner_courses` WHERE `subject` LIKE '{course_department_code}' AND `course` LIKE '{course_number}' ORDER BY `banner_courses`.`term` DESC"
    log.debug( f'sql, ``{sql}``' )
    result_set: list = []
    with db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor.execute( sql )
            result_set = list( db_cursor.fetchall() )  # list() only needed for pylance type-checking
            assert type(result_set) == list
    log.debug( f'result_set, ``{result_set}``' )
    if result_set:
        for entry in result_set:
            class_id = entry.get( 'classid', None )
            if class_id:
                class_id_str = str( class_id )
                class_id_list.append( class_id_str )
        if len( result_set ) > 1:
            log.debug( f'more than one class-id found for course_id, ``{course_department_code}.{course_number}``' )
    log.debug( f'class_id_list, ``{class_id_list}``' )
    return class_id_list
