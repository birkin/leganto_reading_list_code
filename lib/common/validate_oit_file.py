""" Validates that OIT file is tab-delimted, and that it is also encoded as utf-8. 
    Based on ChatGPT, 2023-Feb-28, prompt:
    "Write a python script that could validate that a file is both comma-separated and encoded as UTF-8." """
    
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


def columns_are_valid( file_path ):
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