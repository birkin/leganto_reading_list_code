import datetime, logging, pprint

import gspread
from lib import leganto_final_processor


log = logging.getLogger(__name__)


# def update_gsheet( all_results: list, CREDENTIALS: dict, SPREADSHEET_NAME: str ) -> None:
def update_gsheet( basic_data: list, leganto_data: list, CREDENTIALS: dict, SPREADSHEET_NAME: str ) -> None:
    """ Writes data to gsheet, then...
        - sorts the worksheets so the most recent check appears first in the worksheet list.
        - deletes checks older than the curent and previous checks.
        Called by manage_build_reading_list() """
    ## reformat data
    leganto_ss_data: list = leganto_final_processor.reformat_for_leganto_sheet( leganto_data )
    ## access spreadsheet -------------------------------------------
    log.debug( f'leganto_data, ``{pprint.pformat(leganto_data)}``' )
    credentialed_connection = gspread.service_account_from_dict( CREDENTIALS )
    sheet = credentialed_connection.open( SPREADSHEET_NAME )
    log.debug( f'last-updated, ``{sheet.lastUpdateTime}``' )  # not needed now, but will use it later
    ## process leganto worksheet ------------------------------------
    process_leganto_worksheet( sheet, leganto_ss_data )
    ## process staff worksheet --------------------------------------
    process_staff_worksheet( sheet, basic_data )
    return


def process_leganto_worksheet( sheet, all_results: list ):
    """ Prepares some final data for the spreadsheet. 
        Called by manage_build_reading_list() -> update_gsheet() """
    ## create leganto worksheet -------------------------------------
    dt_stamp: str = datetime.datetime.now().isoformat().split( '.' )[0]
    title: str = f'for_leganto_{dt_stamp}'
    leganto_worksheet = sheet.add_worksheet( title=title, rows=100, cols=20 )
    ## prepare headers ----------------------------------------------
    headers: list = leganto_final_processor.get_headers()
    log.debug( f'headers, ``{headers}``' )
    ## prepare values -----------------------------------------------
    # data_values = []  # for gsheet
    data_values: list = all_results
    ## finalize spreadsheet data ------------------------------------
    end_range_column = calculate_end_column( len(headers) )
    num_entries = len( all_results )
    data_end_range: str = f'{end_range_column}{num_entries + 1}'  # the plus-1 is for the header-row
    log.debug( f'data_end_range, ``{data_end_range}``' )
    new_data = [
        { 
            'range': f'A1:{end_range_column}1',
            'values': [ headers ]
        },
        {
            'range': f'A2:{data_end_range}',
            'values': data_values
        }
    ]
    leganto_worksheet.batch_update( new_data, value_input_option='raw' )
    ## update leganto-sheet formatting ------------------------------
    leganto_worksheet.format( f'A1:{end_range_column}1', {'textFormat': {'bold': True}} )
    # leganto_worksheet.freeze( rows=1, cols=None )
    leganto_worksheet.freeze( rows=1, cols=2 )

    
    ## make leganto-sheet the 2nd sheet -----------------------------
    wrkshts: list = sheet.worksheets()
    log.debug( f'wrkshts, ``{wrkshts}``' )
    reordered_wrkshts: list = [ wrkshts[0], wrkshts[-1] ]
    sheet.reorder_worksheets( reordered_wrkshts )
    wrkshts: list = sheet.worksheets()
    log.debug( f'wrkshts after sort, ``{wrkshts}``' )
    num_wrkshts: int = len( wrkshts )
    log.debug( f'num_wrkshts, ``{num_wrkshts}``' )
    if num_wrkshts > 2:  # keep requested_checks, and the leganto sheet
        wrkshts: list = sheet.worksheets()
        wrkshts_to_delete = wrkshts[2:]
        for wrksht in wrkshts_to_delete:
            sheet.del_worksheet( wrksht )
    wrkshts: list = sheet.worksheets()
    log.debug( f'wrkshts after deletion, ``{wrkshts}``' )
    return

    # end def process_leganto_worksheet()


def process_staff_worksheet( sheet, all_results: list ):
    ## create staff worksheet -------------------------------------
    dt_stamp: str = datetime.datetime.now().isoformat().split( '.' )[0]
    title: str = f'for_staff_{dt_stamp}'
    staff_worksheet = sheet.add_worksheet( title=title, rows=100, cols=20 )
    ## prepare headers ----------------------------------------------
    headers = [
        'coursecode',
        'section_id',
        'citation_secondary_type',
        'citation_title',
        'citation_journal_title',
        'citation_author',
        'citation_publication_date',
        'citation_doi',
        'citation_isbn',
        'citation_issn',
        'citation_volume',
        'citation_issue',
        'citation_start_page',
        'citation_end_page',
        'citation_source1',
        'citation_source2',
        'citation_source3',
        'citation_source4',
        'external_system_id'
        ]
    ## prepare values -----------------------------------------------
    data_values = []
    for entry in all_results:
        entry: dict = entry
        row = [
            entry['coursecode'],
            entry['section_id'],
            entry['citation_secondary_type'],
            entry['citation_title'],
            entry['citation_journal_title'],
            entry['citation_author'],
            entry['citation_publication_date'],
            entry['citation_doi'],
            entry['citation_isbn'],
            entry['citation_issn'],
            entry['citation_volume'],
            entry['citation_issue'],
            entry['citation_start_page'],
            entry['citation_end_page'],
            entry['citation_source1'],
            entry['citation_source2'],
            entry['citation_source3'],
            entry['citation_source4'],
            entry['external_system_id']
            ]
        data_values.append( row )
    log.debug( f'data_values, ``{data_values}``' )
    ## finalize staff data ----------------------------------------
    end_range_column = 'S'
    header_end_range = 'S1'
    num_entries = len( all_results )
    data_end_range: str = f'{end_range_column}{num_entries + 1}'  # the plus-1 is for the header-row
    log.debug( f'data_end_range, ``{data_end_range}``' )
    new_data = [
        { 
            'range': f'A1:{header_end_range}',
            'values': [ headers ]
        },
        {
            'range': f'A2:{data_end_range}',
            'values': data_values
        }
    ]
    log.debug( f'new_data, ``{pprint.pformat(new_data)}``' )
    staff_worksheet.batch_update( new_data, value_input_option='raw' )
    ## update staff-sheet formatting --------------------------------------------
    staff_worksheet.format( f'A1:{end_range_column}1', {'textFormat': {'bold': True}} )
    staff_worksheet.freeze( rows=1, cols=1 )
    ## (no need to sort sheets here)
    return

    # end def process_staff_worksheet()


## helpers ----------------------------------------------------------


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
