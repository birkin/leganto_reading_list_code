""" Stand-alone code to detect data-encoding. 
    Uses chardet.
    - $ pip install chardet
    - <https://chardet.readthedocs.io/en/latest/usage.html> 
    Usage: 
    - $ source ./env_containing_chardet/bin/activate
    - $ python3 ./encoding_detector.py
    """

import os
import chardet  # pip install chardet; 

FILEPATH = os.environ['OIT_COURSE_FILEPATH']

data: bytes = b''
with open( FILEPATH, 'rb' ) as file_handler:
    data = file_handler.read()
assert type( data ) == bytes

encoding = chardet.detect( data )  
assert type( encoding ) == dict
print( f'encoding, ``{encoding}``' )  # yields: {'encoding': 'utf-8', 'confidence': 0.99, 'language': ''}
