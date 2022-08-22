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
        """ Looks up required fields from OIT course_info. """
        log.debug( f'preparing leganto coursecode for {ss_course_id}' )
        for row in self.OIT_course_data:
            log.debug( f'row, ``{pprint.pformat(row)}``' )
            break

        return 'foo'

    ## end class OIT_Course_Loader()