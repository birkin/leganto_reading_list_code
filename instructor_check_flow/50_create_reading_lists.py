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
from lib import loaders
from lib import readings_processor
from lib.cdl import CDL_Checker

## grab env vars ----------------------------------------------------
JSON_DATA_DIR_PATH: str = os.environ['LGNT__JSON_DATA_DIR_PATH']
CSV_DATA_DIR_PATH: str = os.environ['LGNT__CSV_OUTPUT_DIR_PATH']
log.debug( f'JSON_DATA_DIR_PATH, ``{JSON_DATA_DIR_PATH}``' )
log.debug( f'CSV_DATA_DIR_PATH, ``{CSV_DATA_DIR_PATH}``' )

## globals ----------------------------------------------------------
JSON_DATA_SOURCE_PATH = f'{JSON_DATA_DIR_PATH}/oit_data_04.json'
datetimestamp = datetime.datetime.now().isoformat().replace( ':', '-' )[0:2]  # two decimal places is enough
TSV_DATA_OUTPUT_PATH = f'{CSV_DATA_DIR_PATH}/2023_summer/list_{datetimestamp}.tsv'
log.debug( f'JSON_DATA_SOURCE_PATH, ``{JSON_DATA_SOURCE_PATH}``' )
log.debug( f'TSV_DATA_OUTPUT_PATH, ``{TSV_DATA_OUTPUT_PATH}``' )


## controller -------------------------------------------------------

def main():
    """ Controller.
        Called by if __name__ == '__main__' """
    
    ## settings -----------------------------------------------------
    settings: dict = load_initial_settings()
    ## load/prep necessary data -------------------------------------
    err: dict = loaders.rebuild_pdf_data_if_necessary( {'days': settings["PDF_OLDER_THAN_DAYS"]} )
    if err:
        raise Exception( f'problem rebuilding pdf-json, error-logged, ``{err["err"]}``' )  
    
    ## load source file ---------------------------------------------
    data_holder_dict = {}
    with open( JSON_DATA_SOURCE_PATH, 'r' ) as f:
        data_holder_dict = json.loads( f.read() )
    
    ## process courses ----------------------------------------------
    all_courses_enhanced_data = []
    for ( i, (course_key, course_data_val) ) in enumerate( data_holder_dict.items() ):
        if course_key == '__meta__':
            continue
        log.debug( f'processing course_key, ``{course_key}``')
        log.debug( f'processing course_data_val, ``{pprint.pformat(course_data_val)}``')

        ## get ocra data --------------------------------------------
        ocra_course_data: dict = course_data_val['ocra_course_data']  # { 'class_id_1234': {'articles': [], 'audios': [], etc...}, 'class_id_2468': {'articles': [], 'audios': [], etc...} }
        log.debug( f'ocra_course_data, ``{pprint.pformat(ocra_course_data)}``' )

        ## combine all same-formats ---------------------------------  # cuz there could be multiple class_id results for a course
        combined_course_data_dict = combine_course_data( ocra_course_data )
        
        ## prepare data for enhancements ----------------------------
        course_id = f'%s%s' % ( course_key.split('.')[0].upper(), course_key.split('.')[1].upper )  # e.g., 'ENGL1234'
        oit_course_id = course_data_val['oit_course_id']
        cdl_checker = CDL_Checker()
        oit_section_id = 'S01'
        oit_title = course_data_val['oit_course_title']

        ## enhance articles -----------------------------------------
        combined_articles = combined_course_data_dict['ocra_articles']
        enhanced_articles = readings_processor.map_articles( combined_articles, course_id, oit_course_id, cdl_checker, oit_section_id, oit_title, settings )

        ## enhance audios -------------------------------------------
        combined_audios = combined_course_data_dict['ocra_audios']
        enhanced_audios: list = readings_processor.map_audio_files( combined_audios, oit_course_id, cdl_checker, oit_section_id, oit_title, settings )

        ## enhance books --------------------------------------------
        combined_books = combined_course_data_dict['ocra_books']
        enhanced_books: list = readings_processor.map_books( combined_books, oit_course_id, oit_section_id, oit_title, cdl_checker )

        ## enhance ebooks -------------------------------------------
        combined_ebooks = combined_course_data_dict['ocra_ebooks']
        enhanced_ebooks: list = readings_processor.map_ebooks( combined_ebooks, course_id, oit_course_id, cdl_checker, oit_section_id, oit_title, settings )

        ## enhance excerpts -----------------------------------------
        combined_excerpts = combined_course_data_dict['ocra_excerpts']
        enhanced_excerpts: list = readings_processor.map_excerpts( combined_excerpts, course_id, oit_course_id, cdl_checker, oit_section_id, oit_title, settings )



        ## enhance movies -------------------------------------------
        combined_movies = combined_course_data_dict['ocra_movies']
        enhanced_movies: list = readings_processor.map_movies( combined_movies, oit_course_id, cdl_checker, oit_section_id, oit_title, settings )



        ## enhance tracks -------------------------------------------
        combined_tracks = combined_course_data_dict['ocra_tracks']
        enhanced_tracks: list = readings_processor.map_tracks( combined_tracks, course_id, oit_course_id, oit_section_id, oit_title )

        ## enhance videos -------------------------------------------
        combined_videos = combined_course_data_dict['ocra_videos']
        enhanced_videos: list = readings_processor.map_videos( combined_videos, oit_course_id, cdl_checker, oit_section_id, oit_title, settings )

        ## enhance websites -----------------------------------------
        combined_websites = combined_course_data_dict['ocra_websites']
        enhanced_websites: list = readings_processor.map_websites( combined_websites, course_id, oit_course_id, cdl_checker, oit_section_id, oit_title, settings )

        ## combine data ---------------------------------------------
        course_enhanced_data: list = enhanced_articles + enhanced_audios + enhanced_books + enhanced_ebooks + enhanced_excerpts + enhanced_tracks + enhanced_videos + enhanced_websites
        all_courses_enhanced_data = all_courses_enhanced_data + course_enhanced_data

        # if i > 2:
        #     break

        # end for-course loop...

    ## apply final leganto processing -------------------------------
    leganto_data: list = prep_leganto_data( all_courses_enhanced_data, settings )

    ## save ---------------------------------------------------------
    csv_maker.create_csv( leganto_data, leganto_final_processor.get_headers() )

    return

    ## end main()


## helper functions ---------------------------------------------


def load_initial_settings() -> dict:
    """ Loads envar settings.
        Called in setup. """
    settings = {
        'COURSES_FILEPATH': os.environ['LGNT__COURSES_FILEPATH'],                   # path to OIT course-data
        'PDF_OLDER_THAN_DAYS': 30,                                                  # to ascertain whether to requery OCRA for pdf-data
        'CREDENTIALS': json.loads( os.environ['LGNT__SHEET_CREDENTIALS_JSON'] ),    # gspread setting
        'SPREADSHEET_NAME': os.environ['LGNT__SHEET_NAME'],                         # gspread setting
        'LAST_CHECKED_PATH': os.environ['LGNT__LAST_CHECKED_JSON_PATH'],            # contains last-run spreadsheet course-IDs
        'PDF_JSON_PATH': os.environ['LGNT__PDF_JSON_PATH'],                         # pre-extracted pdf data
        'FILES_URL_PATTERN': os.environ['LGNT__FILES_URL_PATTERN'],                 # pdf-url
        'TRACKER_JSON_FILEPATH': os.environ['LGNT__TRACKER_JSON_FILEPATH'],         # json-tracker filepath
    }
    PDF_DATA = {}
    with open( settings['PDF_JSON_PATH'], encoding='utf-8' ) as f_reader:
        jsn: str = f_reader.read()
        PDF_DATA = json.loads( jsn )
    log.debug( f'PDF_DATA (partial), ``{pprint.pformat(PDF_DATA)[0:1000]}``' )
    settings['PDF_DATA'] = PDF_DATA
    log.debug( f'settings-keys, ``{pprint.pformat( sorted(list(settings.keys())) )}``' )
    return settings


def combine_course_data( ocra_course_data ) -> dict:
    combined_articles = []
    combined_audios = []
    combined_books = []
    combined_ebooks = []
    combined_excerpts = []
    combined_movies = []
    combined_tracks = []
    combined_videos = []
    combined_websites = []
    for class_id_key, results_dict_val in ocra_course_data.items():
        log.debug( f'class_id_key, ``{class_id_key}``' )
        log.debug( f'results_dict_val, ``{pprint.pformat(results_dict_val)}``' )
        combined_articles += results_dict_val['article_results']
        combined_audios += results_dict_val['audio_results']
        combined_books += results_dict_val['book_results']
        combined_ebooks += results_dict_val['ebook_results']
        combined_excerpts += results_dict_val['excerpt_results']
        combined_movies += results_dict_val['movie_results']
        combined_tracks += results_dict_val['tracks_results']
        combined_videos += results_dict_val['video_results']
        combined_websites += results_dict_val['website_results']
    course_data_dict = {
        'ocra_articles': combined_articles,
        'ocra_audios': combined_audios,
        'ocra_books': combined_books,
        'ocra_ebooks': combined_ebooks,
        'ocra_excerpts': combined_excerpts,
        'ocra_movies': combined_movies,
        'ocra_tracks': combined_tracks,
        'ocra_videos': combined_videos,
        'ocra_websites': combined_websites,
        }
    log.debug( f'course_data_dict, ``{pprint.pformat(course_data_dict)}``' )
    return course_data_dict


def prep_leganto_data( basic_data: list, settings: dict ) -> list:
    """ Enhances basic data for CSV-files. 
        Called by main() """
    leganto_data: list = []
    for entry in basic_data:
        log.debug( f'result-dict-entry, ``{pprint.pformat(entry)}``' )
        result: dict = entry
        row_dict = {}
        headers: list = leganto_final_processor.get_headers()
        for entry in headers:
            header: str = entry
            row_dict[header] = ''
        log.debug( f'default row_dict, ``{pprint.pformat(row_dict)}``' )
        course_code_found: bool = False if 'oit_course_code_not_found' in result['coursecode'] else True
        row_dict['citation_author'] = leganto_final_processor.clean_citation_author( result['citation_author'] ) 
        row_dict['citation_doi'] = result['citation_doi']
        row_dict['citation_end_page'] = result['citation_end_page']
        row_dict['citation_isbn'] = result['citation_isbn']
        row_dict['citation_issn'] = result['citation_issn']
        row_dict['citation_issue'] = result['citation_issue']
        row_dict['citation_journal_title'] = result['citation_journal_title']
        row_dict['citation_publication_date'] = result['citation_publication_date']
        row_dict['citation_public_note'] = 'Please contact rock-reserves@brown.edu if you have problem accessing the course-reserves material.' if result['external_system_id'] else ''
        row_dict['citation_secondary_type'] = leganto_final_processor.calculate_leganto_type( result['citation_secondary_type'] )
        row_dict['citation_source'] = leganto_final_processor.calculate_leganto_citation_source( result )
        row_dict['citation_start_page'] = result['citation_start_page']
        row_dict['citation_status'] = 'BeingPrepared' if result['external_system_id'] else ''
        row_dict['citation_title'] = leganto_final_processor.clean_citation_title( result['citation_title'] )
        row_dict['citation_volume'] = result['citation_volume']
        row_dict['coursecode'] = leganto_final_processor.calculate_leganto_course_code( result['coursecode'] )
        row_dict['reading_list_code'] = row_dict['coursecode'] if result['external_system_id'] else ''
        # row_dict['citation_library_note'] = leganto_final_processor.calculate_leganto_staff_note( result['citation_source1'], result['citation_source2'], result['citation_source3'], result['external_system_id'] )
        row_dict['citation_library_note'] = leganto_final_processor.calculate_leganto_staff_note( result['citation_source1'], result['citation_source2'], result['citation_source3'], result['external_system_id'], result.get('citation_library_note', '') )
        if row_dict['citation_library_note'] == 'NO-OCRA-BOOKS/ARTICLES/EXCERPTS-FOUND':
            result['external_system_id'] = 'NO-OCRA-BOOKS/ARTICLES/EXCERPTS-FOUND'  # so this will appear in the staff spreadsheet
        row_dict['reading_list_name'] = result['reading_list_name'] if result['external_system_id'] else ''
        row_dict['reading_list_status'] = 'BeingPrepared' if result['external_system_id'] else ''
        row_dict['section_id'] = result['section_id']
        row_dict['section_name'] = 'Resources' if result['external_system_id'] else ''
        row_dict['visibility'] = 'RESTRICTED' if result['external_system_id'] else ''
        log.debug( f'updated row_dict, ``{pprint.pformat(row_dict)}``' )
        leganto_data.append( row_dict )
    log.debug( f'leganto_data, ``{pprint.pformat(leganto_data)}``' )
    return leganto_data


if __name__ == '__main__':
    main()
    sys.exit()
