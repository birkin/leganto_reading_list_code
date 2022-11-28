import logging, os, pprint
import urllib.parse

from lib import cdl

LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)


MAPPED_CATEGORIES: dict = {
    'coursecode': '',
    'section_id': '',
    'citation_secondary_type': '',
    'citation_title': '',
    'citation_journal_title': '',
    'citation_author': '',
    'citation_publication_date': '',
    'citation_doi': '',
    'citation_isbn': '',
    'citation_issn': '',
    'citation_volume': '',
    'citation_issue': '',
    'citation_start_page': '',
    'citation_end_page': '',
    'citation_source1': '',
    'citation_source2': '',
    'citation_source3': '',
    'citation_source4': '',
    'external_system_id': '',
    'reading_list_name': ''
}

def filter_article_table_results( all_articles_results ):
    """ Takes all article results and puts them in proper buckets.
        Called by build_reading_list.prep_basic_data() """
    assert type(all_articles_results) == list
    log.debug( f'count of all_articles_results, ``{len(all_articles_results)}``' )
    ( article_results, audio_results, ebook_results, excerpt_results, video_results, website_results ) = ( [], [], [], [], [], [] )
    for result in all_articles_results:
        if 'format' in result.keys():
            if result['format'].strip() == 'article':
                article_results.append( result )
            elif result['format'].strip() == 'audio':
                audio_results.append( result )
            elif result['format'].strip() == 'ebook':
                ebook_results.append( result )
            elif result['format'].strip() == 'excerpt':
                excerpt_results.append( result )
            elif result['format'].strip() == 'video':
                video_results.append( result )
            elif result['format'].strip() == 'website':
                website_results.append( result )
            else:
                log.debug( f'unknown format, ``{result["format"]}``' )
        else:   # no format
            log.debug( f'no format, ``{result}``' )
    log.debug( f'count of article_results, ``{len(article_results)}``' )
    log.debug( f'count of audio_results, ``{len(audio_results)}``' )
    log.debug( f'count of ebook_results, ``{len(ebook_results)}``' )
    log.debug( f'count of excerpt_results, ``{len(excerpt_results)}``' )
    log.debug( f'count of video_results, ``{len(video_results)}``' )
    log.debug( f'count of website_results, ``{len(website_results)}``' )
    filtered_results = {
        'article_results': article_results,
        'audio_results': audio_results,
        'ebook_results': ebook_results,
        'excerpt_results': excerpt_results,
        'video_results': video_results,
        'website_results': website_results }    
    log.debug( f'filtered_results, ``{pprint.pformat(filtered_results)}``' )
    return filtered_results  

    ## end def filter_article_table_results()  


## articles ---------------------------------------------------------


def map_articles( article_results: list, course_id: str, leganto_course_id: str, cdl_checker, leganto_section_id: str, leganto_course_title: str, settings: dict ) -> list:
    mapped_articles = []
    for article_result in article_results:
        mapped_article: dict = map_article( article_result, course_id, leganto_course_id, cdl_checker, leganto_section_id, leganto_course_title, settings )
        mapped_articles.append( mapped_article )
    return mapped_articles


def map_article( initial_article_data: dict, course_id: str, leganto_course_id: str, cdl_checker, leganto_section_id: str, leganto_course_title: str, settings: dict ) -> dict:
    """ This function maps the data from the database to the format required by the Leganto API. 
        Notes: 
        - the `course_id` is used for building the url for the leganto citation_source4 field (the pdf-url).
        - the `leganto_course_code` is used for the leganto `coursecode` field. """
    log.debug( f'initial_article_data, ``{pprint.pformat(initial_article_data)}``' )
    mapped_article_data: dict = MAPPED_CATEGORIES.copy()
    ourl_parts: dict = parse_openurl( initial_article_data['sfxlink'] )
    mapped_article_data['citation_author'] = f'{initial_article_data["aulast"]}, {initial_article_data["aufirst"]}'
    mapped_article_data['citation_doi'] = initial_article_data['doi']
    mapped_article_data['citation_end_page'] = str(initial_article_data['epage']) if initial_article_data['epage'] else parse_end_page_from_ourl( ourl_parts )
    mapped_article_data['citation_issn'] = initial_article_data['issn']
    mapped_article_data['citation_issue'] = initial_article_data['issue']
    mapped_article_data['citation_publication_date'] = str( initial_article_data['date'] )
    mapped_article_data['citation_secondary_type'] = 'ARTICLE'  # guess
    mapped_article_data['citation_source1'] = cdl.run_article_cdl_check( initial_article_data['facnotes'], initial_article_data['atitle'], cdl_checker )
    mapped_article_data['citation_source2'] = initial_article_data['art_url']  
    mapped_article_data['citation_source3'] = map_bruknow_openurl( initial_article_data.get('sfxlink', '') )  
    # mapped_article_data['citation_source4'] = check_pdfs( initial_article_data, CSV_DATA, course_id )
    mapped_article_data['citation_source4'] = check_pdfs( initial_article_data, settings['PDF_DATA'], course_id, settings )
    mapped_article_data['citation_start_page'] = str(initial_article_data['spage']) if initial_article_data['spage'] else parse_start_page_from_ourl( ourl_parts )
    mapped_article_data['citation_title'] = initial_article_data['atitle'].strip()
    mapped_article_data['citation_journal_title'] = initial_article_data['title']
    mapped_article_data['citation_volume'] = initial_article_data['volume']
    # mapped_article_data['coursecode'] = f'{course_id[0:8]}'
    mapped_article_data['coursecode'] = leganto_course_id    
    mapped_article_data['external_system_id'] = initial_article_data['requests.requestid']
    mapped_article_data['reading_list_name'] = leganto_course_title
    mapped_article_data['section_id'] = leganto_section_id
    log.debug( f'mapped_article_data, ``{pprint.pformat(mapped_article_data)}``' )
    return mapped_article_data


## books ------------------------------------------------------------


def map_books( book_results: list, leganto_course_id: str, leganto_section_id: str, leganto_course_title: str, cdl_checker ) -> list:
    mapped_books = []
    for book_result in book_results:
        mapped_book: dict = map_book( book_result, leganto_course_id, leganto_section_id, leganto_course_title, cdl_checker )
        mapped_books.append( mapped_book )
    return mapped_books


def map_book( initial_book_data: dict, leganto_course_id: str, leganto_section_id: str, leganto_course_title: str, cdl_checker ) -> dict:
    log.debug( f'initial_book_data, ``{pprint.pformat(initial_book_data)}``' )
    mapped_book_data: dict = MAPPED_CATEGORIES.copy()
    mapped_book_data['citation_author'] = initial_book_data['bk_author']
    mapped_book_data['citation_isbn'] = initial_book_data['isbn']
    mapped_book_data['citation_publication_date'] = str(initial_book_data['bk_year']) if initial_book_data['bk_year'] else ''
    mapped_book_data['citation_secondary_type'] = 'BK'
    mapped_book_data['citation_source1'] = cdl.run_book_cdl_check( initial_book_data['facnotes'], initial_book_data['bk_title'], cdl_checker )
    mapped_book_data['citation_source3'] = map_bruknow_openurl( initial_book_data.get('sfxlink', '') )
    mapped_book_data['citation_title'] = initial_book_data['bk_title']
    mapped_book_data['coursecode'] = leganto_course_id
    mapped_book_data['reading_list_name'] = leganto_course_title
    mapped_book_data['external_system_id'] = initial_book_data['requests.requestid']
    mapped_book_data['section_id'] = leganto_section_id
    log.debug( f'mapped_book_data, ``{pprint.pformat(mapped_book_data)}``' )
    return mapped_book_data


## ebooks -----------------------------------------------------------


def map_ebooks( ebook_results: list, course_id: str, leganto_course_id: str, cdl_checker, leganto_section_id: str, leganto_course_title: str, settings: dict ) -> list:
    mapped_ebooks = []
    for ebook_result in ebook_results:
        mapped_ebook: dict = map_ebook( ebook_result, course_id, leganto_course_id, cdl_checker, leganto_section_id, leganto_course_title, settings )
        mapped_ebooks.append( mapped_ebook )
    return mapped_ebooks


def map_ebook( initial_ebook_data: dict, course_id: str, leganto_course_id: str, cdl_checker, leganto_section_id: str, leganto_course_title: str, settings: dict ) -> dict:
    """ This function maps the data from the database to the format required by the Leganto API. 
        Notes: 
        - the `course_id` is used for building the url for the leganto citation_source4 field (the pdf-url).
        - the `leganto_course_code` is used for the leganto `coursecode` field. """
    log.debug( f'initial_ebook_data, ``{pprint.pformat(initial_ebook_data)}``' )
    mapped_ebook_data: dict = MAPPED_CATEGORIES.copy()
    ourl_parts: dict = parse_openurl( initial_ebook_data['sfxlink'] )
    mapped_ebook_data['citation_author'] = parse_ebook_author( initial_ebook_data )
    mapped_ebook_data['citation_doi'] = initial_ebook_data['doi']
    mapped_ebook_data['citation_end_page'] = str(initial_ebook_data['epage']) if initial_ebook_data['epage'] else parse_end_page_from_ourl( ourl_parts )
    mapped_ebook_data['citation_isbn'] = initial_ebook_data['isbn']
    mapped_ebook_data['citation_issn'] = initial_ebook_data['issn']
    mapped_ebook_data['citation_issue'] = initial_ebook_data['issue']
    mapped_ebook_data['citation_publication_date'] = str( initial_ebook_data['date'] )
    mapped_ebook_data['citation_secondary_type'] = 'EBOOK'  # guess
    log.debug( 'about to call run_book_cdl_check() from map_ebook()' )
    # mapped_ebook_data['citation_source1'] = cdl.run_article_cdl_check( initial_ebook_data['facnotes'], initial_ebook_data['title'], cdl_checker )
    mapped_ebook_data['citation_source1'] = cdl.run_book_cdl_check( initial_ebook_data['facnotes'], initial_ebook_data['title'], cdl_checker )
    # mapped_ebook_data['citation_source1'] = 'TEMP-ENTRY'
    mapped_ebook_data['citation_source2'] = initial_ebook_data['art_url']  
    mapped_ebook_data['citation_source3'] = map_bruknow_openurl( initial_ebook_data.get('sfxlink', '') )  
    mapped_ebook_data['citation_source4'] = check_pdfs( initial_ebook_data, settings['PDF_DATA'], course_id, settings )
    mapped_ebook_data['citation_start_page'] = str(initial_ebook_data['spage']) if initial_ebook_data['spage'] else parse_start_page_from_ourl( ourl_parts )
    mapped_ebook_data['citation_title'] = initial_ebook_data['atitle'].strip()
    mapped_ebook_data['citation_journal_title'] = initial_ebook_data['title']
    mapped_ebook_data['citation_volume'] = initial_ebook_data['volume']
    mapped_ebook_data['coursecode'] = leganto_course_id    
    mapped_ebook_data['external_system_id'] = initial_ebook_data['requests.requestid']
    mapped_ebook_data['reading_list_name'] = leganto_course_title
    mapped_ebook_data['section_id'] = leganto_section_id
    log.debug( f'mapped_ebook_data, ``{pprint.pformat(mapped_ebook_data)}``' )
    return mapped_ebook_data

## excerpts ---------------------------------------------------------


def map_excerpts( excerpt_results: list, course_id: str, leganto_course_id: str, cdl_checker, leganto_section_id: str, leganto_course_title: str, settings: dict ) -> list:
    mapped_articles = []
    for excerpt_result in excerpt_results:
        mapped_excerpt: dict = map_excerpt( excerpt_result, course_id, leganto_course_id, cdl_checker, leganto_section_id, leganto_course_title, settings )
        mapped_articles.append( mapped_excerpt )
    return mapped_articles


def map_excerpt( initial_excerpt_data: dict, course_id: str, leganto_course_id: str, cdl_checker, leganto_section_id: str, leganto_course_title: str, settings: dict ) -> dict:
    log.debug( f'initial_excerpt_data, ``{pprint.pformat(initial_excerpt_data)}``' )
    mapped_excerpt_data: dict = MAPPED_CATEGORIES.copy()
    ourl_parts: dict = parse_openurl( initial_excerpt_data['sfxlink'] )
    mapped_excerpt_data['citation_author'] = parse_excerpt_author( initial_excerpt_data )
    mapped_excerpt_data['citation_doi'] = initial_excerpt_data['doi']
    mapped_excerpt_data['citation_end_page'] = str(initial_excerpt_data['epage']) if initial_excerpt_data['epage'] else parse_end_page_from_ourl( ourl_parts )
    mapped_excerpt_data['citation_issn'] = initial_excerpt_data['issn']
    mapped_excerpt_data['citation_issue'] = initial_excerpt_data['issue']
    mapped_excerpt_data['citation_publication_date'] = str( initial_excerpt_data['date'] )
    mapped_excerpt_data['citation_secondary_type'] = 'ARTICLE'  # guess
    mapped_excerpt_data['citation_source1'] = cdl.run_article_cdl_check( initial_excerpt_data['facnotes'], initial_excerpt_data['atitle'], cdl_checker )
    mapped_excerpt_data['citation_source2'] = initial_excerpt_data['art_url']  
    mapped_excerpt_data['citation_source3'] = map_bruknow_openurl( initial_excerpt_data.get('sfxlink', '') )  
    # mapped_excerpt_data['citation_source4'] = check_pdfs( initial_excerpt_data, CSV_DATA, course_id )
    mapped_excerpt_data['citation_source4'] = check_pdfs( initial_excerpt_data, settings['PDF_DATA'], course_id, settings )
    mapped_excerpt_data['citation_start_page'] = str(initial_excerpt_data['spage']) if initial_excerpt_data['spage'] else parse_start_page_from_ourl( ourl_parts )
    mapped_excerpt_data['citation_title'] = f'(EXCERPT) %s' % initial_excerpt_data['atitle'].strip()
    mapped_excerpt_data['citation_journal_title'] = initial_excerpt_data['title']
    mapped_excerpt_data['citation_volume'] = initial_excerpt_data['volume']
    mapped_excerpt_data['coursecode'] = leganto_course_id
    mapped_excerpt_data['external_system_id'] = initial_excerpt_data['requests.requestid']
    mapped_excerpt_data['reading_list_name'] = leganto_course_title
    mapped_excerpt_data['section_id'] = leganto_section_id
    log.debug( f'mapped_excerpt_data, ``{pprint.pformat(mapped_excerpt_data)}``' )
    return mapped_excerpt_data


## mappers ----------------------------------------------------------


def map_empty( leganto_course_id: str, leganto_section_id: str, leganto_course_title: str ) -> dict:
    mapped_data: dict = MAPPED_CATEGORIES.copy()
    mapped_data['coursecode'] = leganto_course_id
    mapped_data['reading_list_name'] = leganto_course_title
    mapped_data['section_id'] = leganto_section_id
    return mapped_data


def map_bruknow_openurl( db_openurl: str ) -> str:
    """ Converts db-openurl (possibly a fragment), to a valid bruknow-openurl.
        Called by map_books(), map_articles(), and map_excerpts() """
    log.debug( f'starting db_openurl, ``{db_openurl}``' )
    bruknow_openurl_pattern: str = 'https://bruknow.library.brown.edu/discovery/openurl?institution=01BU_INST&vid=01BU_INST:BROWN'
    new_openurl = ''
    if db_openurl == '':
        new_openurl = 'no openurl found'
    else:
        ## break ourl out into parts --------------------------------
        parsed_db_ourl = urllib.parse.urlparse( db_openurl )
        log.debug( f'parsed_db_ourl, ``{parsed_db_ourl}``' )
        ## get the query string -------------------------------------
        query_part: str = parsed_db_ourl.query
        log.debug( f'query_part, ``{query_part}``' )
        ## make key-value pairs for urlencode() ---------------------
        param_dct: dict = dict( urllib.parse.parse_qsl(query_part) )
        log.debug( f'param_dct, ``{pprint.pformat(param_dct)}``' )
        if 'url' in param_dct.keys():  # rev-proxy urls can contain the actual sfxlink
            del( param_dct['url'] )
        ## get a nice encoded querystring ---------------------------
        encoded_querystring: str = urllib.parse.urlencode( param_dct, safe=',' )
        log.debug( f'encoded_querystring, ``{encoded_querystring}``' )
        ## build bruknow ourl
        new_openurl = f'%s&%s' % ( bruknow_openurl_pattern, encoded_querystring )
    log.debug( f'new_openurl, ``{new_openurl}``' )
    return new_openurl


## parsers ----------------------------------------------------------


def parse_ebook_author( initial_ebook_data: dict ) -> str:
    """ Checks multiple possible fields for ebook author info.
        Called by map_ebook() """
    assert type (initial_ebook_data) == dict
    first = initial_ebook_data['bk_aufirst']
    last = initial_ebook_data['bk_aulast']
    name = f'{first} {last}'.strip()
    log.debug( f'name, ``{name}``' )
    return name


def parse_excerpt_author( initial_excerpt_data: dict ) -> str:
    """ Checks multiple possible fields for author info.
        Excerpts seem to have author info in multiple places; this function handles that.
        Called by map_excerpt() """
    first: str = initial_excerpt_data.get( 'aufirst', '' )
    if first == '':
        first = initial_excerpt_data.get( 'bk_aufirst', '' )
    last: str = initial_excerpt_data.get( 'aulst', '' )
    if last == '':
        last = initial_excerpt_data.get( 'bk_aulast', '' )
    name = f'{last}, {first}'
    if name.strip() == ',':
        name = 'author_not_found'
    log.debug( f'name, ``{name}``' )
    return name


def parse_openurl( raw_ourl: str ) -> dict:
    """ Returns fielded openurl elements.
        Called by map_article() """
    log.debug( f'raw_ourl, ``{raw_ourl}``' )
    ourl_dct = {}
    if raw_ourl:
        if raw_ourl[0:43] == 'https://login.revproxy.brown.edu/login?url=':
            log.debug( 'removing proxy ' )
            ourl = raw_ourl[43:]
            log.debug( f'updated ourl, ``{ourl}``' )
        else:
            ourl = raw_ourl
        ourl_section: str = ourl.split( '?' )[1]
        ourl_dct: dict = urllib.parse.parse_qs( ourl_section )
    log.debug( f'ourl_dct, ``{pprint.pformat(ourl_dct)}``' )
    return ourl_dct


def parse_start_page_from_ourl( parts: dict ):
    try:
        spage = parts['spage'][0]
    except:
        spage = ''
    log.debug( f'spage, ``{spage}``' )
    return spage


def parse_end_page_from_ourl( parts: dict ):
    try:
        epage = parts['epage'][0]
    except:
        epage = ''
    log.debug( f'epage, ``{epage}``' )
    return epage


## misc helpers -----------------------------------------------------


def check_pdfs( db_dict_entry: dict, pdf_data: dict, course_code: str, settings: dict ) -> str:
    """ Check and return the pdf for the given ocra article or excerpt. 
        Called by map_article() and map_excerpt() 
        Note: course_code does not separate out subject from code; rather, it is like `HIST1234`. """
    log.debug( 'starting check_pdfs()' )
    pdf_check_result = 'no_pdf_found'
    possible_matches = []
    db_entry_request_id: str = db_dict_entry['requests.requestid']
    log.debug( f'db_entry_request_id, ``{db_entry_request_id}``' )
    if db_entry_request_id in pdf_data.keys():
        log.debug( 'match on db request-id' )
        file_info: dict = pdf_data[db_entry_request_id]
        db_article_id: str = str( db_dict_entry['articleid'] )
        assert type(db_article_id) == str
        log.debug( f'looking for match on db_article_id, ``{db_article_id}``' )
        log.debug( f'file_info, ``{pprint.pformat(file_info)}``' )
        file_info_article_id: str = str( file_info['articleid'] )
        assert type( file_info_article_id) == str
        log.debug( f'checking file-info-article-id, ``{file_info_article_id}``' )
        if db_article_id == file_info_article_id:
            log.debug( '...and match on article-id!' )
            pfid = str( file_info['pdfid'] )
            file_name = file_info['filename']
            full_file_name: str = f'{pfid}_{file_name}'
            file_url = f'{settings["FILES_URL_PATTERN"]}'.replace( '{FILENAME}', full_file_name )
            log.debug( f'file_url, ``{file_url}``' )
            possible_matches.append( file_url )
        else:
            log.debug( '...but no match on article-id' ) 
    else:
        log.debug( 'no match on db request-id' )
    if len( possible_matches ) > 0:
        if len( possible_matches ) == 1:
            pdf_check_result = possible_matches[0]
        else:
            pdf_check_result = repr( possible_matches )
    log.debug( f'pdf_check_result, ``{pdf_check_result}``' )
    return pdf_check_result
