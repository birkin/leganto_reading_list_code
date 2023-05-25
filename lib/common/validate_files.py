""" Validates encoding, delimiter, and column-names of files. """
    
import csv, logging, os


LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


def is_utf8_encoded(file_path):
    utf8_validity: bool = False
    with open(file_path, 'rb') as file:
        try:
            file_content = file.read().decode('utf-8')
            utf8_validity = True
        except UnicodeDecodeError:
            utf8_validity = False
    log.debug( f'utf8_validity, ``{utf8_validity}``' )
    return utf8_validity


def is_tab_separated(file_path):
    with open(file_path, newline='', encoding='utf-8') as file:
        # dialect = csv.Sniffer().sniff(file.read(1024))
        dialect = csv.Sniffer().sniff( file.read() )
        log.debug( f'dialect.delimiter, ``{dialect.delimiter}``' )
        delimiter_is_tab: bool = dialect.delimiter == '\t'
        log.debug( f'delimiter_is_tab, ``{delimiter_is_tab}``' )
        return delimiter_is_tab


def OIT_columns_are_valid( file_path: str ) -> bool:
    line = ''
    with open( file_path, 'r' ) as f:
        line = f.readline()
    parts = line.split( '\t' )
    stripped_parts = [ part.strip() for part in parts ]
    try:
        assert len(stripped_parts) == 34, len(stripped_parts )
        assert stripped_parts == ['COURSE_CODE', 'COURSE_TITLE', 'SECTION_ID', 'ACAD', 'PROC_DEPT', 'TERM1', 'TERM2', 'TERM3', 'TERM4', 'START_DATE', 'END_DATE', 'NUM_OF_PARTIICIPANTS', 'WEEKLY_HOURS', 'YEAR', 'SEARCH_ID1', 'SEARCH_ID2', 'MULTI_SEARCH_ID', 'INSTR1', 'INSTR2', 'INSTR3', 'INSTR4', 'INSTR5', 'INSTR6', 'INSTR7', 'INSTR8', 'INSTR9', 'INSTR10', 'ALL_INSTRUCTORS', 'OPERATION', 'OLD_COURSE_CODE', 'OLD_COURSE_SECTION', 'SUBMIT_LISTS_BY', 'CAMPUS_AND_PARTICIPANTS', 'READING_LIST_NAME'], stripped_parts
        column_check = True
    except:
        log.exception( 'file not as expected' )
        column_check = False
    log.debug( f'column_check, ``{column_check}``' )
    return column_check

def already_in_leganto_columns_valid( filepath: str ) -> bool:
    """ Ensures tsv file is as expected.
        Called by main() """
    check_result = False
    line = ''
    with open( filepath, 'r' ) as f:
        line = f.readline()
    parts = line.split( '\t' )
    stripped_parts = [ part.strip() for part in parts ]
    log.debug( f'stripped_parts, ``{stripped_parts}``' )
    if stripped_parts == [
        'Reading List Id', 
        'Reading List Owner', 
        'Academic Department', 
        'Reading List Code',                        # when good, like: "brown.pols.1420.2023-spring.s01"
        'Reading List Name',                        # sometimes contains strings, eg: "HIST 1120" or "ENVS1232"
        'Course Code',                              # sometimes contains the `Reading List Code` value, or a string-segment like "EAST 0141"
        'Course Section', 
        'Course Name', 
        'Course Instructor', 
        'Course Instructor Primary Identifier', 
        'Course Instructor With Primary Identifier', 
        'Course Instructor Preferred Email'         # if not empty, contains one email-address, or multiple email-addresses, separated by a semi-colon.
        ]:
        check_result = True
    log.debug( f'check_result, ``{check_result}``' )
    return check_result

# def already_in_leganto_columns_valid( filepath: str ) -> bool:
#     """ Ensures tsv file is as expected.
#         Called by main() """
#     check_result = False
#     line = ''
#     with open( filepath, 'r' ) as f:
#         line = f.readline()
#     parts = line.split( '\t' )
#     stripped_parts = [ part.strip() for part in parts ]
#     log.debug( f'stripped_parts, ``{stripped_parts}``' )
#     if stripped_parts == [
#         'Reading List Id', 
#         'Reading List Owner', 
#         'Academic Department', 
#         'Reading List Code',                        # when good, like: "brown.pols.1420.2023-spring.s01"
#         'Reading List Name',                        # sometimes contains strings, eg: "HIST 1120" or "ENVS1232"
#         'Course Code',                              # sometimes contains the `Reading List Code` value, or a string-segment like "EAST 0141"
#         'Course Section', 
#         'Course Name', 
#         'Course Instructor', 
#         'Course Instructor Identifier', 
#         'Course Instructor With Primary Identifier', 
#         'Course Instructor Preferred Email'         # if not empty, contains one email-address, or multiple email-addresses, separated by a semi-colon.
#         ]:
#         check_result = True
#     log.debug( f'check_result, ``{check_result}``' )
#     return check_result
