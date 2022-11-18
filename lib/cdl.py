import logging, os, pprint

from fuzzywuzzy import fuzz
from lib import db_stuff


LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)


class CDL_Checker(object):

    def __init__( self ):
        self.CDL_TITLES: list = []

    def populate_cdl_titles( self ) -> list:
        db_connection = db_stuff.get_CDL_db_connection()
        sql = "SELECT * FROM `cdl_app_item` ORDER BY `title` ASC"
        log.debug( f'sql, ``{sql}``' )
        result_set: list = []
        with db_connection:
            with db_connection.cursor() as db_cursor:
                db_cursor.execute( sql )
                result_set = list( db_cursor.fetchall() )
                assert type(result_set) == list
        return result_set


    def search_cdl( self, search_title: str ) -> list:
        """ Fuzzy-searches cdl-titles, returns back score and file_name. """
        log.debug( f'search_title, ``{search_title}``' )
        assert type(search_title) == str
        matches = []
        if len( search_title.strip() ) > 0:
            if self.CDL_TITLES == []:
                log.debug( 'populating CDL_TITLES' )
                self.CDL_TITLES = self.populate_cdl_titles()
                # log.debug( f'CDL_TITLES, ``{pprint.pformat(CDL_TITLES)}``' )
                log.debug( f'len(self.CDL_TITLES), ``{len(self.CDL_TITLES)}``' )
            for entry in self.CDL_TITLES:
                assert type(entry) == dict
                score: int = fuzz.ratio( search_title, entry['title'] )
                if score > 80:
                    entry['fuzzy_score'] = score
                    matches.append( entry )
        log.debug( f'matches, ``{pprint.pformat(matches)}``' )
        return matches

    def prep_cdl_field_text( self, entries: list ) -> str:
        result = 'no CDL link found'
        if len( entries ) == 1:
            entry = entries[0]
            if entry['fuzzy_score'] > 97:
                result = f'CDL link likely: <https://cdl.library.brown.edu/cdl/item/{entry["item_id"]}>'
            else:
                result = f'CDL link possibly: <https://cdl.library.brown.edu/cdl/item/{entry["item_id"]}>'
        elif len( entries ) > 1:
            result: str = f'Multiple possible CDL links: '
            cdl_pattern: str = '<https://cdl.library.brown.edu/cdl/item/ITEM_ID>'
            for ( i, entry ) in enumerate( entries ):
                if i == 0:
                    append_str = cdl_pattern.replace( 'ITEM_ID', entry['item_id'] )
                else:
                    temp_str = cdl_pattern.replace( 'ITEM_ID', entry['item_id'] )
                    append_str = f', {temp_str}'
                result = result + append_str
        log.debug( f'result, ``{result}``' )
        return result

    ## end class CDL_Checker()


def run_book_cdl_check( ocra_facnotes_data: str, ocra_title: str, cdl_checker  ) -> str:
    """ Sees if data contains a CDL reference, and, if so, see if I can find one.
        Called by map_book() and map_article(). 
        TODO -- the same code is run regardless of the if-statement; why?! """
    field_text: str = ocra_facnotes_data
    if 'cdl' in ocra_facnotes_data.lower():
        results: list = cdl_checker.search_cdl( ocra_title )
        field_text: str = cdl_checker.prep_cdl_field_text( results )
    else:
        results: list = cdl_checker.search_cdl( ocra_title )
        field_text: str = cdl_checker.prep_cdl_field_text( results )
        log.debug( f'ADDITIONAL BOOK-CDL CHECK WOULD HAVE FOUND..., ``{field_text}``' )
    log.debug( f'field_text, ``{field_text}``' )
    return field_text


def run_article_cdl_check( ocra_facnotes_data: str, ocra_title: str, cdl_checker  ) -> str:
    """ Sees if data contains a CDL reference, and, if so, see if I can find one.
        Called by map_book() and map_article(). """
    field_text: str = ocra_facnotes_data
    if ocra_facnotes_data == '':
        results: list = cdl_checker.search_cdl( ocra_title )
        field_text: str = cdl_checker.prep_cdl_field_text( results )
        log.debug( f'ARTICLE CDL-CHECK RESULT, ``{field_text}``' )
    log.debug( f'field_text, ``{field_text}``' )
    return field_text
