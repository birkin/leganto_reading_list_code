""" Iterates through source reading-list files,
    - Creates a filtered list of reading-list files, excludes a preset list of course-codes.
    - Creates a reading-list file for each excluded course-code. """

import logging, os, pprint

LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


## controller -------------------------------------------------------

def manage_filtered_build():
    """ Manages build of filtered reading-list files and of individual reading-list files for each excluded course-code. 
        Called by if __name__ == '__main__' """
    ## settings -----------------------------------------------------
    settings: dict = load_initial_settings()
    ## get exclusions -----------------------------------------------
    exclusions = manage_exclusions()
    ## get reading-list files ---------------------------------------
    source_filepaths = get_source_readinglist_files( settings )
    ## iterate through source files ---------------------------------
    exclusion_dict = make_exclusions_dict( exclusions )
    for source_filepath in source_filepaths:
        ## get data-rows --------------------------------------------
        source_file_lines = get_source_file_lines( source_filepath )
        filtered_file_lines = []
        ## iterate through data-rows --------------------------------
        for i, line in enumerate( source_file_lines ):
            if i == 0:
                continue  # skip header
            process_line( line, exclusion_dict, filtered_file_lines, settings )
        break
    log.debug( f'filtered_file_lines, ``{pprint.pformat(filtered_file_lines)}``' )
    log.debug( f'exclusion_dict, ``{pprint.pformat(exclusion_dict)}``' )
    return


def process_line( line: str, exclusion_dict: dict, filtered_file_lines: list, settings: dict ) -> None:
    """ Processes a line from a source file. 
        Returns nothing, but updates exclusion_dict and filtered_file_lines.
        Called by manage_filtered_build() """
    log.debug( f'line, ``{line}``' )
    ## get course-code ----------------------------------------------
    simple_course_code = get_simple_course_code( line )
    log.debug( f'simple_course_code, ``{simple_course_code}``' )
    ## if course-code is in exclusions, append to exclusion-dict entry 
    if simple_course_code in exclusion_dict:
        log.debug( f'adding line to exclusion_dict' )
        exclusion_dict[simple_course_code].append( line )
    else:
        log.debug( f'adding line to filtered_file_lines' )
        filtered_file_lines.append( line )    
    return





## called functions -------------------------------------------------


def get_simple_course_code( line: str ) -> str:
    """ Converts OIT course-code to a simplified version.
        Called by process_line() """
    oit_course_code = line.split( '\t' )[0]
    parts: list = oit_course_code.split('.')
    new_simple_course_code: str = parts[1].upper() + '_' + parts[2].upper()
    assert type(new_simple_course_code) == str
    log.debug( f'before, ``{oit_course_code}``; after, ``{new_simple_course_code}``' )
    return new_simple_course_code


def make_exclusions_dict( exclusions: list ) -> dict:
    """ Returns a dict of exclusions.
        Called by manage_filtered_build() """
    exclusion_dict = {}
    for exclusion in exclusions:
        updated_key = exclusion.replace( ' ', '_' ) # for use in file-names, eventually
        exclusion_dict[updated_key] = []
    log.debug( f'exclusion_dict, ``{pprint.pformat(exclusion_dict)[0:100]}...``' )
    return exclusion_dict


def get_source_file_lines( source_filepath: str ) -> list:
    """ Returns a list of data-rows from the source file.
        Called by manage_filtered_build() """
    with open( source_filepath, 'r' ) as f:
        source_file_lines = f.readlines()
    log.debug( f'len(source_file_lines), ``{len(source_file_lines)}`` for source_filepath, ``{source_filepath}``' )
    return source_file_lines


def load_initial_settings() -> dict:
    """ Loads envar settings.
        Called by manage_build_reading_list() """
    settings = {
        'SOURCEFILES_DIR_PATH': f'{os.environ["LGNT__CSV_OUTPUT_DIR_PATH"]}/archived/2022-12-07_reading_lists',                   
        'OUTPUTFILES_DIR_PATH': f'{os.environ["LGNT__CSV_OUTPUT_DIR_PATH"]}/2022-12-08_filtered_reading_lists',                   
    }
    log.debug( f'settings-keys, ``{pprint.pformat( sorted(list(settings.keys())) )}``' )
    return settings


def manage_exclusions() -> list:
    """ Returns a list of course-codes to be excluded from the filtered reading-list files. """
    original_exclusions: list = get_original_exclusions()
    validate_original_exclusions( original_exclusions )
    final_exclusions: list = get_final_exclusions( original_exclusions )
    return final_exclusions


def validate_original_exclusions( original_exclusions: list ) -> None:
    """ Split the course-code, 
        ensure the first part has 3 or 4 uppercase characters, 
        and the second part has four characters optionally followed by a lowercase character. 
        If not valid, raise an error.
        Called by manage_exclusions() """
    for course_code in original_exclusions:
        if course_code == '???':
            continue
        else:
            parts = course_code.split( ' ' )
            assert len(parts) == 2
            first_part = parts[0]
            second_part = parts[1]
            assert len(first_part) in [3, 4]
            assert len(second_part) in [4, 5]
            assert first_part.isupper()
            assert second_part.isalnum()
            assert second_part[0:4].isnumeric()
            if len(second_part) == 5:
                assert second_part[4].islower()
    return 


def get_original_exclusions() -> list:
    """ Returns a list of course-codes to be excluded from the filtered reading-list files. 
        This list is from the 2022-12-07-Wed export spreadsheet emailed around 4:30pm
        Called by manage_exclusions() """
    original_exclusions: list = [
        'POBS 0105',
        'ANTH 1990',
        'ANTH 1901',
        'JUDS 0063',
        'PHIL 1125',
        'ARTS 1001',
        'ARTS 1001',
        'ARTS 1002',
        'BIOL 0530',
        'BIOL 1945',
        'EDUC 1230',
        'HIST 1266d',
        'AMST 1500b',
        'EAST 0141',
        'CLAS 1770',
        '???',
        'COLT 1810g',
        'EAST 0531',
        'EAST 0703',
        'CSCI 1870',
        'TAPS 1600',
        'TAPS 2545',
        'EAST 0411',
        'EDUC 1310',
        'EDUC 2320',
        'ENGL 1050o',
        'ENVS 1232',
        'ENVS 1920',
        'POLS 2320',
        'AMST 1905z',
        'RELS 0545',
        'GNSS 1961w',
        'TAPS 1230',
        'HCL 2080',
        'HIST 1120',
        'HIST 0624',
        'HIST 1120',
        'HMAN 2401i',
        'POLS 0400',
        '???',
        '???',
        'EAST 0402',
        'JAPN 0812',
        'FREN 1070k',
        'HIST 0150c',
        '???',
        'MCM 1701w',
        'PHP 2120',
        'MGRK 0300',
        'EDUC 0870',
        'MUSC 9000',
        'MUSC 0021l',
        'PHIL 0991s',
        'PHIL 1470',
        'POLS 1822q',
        'POLS 1824s',
        'HIST 1156',
        'HIST 2971w',
        'HMAN 1975r',
        'RELS 0012',
        'RELS 1530h',
        'ENGL 0511q',
        'SLAV 1260',
        '???',
        'MUSC 2100',
        'MUSC 2100',
        'POLS 1824k',
        'AMST 1611m',
        'AMST 1905n',
        'ENGL 1050o',
        'ENGL 1191d',
    ]
    return original_exclusions

    ## end def get_original_exclusions()
    

def get_final_exclusions( original_exclusions: list ) -> list:
    """ Remove all the '???' entries from the original_exclusions list, skip duplicate entries, and sort the entries. 
        Called by manage_exclusions() """
    final_exclusions: list = []
    for course_code in original_exclusions:
        if course_code == '???':
            log.debug( 'skipping `???`' )
            continue
        else:
            if course_code in final_exclusions:
                log.debug( f'skipping duplicate, ``{course_code}``' )
                continue
            else:  
                final_exclusions.append( course_code )
    final_exclusions.sort()
    assert final_exclusions == [
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
    ]  # i know I'm building this, but i'm putting this assert here for quick-access reference
    """
    from logging...
    skipping duplicate, ``ARTS 1001``
    skipping `???`
    skipping duplicate, ``HIST 1120``
    skipping `???`
    skipping `???`
    skipping `???`
    skipping `???`
    skipping duplicate, ``MUSC 2100``
    skipping duplicate, ``ENGL 1050o``
    len of final_exclusions, ``62`` 
    """
    # log.debug( f'len of final_exclusions, ``{len(final_exclusions)}``' )
    # log.debug( f'final_exclusions, ``{pprint.pformat(final_exclusions)}``' )
    return final_exclusions

    ## end def get_final_exclusions()


def get_source_readinglist_files( settings: dict ) -> list:
    """ Returns a list of source reading-list absolute filepaths ending in '.txt', sorted.
        Called by manage_filtered_build() """
    source_filepaths = []
    for filename in os.listdir( settings['SOURCEFILES_DIR_PATH'] ):
        if filename.endswith('.txt'):
            source_filepaths.append( f'{settings["SOURCEFILES_DIR_PATH"]}/{filename}' )
    source_filepaths.sort()
    log.debug( f'source_filepaths, ``{pprint.pformat(source_filepaths)}``' )
    return source_filepaths


if __name__ == "__main__":
    manage_filtered_build()
