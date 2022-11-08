import logging, pprint

import gspread
from lib import leganto_final_processor


log = logging.getLogger(__name__)


def update_gsheet( all_results: list, CREDENTIALS: dict, SPREADSHEET_NAME: str ) -> None:
    """ Writes data to gsheet, then...
        - sorts the worksheets so the most recent check appears first in the worksheet list.
        - deletes checks older than the curent and previous checks.
        Called by check_bibs() """
    ## access spreadsheet -------------------------------------------
    log.debug( f'all_results, ``{pprint.pformat(all_results)}``' )
    credentialed_connection = gspread.service_account_from_dict( CREDENTIALS )
    sheet = credentialed_connection.open( SPREADSHEET_NAME )
    log.debug( f'last-updated, ``{sheet.lastUpdateTime}``' )  # not needed now, but will use it later
    ## process leganto worksheet ------------------------------------
    process_leganto_worksheet( sheet, all_results )
    ## process staff worksheet --------------------------------------
    process_staff_worksheet( sheet, all_results )
    return


def process_leganto_worksheet( sheet, all_results: list ) -> list:
    ## create leganto worksheet -------------------------------------
    dt_stamp: str = datetime.datetime.now().isoformat().split( '.' )[0]
    title: str = f'for_leganto_{dt_stamp}'
    leganto_worksheet = sheet.add_worksheet( title=title, rows=100, cols=20 )
    ## prepare headers ----------------------------------------------
    headers: list = leganto_final_processor.get_headers()
    log.debug( f'headers, ``{headers}``' )
    ## prepare values -----------------------------------------------
    data_values = []  # for gsheet
    csv_rows = []     # for csv output
    # row_dict = {}
    # for header in headers:
    #     header: str = header
    #     row_dict[header] = ''
    # log.debug( f'default row_dict, ``{pprint.pformat(row_dict)}``' )
    for result in all_results:
        log.debug( f'result-dict-entry, ``{pprint.pformat(result)}``' )
        result: dict = result

        row_dict = {}
        for header in headers:
            header: str = header
            row_dict[header] = ''
        log.debug( f'default row_dict, ``{pprint.pformat(row_dict)}``' )
        
        course_code_found: bool = False if 'oit_course_code_not_found' in result['coursecode'] else True

        # row_dict['citation_author'] = result['citation_author']
        row_dict['citation_author'] = clean_citation_author( result['citation_author'] ) 
        row_dict['citation_doi'] = result['citation_doi']
        row_dict['citation_end_page'] = result['citation_end_page']
        row_dict['citation_isbn'] = result['citation_isbn']
        row_dict['citation_issn'] = result['citation_issn']
        row_dict['citation_issue'] = result['citation_issue']
        row_dict['citation_journal_title'] = result['citation_journal_title']
        row_dict['citation_publication_date'] = result['citation_publication_date']
        row_dict['citation_public_note'] = 'Please contact rock-reserves@brown.edu if you have problem accessing the course-reserves material.' if result['external_system_id'] else ''
        row_dict['citation_secondary_type'] = calculate_leganto_type( result['citation_secondary_type'] )
        row_dict['citation_source'] = calculate_leganto_citation_source( result )
        row_dict['citation_start_page'] = result['citation_start_page']
        row_dict['citation_status'] = 'BeingPrepared' if result['external_system_id'] else ''
        # row_dict['citation_title'] = calculate_leganto_title( result['citation_title'] )
        row_dict['citation_title'] = clean_citation_title( result['citation_title'] )
        row_dict['citation_volume'] = result['citation_volume']
        row_dict['coursecode'] = calculate_leganto_course_code( result['coursecode'] )
        row_dict['reading_list_code'] = row_dict['coursecode'] if result['external_system_id'] else ''
        # row_dict['reading_list_library_note'] = f'Possible full-text link: <{result["citation_source2"]}>.' if result["citation_source2"] else ''
        # row_dict['reading_list_library_note'] = f'Possible full-text link: <https://url_one>./nOccasionally-helpful link: <https://url_two>'
        row_dict['reading_list_library_note'] = calculate_leganto_staff_note( result['citation_source2'], result['citation_source3'] )
        row_dict['reading_list_name'] = result['reading_list_name'] if result['external_system_id'] else ''
        row_dict['reading_list_status'] = 'BeingPrepared' if result['external_system_id'] else ''
        # row_dict['section_id'] = result['section_id']
        row_dict['section_id'] = result['section_id'] if result['external_system_id'] else 'NO-OCRA-DATA-FOUND'
        row_dict['section_name'] = 'Resources' if result['external_system_id'] else ''
        row_dict['visibility'] = 'RESTRICTED' if result['external_system_id'] else ''
        log.debug( f'updated row_dict, ``{pprint.pformat(row_dict)}``' )
        csv_rows.append( row_dict )
        row_values: list = list( row_dict.values() )
        data_values.append( row_values )
    log.debug( f'csv_rows, ``{pprint.pformat(csv_rows)}``' )
    log.debug( f'data_values, ``{data_values}``' )
    ## finalize leganto data ----------------------------------------
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
    return csv_rows

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