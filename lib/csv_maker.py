import csv, datetime, logging, os, pprint


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


CSV_OUTPUT_DIR_PATH: str = os.environ['LGNT__CSV_OUTPUT_DIR_PATH']


def create_csv( data: list, headers: list ) -> None:
    """ Credit: <https://python-adv-web-apps.readthedocs.io/en/latest/csv.html#writing-from-a-dictionary> """

    log.debug( f'data, ``{pprint.pformat(data)}``' )

    output_filename: str = f'reading_list_{datetime.datetime.now().isoformat()}.csv'.replace( ':', '-' )  # produces, eg, `reading_list_2022-09-06T10-59-04.345469`
    log.debug( f'output_filename, ``{output_filename}``' ) 

    ## open a new file for writing - if file exists, contents will be erased
    csvfile = open('new_file.csv', 'w')

    ## set the headers
    headers = ['Presidency', 'President', 'Wikipedia_entry', 'Took_office', 'Left_office', 'Party', 'Home_state', 'Occupation', 'College', 'Age_when_took_office', 'Birth_date', 'Birthplace', 'Death_date', 'Location_death']

    # # make a new variable - c - for Python's DictWriter object -
    # # note that fieldnames is required
    # c = csv.DictWriter(csvfile, fieldnames=headers)

    # # optional - write a header row
    # c.writeheader()

    # # write all rows from list to file
    # c.writerows(presidents_list)

    # # save and close file
    # csvfile.close()

    return