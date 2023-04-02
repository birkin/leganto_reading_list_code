"""
- This script iterates through "json_data/oit_data_03b.json" OIT-courses.
- For each course's instructor-matching class-ids, it looks up the class_id in the ocra database.
- It pulls out book, article, audio, ebook, excerpt, video, website, and tracks reading-list data.
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
from lib.common.query_ocra import get_class_id_entries
# from lib.common.validate_files import is_utf8_encoded, is_tab_separated, columns_are_valid

## grab env vars ----------------------------------------------------
JSON_DATA_DIR_PATH: str = os.environ['LGNT__JSON_DATA_DIR_PATH']
log.debug( f'JSON_DATA_DIR_PATH, ``{JSON_DATA_DIR_PATH}``' )

## constants --------------------------------------------------------
JSON_DATA_SOURCE_PATH = f'{JSON_DATA_DIR_PATH}/oit_data_03b.json'
JSON_DATA_OUTPUT_PATH = f'{JSON_DATA_DIR_PATH}/oit_data_04.json'
log.debug( f'JSON_DATA_SOURCE_PATH, ``{JSON_DATA_SOURCE_PATH}``' )
log.debug( f'JSON_DATA_OUTPUT_PATH, ``{JSON_DATA_OUTPUT_PATH}``' )

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
        'description': 'Starts with "oit_data_03b.json". Produces "oit_data_04.json". Extracts reading-list data from ocra database for each class_id.',
        'number_of_courses_below': 0,
        }
    
    ## process courses ----------------------------------------------
    for ( i, (course_key, course_data_dict) ) in enumerate( data_holder_dict.items() ):
        log.debug( f'processing course_key, ``{course_key}``')
        if course_key == '__meta__':
            continue
        # log.debug( f'i, ``{i}``')
        # log.debug( f'course_key, ``{course_key}``' )
        # log.debug( f'course_data_dict, ``{pprint.pformat(course_data_dict)}``' )
        ## get class_ids ---------------------------------------------
        relevant_course_classids = []
        for ( class_id_key, email_val ) in course_data_dict['ocra_class_id_to_instructor_email_map_for_matches']:
            relevant_course_classids.append( class_id_key )

        ## ocra book data -------------------------------------------
        book_results: list = readings_extractor.get_book_readings( class_id )
        ## ocra all-artcles data ------------------------------------
        all_articles_results: list = readings_extractor.get_all_articles_readings( class_id )
        ## ocra filtered article data -------------------------------
        filtered_articles_results: dict = readings_processor.filter_article_table_results(all_articles_results)
        article_results = filtered_articles_results['article_results']
        audio_results = filtered_articles_results['audio_results']          # from article-table; TODO rename
        ebook_results = filtered_articles_results['ebook_results'] 
        excerpt_results = filtered_articles_results['excerpt_results']
        video_results = filtered_articles_results['video_results']          
        website_results = filtered_articles_results['website_results']      
        log.debug( f'website_results, ``{pprint.pformat(website_results)}``' )
        ## ocra tracks data -----------------------------------------
        tracks_results: list = readings_extractor.get_tracks_data( class_id )

        if i > 2:
            break


    ## update meta --------------------------------------------------
    data_holder_dict['__meta__'] = meta

    ## save class_ids data ------------------------------------------
    with open( JSON_DATA_OUTPUT_PATH, 'w' ) as f:
        jsn = json.dumps( data_holder_dict, sort_keys=True, indent=2 )
        f.write( jsn )

    return

    ## end main()


if __name__ == '__main__':
    main()
    sys.exit()
