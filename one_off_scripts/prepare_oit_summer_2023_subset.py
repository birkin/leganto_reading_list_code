import logging, os, pprint, sys


LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


PROJECT_CODE_DIR = os.environ['LGNT__PROJECT_CODE_DIR']
sys.path.append( PROJECT_CODE_DIR )


OIT_COURSE_LIST_PATH: str = os.environ['LGNT__COURSES_FILEPATH']
log.debug( f'OIT_COURSE_LIST_PATH, ``{OIT_COURSE_LIST_PATH}``' )

## validate OIT file ------------------------------------------------
from lib.common.validate_oit_file import is_utf8_encoded, is_tab_separated
assert is_utf8_encoded(OIT_COURSE_LIST_PATH) == True
# assert is_tab_separated(OIT_COURSE_LIST_PATH) == True

## load OIT file ----------------------------------------------------
lines = []
with open( OIT_COURSE_LIST_PATH, 'r' ) as f:
    lines = f.readlines()

## inspect fields ---------------------------------------------------

## heading line
heading_line = lines[0]
parts = heading_line.split( '\t' )
parts = [ part.strip() for part in parts ]
log.debug( f'parts, ``{pprint.pformat(parts)}``' )

## process data lines
data_lines = lines[1:]
missing_institutions = []
missing_departments = []
missing_numbers = []
missing_years = []
missing_terms = []
missing_sections = []
course_code_institutions = []
course_code_departments = []
# course_code_numbers = []  ## don't need to populate this
course_code_years = []
course_code_terms = []
course_code_sections = []
course_code_section_missing_count = 0
for i, data_line in enumerate( data_lines ):
    log.debug( f'processing data_line, ``{data_line}``' )
    parts = data_line.split( '\t' )
    parts = [ part.strip() for part in parts ]
    course_code_parts: list = parts[0].split( '.' )
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
        course_code_dict['course_code_section'] = 'EMPTY'
        course_code_section_missing_count += 1
    ## handle year and term
    course_code_year = course_code_parts[3].split('-')[0]
    course_code_term = course_code_parts[3].split('-')[1]
    course_code_dict['course_code_year'] = course_code_year
    course_code_dict['course_code_term'] = course_code_term
    if i < 5:
        log.debug( f'course_code_dict, ``{pprint.pformat(course_code_dict)}``' )
    # if i > 6:
    #     break
    ## checks...
    if course_code_dict['course_code_institution'].strip() == '':
        missing_institutions.append( course_code_dict )
    if course_code_dict['course_code_department'].strip() == '':
        missing_departments.append( course_code_dict )
    if course_code_dict['course_code_number'].strip() == '':
        missing_numbers.append( course_code_dict )
    if course_code_dict['course_code_year'].strip() == '':
        missing_years.append( course_code_dict )
    if course_code_dict['course_code_term'].strip() == '':
        missing_terms.append( course_code_dict )
    if course_code_dict['course_code_section'].strip() == '':
        missing_sections.append( course_code_dict )
    ## collect...
    if course_code_dict['course_code_institution'] not in course_code_institutions:
        course_code_institutions.append( course_code_dict['course_code_institution'] )
    if course_code_dict['course_code_department'] not in course_code_departments:       
        course_code_departments.append( course_code_dict['course_code_department'] )
    if course_code_dict['course_code_year'] not in course_code_years:
        course_code_years.append( course_code_dict['course_code_year'] )
    if course_code_dict['course_code_term'] not in course_code_terms:
        course_code_terms.append( course_code_dict['course_code_term'] )
    if course_code_dict['course_code_section'] not in course_code_sections:
        course_code_sections.append( course_code_dict['course_code_section'] )

## log results ------------------------------------------------------
log.debug( f'missing_institutions, ``{pprint.pformat(missing_institutions)}``' )
log.debug( f'missing_departments, ``{pprint.pformat(missing_departments)}``' )
log.debug( f'missing_numbers, ``{pprint.pformat(missing_numbers)}``' )
log.debug( f'missing_years, ``{pprint.pformat(missing_years)}``' )
log.debug( f'missing_terms, ``{pprint.pformat(missing_terms)}``' )
log.debug( f'missing_sections, ``{pprint.pformat(missing_sections)}``' )
log.debug( f'course_code_institutions, ``{pprint.pformat(course_code_institutions)}``' )
log.debug( f'course_code_departments, ``{pprint.pformat(course_code_departments)}``' )
# log.debug( f'course_code_numbers, ``{pprint.pformat(course_code_numbers)}``' )
log.debug( f'course_code_years, ``{pprint.pformat(course_code_years)}``' )
log.debug( f'course_code_terms, ``{pprint.pformat(course_code_terms)}``' )
log.debug( f'course_code_sections, ``{pprint.pformat(course_code_sections)}``' )





# brown.afri.0090.2023-fall.s01