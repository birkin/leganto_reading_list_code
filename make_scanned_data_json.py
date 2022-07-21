import csv, json, logging, os, pprint

CSV_PATH: str = os.environ['LGNT__SCANNED_DATA_CSV_PATH']
LOG_PATH: str = os.environ['LGNT__LOG_PATH']

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)


data: dict = {}

with open( CSV_PATH, encoding='utf-8' ) as csv_file_handler:
    csv_dict_reader = csv.DictReader( csv_file_handler )
        
    ## Convert each row into a dictionary and add it to data
    for rows in csv_dict_reader:
            
        ## Let's say 'filename' will be the primary key for now (cuz it should be unique)
        key = rows[ 'filename' ]
        data[key] = rows

log.debug( f'data, ``{pprint.pformat(data)}``' )

jsn = json.dumps( data, sort_keys=True, indent=2 )
with open( '../scanned_data.json', 'w', encoding='utf-8' ) as json_file_handler:
    json_file_handler.write( jsn )
