import logging, os, pprint


## setup logging ----------------------------------------------------
LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


def parse_line( data_line: str, heading_line: str, line_number: int ) -> dict:
    """ Parses OIT data-line.
        Called by main() """
    log.debug( 'starting parse_line()')
    assert type(data_line) == str
    assert type(heading_line) == str
    assert type(line_number) == int
    parts = data_line.split( '\t' )
    parts = [ part.strip() for part in parts ]
    heading_parts = heading_line.split( '\t' )
    heading_parts = [ part.strip() for part in heading_parts ]
    line_dict = {}
    for i, part in enumerate( parts ):
        line_dict[heading_parts[i]] = part
    if line_number < 5:
        log.debug( f'line_dict, ``{pprint.pformat(line_dict)}``' )
    return line_dict


def parse_course_code( data_line, i ):
    """ Parses OIT course-code into dict. """
    assert type(data_line) == str
    assert type(i) == int
    parts = data_line.split( '\t' )
    parts = [ part.strip() for part in parts ]
    ## parse course code --------------------------------------------
    course_code_parts: list = parts[0].split( '.' )
    if i < 5:
        log.debug( f'processing course_code_parts, ``{course_code_parts}``' )
    course_code_dict = {
        'course_code_institution': course_code_parts[0],
        'course_code_department': course_code_parts[1],
        'course_code_number': course_code_parts[2],
        'course_code_year_and_term': course_code_parts[3],
        # 'course_code_section': course_code_parts[4] 
        }
    ## handle missing section
    if len(course_code_parts) == 5:
        course_code_dict['course_code_section'] = course_code_parts[4]
    else:
        log.debug( 'adding EMPTY section' )
        course_code_dict['course_code_section'] = 'EMPTY'
        # course_code_section_missing_count += 1
    ## handle year and term
    course_code_year = course_code_parts[3].split('-')[0]
    course_code_term = course_code_parts[3].split('-')[1]
    course_code_dict['course_code_year'] = course_code_year
    course_code_dict['course_code_term'] = course_code_term
    if i < 5:
        log.debug( f'course_code_dict, ``{pprint.pformat(course_code_dict)}``' )
    return course_code_dict
