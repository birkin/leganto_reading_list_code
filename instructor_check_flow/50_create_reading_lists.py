"""
- This script produces reading-list files for each course in "json_data/oit_data_04.json".
- The necessary leganto categories are defined.
- Data is prepared from the OCRA data, with some additional lookups.
    - TODO: Define the addtional lookups.
"""

import datetime, json, logging, os, pprint, sys

## setup logging ----------------------------------------------------
LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )

## update sys.path for project imports  -----------------------------
PROJECT_CODE_DIR = os.environ['LGNT__PROJECT_CODE_DIR']
sys.path.append( PROJECT_CODE_DIR )

## additional imports -----------------------------------------------
from lib import csv_maker
from lib import leganto_final_processor

## grab env vars ----------------------------------------------------
JSON_DATA_DIR_PATH: str = os.environ['LGNT__JSON_DATA_DIR_PATH']
CSV_DATA_DIR_PATH: str = os.environ['LGNT__CSV_OUTPUT_DIR_PATH']
log.debug( f'JSON_DATA_DIR_PATH, ``{JSON_DATA_DIR_PATH}``' )
log.debug( f'CSV_DATA_DIR_PATH, ``{CSV_DATA_DIR_PATH}``' )

## globals ----------------------------------------------------------
JSON_DATA_SOURCE_PATH = f'{JSON_DATA_DIR_PATH}/oit_data_04.json'
datetimestamp = datetime.datetime.now().isoformat().replace( ':', '-' )[0:22]  # two decimal places is enough
TSV_DATA_OUTPUT_PATH = f'{CSV_DATA_DIR_PATH}/2023_summer/list_{datetimestamp}.tsv'
log.debug( f'JSON_DATA_SOURCE_PATH, ``{JSON_DATA_SOURCE_PATH}``' )
log.debug( f'TSV_DATA_OUTPUT_PATH, ``{TSV_DATA_OUTPUT_PATH}``' )


## controller -------------------------------------------------------

def main():
    """ Controller.
        Called by if __name__ == '__main__' """
    
    ## load source file ---------------------------------------------
    data_holder_dict = {}
    with open( JSON_DATA_SOURCE_PATH, 'r' ) as f:
        data_holder_dict = json.loads( f.read() )

    ## initialize meta ----------------------------------------------
    meta = {
        'datetime_stamp': datetime.datetime.now().isoformat(),
        'description': f'Starts with "oit_data_04.json". Produces "{TSV_DATA_OUTPUT_PATH}" file. Defines necessary leganto fields and assembles the data. Then writes it to a .tsv file.',
        'number_of_courses_in_reading_list_file': len( data_holder_dict ) - 1, # -1 for meta
        'number_of_courses_below': 0,
        }
    
    ## initialize leganto fields ------------------------------------
    reading_list_lines = []
    leganto_dict_template = {}
    # leganto_list_header_dict = {}
    leganto_fields = leganto_final_processor.get_headers()
    for field in leganto_fields:
        leganto_dict_template[field] = ''
        # leganto_list_header_dict[field] = field
    # reading_list_lines.append( leganto_list_header_dict )
    # log.debug( f'reading_list_lines, ``{pprint.pformat(reading_list_lines, sort_dicts=False)}``' )
    
    ## process courses ----------------------------------------------
    for ( i, (course_key, course_data_dict) ) in enumerate( data_holder_dict.items() ):
        if course_key == '__meta__':
            continue

        log.debug( f'processing course_key, ``{course_key}``')
        # log.debug( f'course_data_dict, ``{pprint.pformat(course_data_dict)}``')

        leganto_dct = leganto_dict_template.copy()
        leganto_dct['coursecode'] = course_data_dict['oit_course_id']
        # log.debug( f'leganto_dct, ``{pprint.pformat(leganto_dct, sort_dicts=False)}``' )

        ## add to reading_list_lines --------------------------------
        reading_list_lines.append( leganto_dct )

        if i > 2:
            break

    log.debug( f'reading_list_lines, ``{pprint.pformat(reading_list_lines, sort_dicts=False)}``' )

    ## end for-course loop...

    ## delete no-ocra-match courses ---------------------------------

    ## save ---------------------------------------------------------
    csv_maker.create_csv( reading_list_lines, leganto_final_processor.get_headers() )

    # with open( JSON_DATA_OUTPUT_PATH, 'w' ) as f:
    #     try:
    #         jsn = json.dumps( updated_data_holder_dict, sort_keys=True, indent=2 )
    #     except Exception as e:
    #         message = f'problem with json.dumps(); e, ``{e}``'
    #         log.exception( message )
    #         raise Exception( message )
    #     f.write( jsn )

    return

    ## end main()


## helper functions ---------------------------------------------


if __name__ == '__main__':
    main()
    sys.exit()
