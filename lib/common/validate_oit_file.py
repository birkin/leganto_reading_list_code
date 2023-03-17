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


# file_path = 'example.csv'

# if is_utf8_encoded(file_path) and is_tab_separated(file_path):
#     print(f'The file {file_path} is both tab-separated and encoded as UTF-8')
# else:
#     print(f'The file {file_path} is not both tab-separated and encoded as UTF-8')