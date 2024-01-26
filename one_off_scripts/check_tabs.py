import sys

def check_tabs_in_file(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if not lines:
                print('The file is empty.')
                return

            # Determine the expected number of tabs from the first line
            expected_tabs = lines[0].count('\t')
            error_found = False

            for line_num, line in enumerate(lines):
                tab_count = line.count('\t')
                if tab_count != expected_tabs:
                    # print(f'Line {line_num + 1} has an unexpected number of tabs: {line.strip()}')
                    print( f'Line {line_num + 1} has an unexpected number of tabs. Expected, ``{expected_tabs}``; found, ``{tab_count}``: \n(START)\n{line.strip()}\n(END)')
                    error_found = True

            if not error_found:
                print(f'No problems, all the lines had {expected_tabs} tabs.')

    except FileNotFoundError:
        print(f'Error: The file {file_path} was not found.')
    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python script.py <file_path>')
    else:
        file_path = sys.argv[1]
        check_tabs_in_file(file_path)
