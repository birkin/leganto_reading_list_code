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
    settings: dict = load_settings()
    for entry in exclusions_list:
        search_code = entry.replace( ' ', '.' )
        print( search_code )
        ## check if the search_code exists in the filtered-files directory


def load_initial_settings() -> dict:
    """ Loads envar settings.
        Called by manage_build_reading_list() """
    settings = {
        'SOURCEFILES_DIR_PATH': f'{os.environ["LGNT__CSV_OUTPUT_DIR_PATH"]}/2022-12-07_full_reading_lists',                   
        'OUTPUTFILES_DIR_PATH': f'{os.environ["LGNT__CSV_OUTPUT_DIR_PATH"]}/2022-12-08_filtered_reading_lists',
        # 'EXCLUSIONS_DIR_PATH': f'{os.environ["LGNT__CSV_OUTPUT_DIR_PATH"]}/2022-12-08_exclusion_files',                   
    }
    log.debug( f'settings-keys, ``{pprint.pformat( sorted(list(settings.keys())) )}``' )
    return settings


if __name__ == '__main__':
    run_double_check( exclusions_list )