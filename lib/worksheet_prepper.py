import datetime, logging, os, pprint

import gspread


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
    process_leganto_worksheet( sheet )
    ## process staff worksheet --------------------------------------
    process_staff_worksheet( sheet )
    return
    ## end def update_gsheet()


def process_staff_worksheet( sheet ):
    ## create leganto worksheet -------------------------------------
    title: str = f'staff_{datetime.datetime.now()}'
    staff_worksheet = sheet.add_worksheet( title=title, rows=100, cols=20 )
    ## finalize staff data ----------------------------------------
    headers = [ 'header_a', 'header_b' ]
    data_values = []
    rows = [
        [ 'data_row_1_col_a', 'data_row_1_col_b' ],
        [ 'data_row_2_col_a', 'data_row_2_col_b' ]
    ]
    for row in rows:
        data_values.append( row )
    new_data = [
        { 
            'range': f'A1:B1',
            'values': [ headers ]
        },
        {
            'range': f'A2:B3',
            'values': data_values
        }
    ]
    staff_worksheet.batch_update( new_data, value_input_option='raw' )
    ## update leganto-sheet formatting --------------------------------------------
    staff_worksheet.format( f'A1:B1', {'textFormat': {'bold': True}} )
    staff_worksheet.freeze( rows=1, cols=None )
    ## (no need to sort sheets here)
    return


def process_leganto_worksheet( sheet ):
    ## create leganto worksheet -------------------------------------
    title: str = f'leganto_{datetime.datetime.now()}'
    leganto_worksheet = sheet.add_worksheet( title=title, rows=100, cols=20 )
    ## finalize leganto data ----------------------------------------
    headers = [ 'header_a', 'header_b' ]
    data_values = []
    rows = [
        [ 'data_row_1_col_a', 'data_row_1_col_b' ],
        [ 'data_row_2_col_a', 'data_row_2_col_b' ]
    ]
    for row in rows:
        data_values.append( row )
    new_data = [
        { 
            'range': f'A1:B1',
            'values': [ headers ]
        },
        {
            'range': f'A2:B3',
            'values': data_values
        }
    ]
    leganto_worksheet.batch_update( new_data, value_input_option='raw' )
    ## update leganto-sheet formatting --------------------------------------------
    leganto_worksheet.format( f'A1:B1', {'textFormat': {'bold': True}} )
    leganto_worksheet.freeze( rows=1, cols=None )
    ## make leganto-sheet 2nd...
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


# def update_gsheet( all_results: list, CREDENTIALS: dict, SPREADSHEET_NAME: str ) -> None:
#     """ Writes data to gsheet, then...
#         - sorts the worksheets so the most recent check appears first in the worksheet list.
#         - deletes checks older than the curent and previous checks.
#         Called by check_bibs() """
#     ## access spreadsheet -------------------------------------------
#     log.debug( f'all_results, ``{pprint.pformat(all_results)}``' )
#     credentialed_connection = gspread.service_account_from_dict( CREDENTIALS )
#     sheet = credentialed_connection.open( SPREADSHEET_NAME )
#     log.debug( f'last-updated, ``{sheet.lastUpdateTime}``' )  # not needed now, but will use it later
#     ## create leganto worksheet -------------------------------------
#     title: str = f'leganto_{datetime.datetime.now()}'
#     leganto_worksheet = sheet.add_worksheet( title=title, rows=100, cols=20 )
#     ## finalize leganto data ----------------------------------------
#     headers = [ 'header_a', 'header_b' ]
#     data_values = []
#     rows = [
#         [ 'data_row_1_col_a', 'data_row_1_col_b' ],
#         [ 'data_row_2_col_a', 'data_row_2_col_b' ]
#     ]
#     for row in rows:
#         data_values.append( row )
#     new_data = [
#         { 
#             'range': f'A1:B1',
#             'values': [ headers ]
#         },
#         {
#             'range': f'A2:B3',
#             'values': data_values
#         }
#     ]
#     leganto_worksheet.batch_update( new_data, value_input_option='raw' )
#     ## update leganto-sheet formatting --------------------------------------------
#     leganto_worksheet.format( f'A1:B1', {'textFormat': {'bold': True}} )
#     leganto_worksheet.freeze( rows=1, cols=None )
#     ## make leganto-sheet 2nd...
#     wrkshts: list = sheet.worksheets()
#     log.debug( f'wrkshts, ``{wrkshts}``' )
#     reordered_wrkshts: list = [ wrkshts[0], wrkshts[-1] ]
#     sheet.reorder_worksheets( reordered_wrkshts )
#     wrkshts: list = sheet.worksheets()
#     log.debug( f'wrkshts after sort, ``{wrkshts}``' )
#     num_wrkshts: int = len( wrkshts )
#     log.debug( f'num_wrkshts, ``{num_wrkshts}``' )
#     if num_wrkshts > 3:  # keep requested_checks, and two recent checks
#         wrkshts: list = sheet.worksheets()
#         wrkshts_to_delete = wrkshts[2:]
#         for wrksht in wrkshts_to_delete:
#             sheet.del_worksheet( wrksht )
#     wrkshts: list = sheet.worksheets()
#     log.debug( f'wrkshts after deletion, ``{wrkshts}``' )

#     return

#     ## end def update_gsheet()





# def update_gsheet( all_results: list, CREDENTIALS: dict, SPREADSHEET_NAME: str ) -> None:
#     """ Writes data to gsheet, then...
#         - sorts the worksheets so the most recent check appears first in the worksheet list.
#         - deletes checks older than the curent and previous checks.
#         Called by check_bibs() """
#     ## access spreadsheet -------------------------------------------
#     log.debug( f'all_results, ``{pprint.pformat(all_results)}``' )
#     credentialed_connection = gspread.service_account_from_dict( CREDENTIALS )
#     sheet = credentialed_connection.open( SPREADSHEET_NAME )
#     log.debug( f'last-updated, ``{sheet.lastUpdateTime}``' )  # not needed now, but will use it later
#     ## create new worksheet ----------------------------------------
#     title: str = f'check_results_{datetime.datetime.now()}'
#     worksheet = sheet.add_worksheet(
#         title=title, rows=100, cols=20
#         )
#     ## prepare range ------------------------------------------------
#     headers = [
#         'coursecode',
#         'section_id',
#         'citation_secondary_type',
#         'citation_title',
#         'citation_journal_title',
#         'citation_author',
#         'citation_publication_date',
#         'citation_doi',
#         'citation_isbn',
#         'citation_issn',
#         'citation_volume',
#         'citation_issue',
#         'citation_start_page',
#         'citation_end_page',
#         'citation_source1',
#         'citation_source2',
#         'citation_source3',
#         'citation_source4',
#         'external_system_id'
#         ]
#     end_range_column = 'S'
#     header_end_range = 'S1'
#     num_entries = len( all_results )
#     data_end_range: str = f'{end_range_column}{num_entries + 1}'  # the plus-1 is for the header-row
#     ## prepare data -------------------------------------------------
#     data_values = []
#     for entry in all_results:
#         row = [
#             entry['coursecode'],
#             entry['section_id'],
#             entry['citation_secondary_type'],
#             entry['citation_title'],
#             entry['citation_journal_title'],
#             entry['citation_author'],
#             entry['citation_publication_date'],
#             entry['citation_doi'],
#             entry['citation_isbn'],
#             entry['citation_issn'],
#             entry['citation_volume'],
#             entry['citation_issue'],
#             entry['citation_start_page'],
#             entry['citation_end_page'],
#             entry['citation_source1'],
#             entry['citation_source2'],
#             entry['citation_source3'],
#             entry['citation_source4'],
#             entry['external_system_id']
#             ]
#         data_values.append( row )
#     log.debug( f'data_values, ``{data_values}``' )
#     log.debug( f'data_end_range, ``{data_end_range}``' )
#     new_data = [
#         { 
#             'range': f'A1:{header_end_range}',
#             'values': [ headers ]
#         },
#         {
#             'range': f'A2:{data_end_range}',
#             'values': data_values
#         }

#     ]
#     log.debug( f'new_data, ``{pprint.pformat(new_data)}``' )
#     ## update values ------------------------------------------------
#     # 1/0
#     worksheet.batch_update( new_data, value_input_option='raw' )
#     # worksheet.batch_update( new_data, value_input_option='USER_ENTERED' )
#     ## update formatting --------------------------------------------
#     worksheet.format( f'A1:{end_range_column}1', {'textFormat': {'bold': True}} )
#     worksheet.freeze( rows=1, cols=None )
#     ## re-order worksheets so most recent is 2nd --------------------
#     wrkshts: list = sheet.worksheets()
#     log.debug( f'wrkshts, ``{wrkshts}``' )
#     reordered_wrkshts: list = [ wrkshts[0], wrkshts[-1] ]
#     log.debug( f'reordered_wrkshts, ``{reordered_wrkshts}``' )
#     sheet.reorder_worksheets( reordered_wrkshts )
#     ## delete old checks (keeps current and previous) ---------------
#     num_wrkshts: int = len( wrkshts )
#     log.debug( f'num_wrkshts, ``{num_wrkshts}``' )
#     if num_wrkshts > 3:  # keep requested_checks, and two recent checks
#         wrkshts: list = sheet.worksheets()
#         wrkshts_to_delete = wrkshts[3:]
#         for wrksht in wrkshts_to_delete:
#             sheet.del_worksheet( wrksht )
#     return

#     ## end def update_gsheet()