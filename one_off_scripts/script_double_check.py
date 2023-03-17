import logging, os, pprint

LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


exclusions_list = [
        'AMST 1500b',
        'AMST 1611m',
        'AMST 1905n',
        'AMST 1905z',
        'ANTH 1901',
        'ANTH 1990',
        'ARTS 1001',
        'ARTS 1002',
        'BIOL 0530',
        'BIOL 1945',
        'CLAS 1770',
        'COLT 1810g',
        'CSCI 1870',
        'EAST 0141',
        'EAST 0402',
        'EAST 0411',
        'EAST 0531',
        'EAST 0703',
        'EDUC 0870',
        'EDUC 1230',
        'EDUC 1310',
        'EDUC 2320',
        'ENGL 0511q',
        'ENGL 1050o',
        'ENGL 1191d',
        'ENVS 1232',
        'ENVS 1920',
        'FREN 1070k',
        'GNSS 1961w',
        'HCL 2080',
        'HIST 0150c',
        'HIST 0624',
        'HIST 1120',
        'HIST 1156',
        'HIST 1266d',
        'HIST 2971w',
        'HMAN 1975r',
        'HMAN 2401i',
        'JAPN 0812',
        'JUDS 0063',
        'MCM 1701w',
        'MGRK 0300',
        'MUSC 0021l',
        'MUSC 2100',
        'MUSC 9000',
        'PHIL 0991s',
        'PHIL 1125',
        'PHIL 1470',
        'PHP 2120',
        'POBS 0105',
        'POLS 0400',
        'POLS 1822q',
        'POLS 1824k',
        'POLS 1824s',
        'POLS 2320',
        'RELS 0012',
        'RELS 0545',
        'RELS 1530h',
        'SLAV 1260',
        'TAPS 1230',
        'TAPS 1600',
        'TAPS 2545'    
    ]


def run_double_check( exclusions_list ):
    """ for each exclusion entry,
        convert the entry to the pattern 'xxxx.1234' 
        and check if it exists anywhere in the filtered-files directory. It shouldn't. """
    settings: dict = load_initial_settings()
    # temp_intential_error_entry = 'afri.0990'
    # exclusions_list.append( temp_intential_error_entry )
    filtered_files_dir_path = settings['FILTERED_FILES_DIR_PATH']
    log.debug( f'filtered_files_dir_path, ``{filtered_files_dir_path}``' )
    ## get a list of the files in the filtered-files directory ------
    all_paths: list = os.listdir( filtered_files_dir_path )
    reading_list_files: list = []
    for entry in all_paths:
        if entry.endswith( '.txt' ):
            reading_list_files.append( entry )
    log.debug( f'reading_list_files, ``{reading_list_files}``' )
    for entry in exclusions_list:
        ## get search-code ------------------------------------------
        search_code = entry.replace( ' ', '.' ).lower()
        log.debug( f'checking exclude_code, ``{search_code}``' )
        ## check if the search_code exists in the filtered-files directory
        for reading_list_file in reading_list_files:
            reading_list_filepath = f'{filtered_files_dir_path}/{reading_list_file}'
            ## open file and see if search_code is in it
            with open( reading_list_filepath, 'r' ) as f:
                contents = f.read()
                if search_code in contents:
                    raise Exception( f'found search_code, ``{search_code}`` in reading_list_filepath, ``{reading_list_filepath}``' )
    log.debug( 'double-check complete' )
    return


def load_initial_settings() -> dict:
    """ Loads envar settings.
        Called by manage_build_reading_list() """
    settings = {
        # 'FILTERED_FILES_DIR_PATH': f'{os.environ["LGNT__CSV_OUTPUT_DIR_PATH"]}/archived/2022-12-08_filtered_reading_lists',
        'FILTERED_FILES_DIR_PATH': f'{os.environ["LGNT__CSV_OUTPUT_DIR_PATH"]}/2022-12-09_filtered_reading_lists',
    }
    log.debug( f'settings-keys, ``{pprint.pformat( sorted(list(settings.keys())) )}``' )
    return settings


if __name__ == '__main__':
    run_double_check( exclusions_list )