import logging


log = logging.getLogger(__name__)


def get_headers() -> list:
    """ Getter for headers.
        Called by manage_build_reading_list() -> prep_leganto_data() """
    headers = [
        'coursecode', 'section_id', 'searchable_id1', 'searchable_id2', 'searchable_id3', 'reading_list_code', 
        'reading_list_name', 'reading_list_description', 'reading_list_subject', 'reading_list_status', 'RLStatus', 
        'visibility', 'reading_list_assigned_to', 'reading_list_library_note', 'reading_list_instructor_note', 
        'owner_user_name', 'creativecommon', 'section_name', 'section_description', 'section_start_date', 
        'section_end_date', 'section_tags', 'citation_secondary_type', 'citation_status', 'citation_tags', 
        'citation_mms_id', 'citation_original_system_id', 'citation_title', 'citation_journal_title', 'citation_author', 
        'citation_publication_date', 'citation_edition', 'citation_isbn', 'citation_issn', 
        'citation_place_of_publication', 'citation_publisher', 'citation_volume', 'citation_issue', 'citation_pages', 
        'citation_start_page', 'citation_end_page', 'citation_doi', 'citation_oclc', 'citation_lccn', 
        'citation_chapter', 'rlterms_chapter_title', 'citation_chapter_author', 'editor', 'citation_source', 
        'citation_source1', 'citation_source2', 'citation_source3', 'citation_source4', 'citation_source5', 
        'citation_source6', 'citation_source7', 'citation_source8', 'citation_source9', 'citation_source10', 
        'citation_note', 'additional_person_name', 'file_name', 'citation_public_note', 'license_type', 
        'citation_instructor_note', 'citation_library_note', 'external_system_id'
    ]
    log.debug( f'header-count, ``{len(headers)}``' )
    return headers


def clean_citation_title( db_title: str ) -> str:
    log.debug( f'db_title initially, ``{db_title}``' )
    if db_title:
        db_title = db_title.strip()
        if '(EXCERPT)' in db_title:
            db_title = db_title.replace( '(EXCERPT)', '' )
        db_title = db_title.strip()
        if db_title[-1] == ':':
            db_title = db_title[0:-1]
        if db_title[-1] == '.':
            log.debug( 'found period' )
            db_title = db_title[0:-1]
        if db_title[0] == '“':  # starting smart-quotes
            ## remove initial-smart-quotes if there's only one, and only one end-smart-quotes, and it's at the end.
            log.debug( 'found starting smart-quotes' )
            count_start: int = db_title.count( '“' )
            if count_start == 1:
                count_end: int = db_title.count( '”' )
                if count_end == 1:
                    if db_title[-1] == '”':  # ok, remove both
                        db_title = db_title[1:-1]
        if db_title[0] == '“':
            count_quotes: int = db_title.count( '“' )
            if count_quotes == 1:
                db_title = db_title[1:] 
        if db_title[0] == '"':
            ## remove initial-quotes if there are two, and the other is at the end.
            log.debug( 'found starting simple-quotes' )
            count_quotes: int = db_title.count( '"' )
            if count_quotes == 2:
                if db_title[-1] == '"':  # ok, remove both
                    db_title = db_title[1:-1]
        if db_title[0] == '"':
            count_quotes: int = db_title.count( '"' )
            if count_quotes == 1:
                db_title = db_title[1:]
        db_title = db_title.strip()
    log.debug( f'db_title cleaned, ``{db_title}``' )
    return db_title


def clean_citation_author( db_author: str ) -> str:
    log.debug( f'db_author initially, ``{db_author}``' )
    if db_author:
        db_author = db_author.strip()
        if db_author[0] == ',':
            db_author = db_author[1:]
        if db_author[-1] == ',':
            db_author = db_author[0:-1]
        db_author = db_author.strip()
    log.debug( f'db_author cleaned, ``{db_author}``' )
    return db_author


def calculate_end_column( number_of_columns: int ) -> str:
    """ Calculates end-column string from number-of-columns. """
    alphabet: list = list( 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' )
    result = ''
    if number_of_columns <= 26:
        zero_length = number_of_columns - 1
        result: str = alphabet[zero_length]
    else:
        ( multiple, remainder ) = divmod( number_of_columns, 26 )
        log.debug( f'multiple, ``{multiple}``; remainder, ``{remainder}``' )
        zero_multiple: int = multiple - 1
        zero_remainder: int = remainder - 1
        char_one: str = alphabet[zero_multiple]
        char_two: str = alphabet[zero_remainder]
        result = f'{char_one}{char_two}'
    log.debug( f'result, ``{result}``' )
    return result


# def calculate_leganto_title( title: str ) -> str:
#     """ Removes `(EXCERPT) ` if necessary. """
#     return_title = title
#     if '(EXCERPT)' in title:
#         return_title = title.replace( '(EXCERPT)', '' )
#         return_title = return_title.strip()
#     log.debug( f'return_title, ``{return_title}``' )
#     return return_title


def calculate_leganto_type( perceived_type: str ) -> str:
    """ Converts `ARTICLE` to `JR` """
    return_type = perceived_type
    if perceived_type == 'ARTICLE':
        return_type = 'JR'
    log.debug( f'return_type, ``{return_type}``' )
    return return_type


def calculate_leganto_course_code( data_string: str ) -> str:
    """ Removes commentary if necessary. """
    calculated_course_code = data_string
    if 'oit_course_code_not_found' in data_string:
        calculated_course_code = ''
    log.debug( f'calculated_course_code, ``{calculated_course_code}``' )
    return calculated_course_code


def calculate_leganto_citation_source( result: dict ) -> str:
    """ Prioritizes PDF, then CDL. """
    link: str = ''
    possible_pdf_data: str = result['citation_source4']
    possible_cdl_data: str = result['citation_source1']
    if possible_pdf_data:
        log.debug( f'in `possible_pdf_data`; possible_pdf_data, ``{possible_pdf_data}``')
        if possible_pdf_data == 'no_pdf_found':
            link = ''
        else:
            link = possible_pdf_data
    elif possible_cdl_data:
        log.debug( f'in `possible_cdl_data`; possible_cdl_data, ``{possible_cdl_data}``')
        if possible_cdl_data == 'TODO -- handle multiple possible results':
            link = ''
        elif possible_cdl_data == 'no CDL link found':
            link = ''
        elif 'CDL link' in possible_cdl_data:
            # log.debug( 'here' )
            link = possible_cdl_data.replace( 'CDL link likely: <', '' )
            link = link.replace( 'CDL link possibly: <', '' )
            link = link.replace( '>', '' )
        else:
            link = possible_cdl_data
    log.debug( f'link, ``{link}``' )
    return link


def calculate_leganto_staff_note( possible_full_text: str, possible_openurl: str ) -> str:
    """ Returns possibly-helpful info for staff. """
    log.debug( f'possible_full_text, ``{possible_full_text}``' )
    log.debug( f'possible_openurl, ``{possible_openurl}``' )
    message = ''
    if possible_full_text:
        message = f'Possible full-text link: <{possible_full_text}>.'
    if possible_openurl:
        if 'https' in possible_openurl:
            params: str = possible_openurl.split( 'openurl?' )[1]  # sometimes there's a link, but with no parameters.
            if params:
                log.debug( 'params exist' )
                ourl_message: str = f'Occasionally-helpful link: <{possible_openurl}>.'
                if message:
                    message = f'{message} {ourl_message}'
                else:
                    message = ourl_message
    log.debug( f'staff-message, ``{message}``' )
    return message