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
from lib import readings_extractor, readings_processor

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
    updated_data_holder_dict = {}
    for ( i, (course_key, course_data_dict) ) in enumerate( data_holder_dict.items() ):
        log.debug( f'processing course_key, ``{course_key}``')
        if course_key == '__meta__':
            continue
        ## add basic course data to new data-holder -----------------
        basic_course_data = {
            'ocra_class_id_to_instructor_email_map_for_matches': course_data_dict['ocra_class_id_to_instructor_email_map_for_matches'],
            'oit_bruid_to_email_map': course_data_dict['oit_bruid_to_email_map'],
            'oit_course_id': course_data_dict['oit_course_id'],
            'oit_course_title': course_data_dict['oit_course_title'],
            'status': 'not_yet_processed',
        }
        updated_data_holder_dict[course_key] = basic_course_data
        ## switch to new data-holder --------------------------------
        course_data_dict = updated_data_holder_dict[course_key]
        ## add inverted email-match map -----------------------------
        existing_classid_to_email_map = course_data_dict['ocra_class_id_to_instructor_email_map_for_matches']
        inverted_ocra_classid_email_map = make_inverted_ocra_classid_email_map( existing_classid_to_email_map )
        course_data_dict['inverted_ocra_classid_email_map'] = inverted_ocra_classid_email_map
        log.debug( f'course_data_dict, ``{pprint.pformat(course_data_dict)}``' )
        ## get class_ids --------------------------------------------
        relevant_course_classids = inverted_ocra_classid_email_map.values()
        log.debug( f'relevant_course_classids, ``{pprint.pformat(relevant_course_classids)}``' )

        ## process relevant class_ids ------------------------------------
        all_course_results = {}
        for class_id in relevant_course_classids:
            ## ------------------------------------------------------
            ## GET OCRA DATA ----------------------------------------
            ## ------------------------------------------------------            
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

            ## combine results ------------------------------------------
            classid_results = {
                'book_results': book_results,
                'article_results': article_results,
                'audio_results': audio_results,
                'ebook_results': ebook_results,
                'excerpt_results': excerpt_results,
                'video_results': video_results,
                'website_results': website_results,
                'tracks_results': tracks_results,
            }
            all_course_results[class_id] = classid_results


            # ## ------------------------------------------------------
            # ## MAP OCRA DATA TO LEGANTO DATA ------------------------           
            # ## ------------------------------------------------------
            # ## leganto article data ---------------------------------
            # leg_articles: list = readings_processor.map_articles( article_results, course_id, leganto_course_id, cdl_checker, leganto_section_id, leganto_course_title, settings )
            # ## leganto audio data (from article-table) --------------
            # leg_audios: list = readings_processor.map_audio_files( audio_results, leganto_course_id, cdl_checker, leganto_section_id, leganto_course_title, settings )
            # ## leganto book data ------------------------------------            
            # leg_books: list = readings_processor.map_books( book_results, leganto_course_id, leganto_section_id, leganto_course_title, cdl_checker )
            # ## leganto ebook data -----------------------------------
            # leg_ebooks: list = readings_processor.map_ebooks( ebook_results, course_id, leganto_course_id, cdl_checker, leganto_section_id, leganto_course_title, settings )
            # ## leganto excerpt data ---------------------------------
            # leg_excerpts: list = readings_processor.map_excerpts( excerpt_results, course_id, leganto_course_id, cdl_checker, leganto_section_id, leganto_course_title, settings )
            # ## leganto video data -----------------------------------
            # leg_videos: list = readings_processor.map_videos( video_results, leganto_course_id, cdl_checker, leganto_section_id, leganto_course_title, settings )
            # ## leganto website data ---------------------------------
            # leg_websites: list = readings_processor.map_websites( website_results, course_id, leganto_course_id, cdl_checker, leganto_section_id, leganto_course_title, settings )
            # ## leganto tracks data ----------------------------------
            # leg_tracks: list = readings_processor.map_tracks( tracks_results, course_id, leganto_course_id, leganto_section_id, leganto_course_title )
            # ## leganto combined data --------------------------------
            # # all_course_results: list = leg_articles + leg_books + leg_ebooks + leg_excerpts + leg_websites + leg_audios + leg_videos
            # # all_course_results: list = leg_articles + leg_audios + leg_books + leg_ebooks + leg_excerpts + leg_videos + leg_websites  
            # all_course_results: list = leg_articles + leg_audios + leg_books + leg_ebooks + leg_excerpts + leg_tracks + leg_videos + leg_websites  
            # if all_course_results == []:
            #     all_course_results: list = [ readings_processor.map_empty(leganto_course_id, leganto_section_id, leganto_course_title) ]

        course_data_dict['ocra_course_data'] = all_course_results
        # log.debug( f'ocra_course_data, ``{pprint.pformat(course_data_dict["ocra_course_data"])}``')

        if i > 2:
            break

    ## end for loop

    log.debug( f'updated_data_holder_dict, ``{pprint.pformat(updated_data_holder_dict)}``' )

    ## update meta --------------------------------------------------
    data_holder_dict['__meta__'] = meta

    ## save class_ids data ------------------------------------------
    with open( JSON_DATA_OUTPUT_PATH, 'w' ) as f:
        jsn = json.dumps( data_holder_dict, sort_keys=True, indent=2 )
        f.write( jsn )

    return

    ## end main()


## helper functions ---------------------------------------------


def make_inverted_ocra_classid_email_map( existing_classid_to_email_map ) -> dict:
    """ Converts `existing_classid_to_email_map` to `inverted_ocra_classid_email_map
        Takes a dict like:
            {   '10638': 'person_A@brown.edu',
                '8271': 'person_A@brown.edu',
                '8500': 'person_B@brown.edu'
                '8845': 'person_A@brown.edu' }
        ...and returns a dict like:
            {   'person_A@brown.edu': '10638',
                'person_B@brown.edu': '8500'  }
        Allows for multiple class_ids per email, and returns the highest (latest) class_id. 
        Called by main() """
    ## convert keys to integers and sort them -----------------------
    int_keys = sorted( [int(key) for key in existing_classid_to_email_map.keys()] )
    temp_int_dict = {}
    for key in int_keys:
        temp_int_dict[key] = existing_classid_to_email_map[str(key)]
    inverted_ocra_classid_email_map = {}
    for ( class_id_key, email_val ) in temp_int_dict.items():
        inverted_ocra_classid_email_map[email_val] = str( class_id_key )
    log.debug( f'inverted_ocra_classid_email_map, ``{pprint.pformat(inverted_ocra_classid_email_map)}``' )
    return inverted_ocra_classid_email_map


if __name__ == '__main__':
    main()
    sys.exit()
