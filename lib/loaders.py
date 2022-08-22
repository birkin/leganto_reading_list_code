import csv, logging, pprint

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

    def prepare_leganto_coursecode( self, ss_course_id: str ) -> str:
        """ Looks up required fields from OIT course_info. 
            Required leganto format: like `Summer 2022 DATA 2051 S01` (season, year, subject, code, section) """
        log.debug( f'preparing leganto coursecode for {ss_course_id}' )
        leganto_course_code = ss_course_id
        ( ss_subject, ss_code ) = ( ss_course_id[0:4], ss_course_id[4:] )
        log.debug( f'ss_subject, ``{ss_subject}``; ss_code, ``{ss_code}``' )
        for entry in self.OIT_course_data:
            row: dict = entry
            log.debug( f'row, ``{pprint.pformat(row)}``' )
            oit_course_code = row['COURSE_CODE']
            log.debug( f'oit_course_code, ``{oit_course_code}``' )
            parts: list = oit_course_code.split(' ')
            [ oit_season, oit_year, oit_subject, oit_code, oit_section ] = parts
            if ss_subject == oit_subject and ss_code == oit_code:
                leganto_course_code = oit_course_code                
        log.debug( f'leganto_course_code, ``{leganto_course_code}``' )
        return leganto_course_code

    ## end class OIT_Course_Loader()