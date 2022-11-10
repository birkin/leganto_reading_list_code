import csv, datetime, logging, os, pathlib, pprint


## logging ----------------------------------------------------------

LOG_PATH: str = os.environ['LGNT__LOG_PATH']

log_level_dict: dict = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARNING': logging.WARNING, 'ERROR': logging.ERROR, 'CRITICAL': logging.CRITICAL }    
LOG_LEVEL: str = os.environ['LGNT__LOG_LEVEL']
log_level_value = log_level_dict[LOG_LEVEL]  # yields logging.DEBUG or logging.INFO, etc.
logging.basicConfig(
    filename=LOG_PATH,
    level=log_level_value,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)


class OIT_Course_Loader( object ):

    def __init__(self, COURSES_FILEPATH: str) -> None:
        self.OIT_course_data: list = self.load_OIT_course_data( COURSES_FILEPATH )

    def load_OIT_course_data( self, COURSES_FILEPATH: str ) -> list:
        """ On instantiation, loads courses CSV file into a list of dictionaries. """
        rows = []
        with open( COURSES_FILEPATH ) as f:
            reader = csv.DictReader( f, delimiter = '\t' )
            rows = list(reader)
        return rows

    def grab_oit_course_data( self, ss_course_id: str ) -> dict:
        """ Returns the OIT info for the spreadsheet course-id. 
            Called by manage_build_reading_list -> prep_classes_info() """
        log.debug( f'OIT_course_data - partial, ``{pprint.pformat(self.OIT_course_data)[0:1000]}...``' )
        log.debug( f'preparing oit-data for ss_course_id, ``{ss_course_id}``' )
        ss_subject: str = ss_course_id[0:4]
        ss_code: str = ss_course_id[4:]    
        log.debug( f'ss_subject, ``{ss_subject}``; ss_code, ``{ss_code}``' )
        matcher: str = f'.{ss_subject.lower()}.{ss_code}.'
        log.debug( f'matcher, ``{matcher}``' )
        found_oit_course_data: dict = {}
        for entry in self.OIT_course_data:
            course_entry: dict = entry
            # log.debug( f'course_entry, ``{course_entry}``' )
            oit_course_code = course_entry['COURSE_CODE']
            if matcher in oit_course_code:
                found_oit_course_data = course_entry
                log.debug( 'match found; breaking' )
                break
        log.debug( f'found_oit_course_data, ``{found_oit_course_data}``' )
        return found_oit_course_data

    # def grab_oit_course_data( self, ss_course_id: str ) -> dict:
    #     """ Returns the OIT info for the spreadsheet course-id. """
    #     log.debug( f'OIT_course_data - partial, ``{pprint.pformat(self.OIT_course_data)[0:1000]}...``' )
    #     log.debug( f'preparing oit-data for ss_course_id, ``{ss_course_id}``' )
    #     ss_subject: str = ss_course_id[0:4]
    #     ss_code: str = ss_course_id[4:]    
    #     log.debug( f'ss_subject, ``{ss_subject}``; ss_code, ``{ss_code}``' )
    #     matcher: str = f'{ss_subject} {ss_code}'
    #     found_oit_course_data: dict = {}
    #     for entry in self.OIT_course_data:
    #         course_entry: dict = entry
    #         # log.debug( f'course_entry, ``{course_entry}``' )
    #         oit_course_code = course_entry['COURSE_CODE']
    #         if matcher in oit_course_code:
    #             found_oit_course_data = course_entry
    #             log.debug( 'match found; breaking' )
    #             break
    #     log.debug( f'found_oit_course_data, ``{found_oit_course_data}``' )
    #     return found_oit_course_data

    ## end class OIT_Course_Loader()


def rebuild_pdf_data_if_necessary( days: dict ) -> dict:
    """ Initiates OCRA pdf-data extraction if necessary. 
        Called by build_reading_list.manage_build_reading_list() """
    log.debug( f'days, ``{days}``' )
    num_days: int = days['days']
    return_val = {}
    PDF_JSON_PATH: str = os.environ['LGNT__PDF_JSON_PATH']
    log.debug( f'PDF_JSON_PATH, ``{PDF_JSON_PATH}``' )
    update: bool = determine_update( num_days, PDF_JSON_PATH, datetime.datetime.now()  )
    if update:
        log.debug( 'gonna update the pdf-data -- TODO' )
        try:
            from lib import make_pdf_json_data  # the import actually runs the code
        except Exception as e:
            log.exception( 'problem running pdf-json script' )
            return_val = { 'err': repr(e) }
    else:
        log.debug( 'pdf_data is new enough; not updating' )
    return return_val


def determine_update( days: int, fpath: str, now_time: datetime.datetime ) -> bool:
    """ Determines whether to update given file. 
        Called by rebuild_pdf_data_if_necessary() """
    log.debug( f'days, ``{days}``' )
    log.debug( f'now_time, ``{now_time}``' )
    return_val = False
    last_updated_epoch_timestamp: float = pathlib.Path( fpath ).stat().st_mtime
    dt_last_updated: datetime.datetime = datetime.datetime.fromtimestamp( last_updated_epoch_timestamp )
    cutoff_date: datetime.datetime = dt_last_updated + datetime.timedelta( days )
    log.debug( f'cutoff_date, ``{str(cutoff_date)}``' )
    if cutoff_date < now_time:
        return_val = True
    log.debug( f'return_val, ``{return_val}``' )
    return return_val
