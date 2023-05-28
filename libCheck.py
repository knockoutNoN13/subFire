import json
import re
from base64 import *

def check_in(file_path, data):
    with open(file_path, 'r') as f:
        patterns = json.load(f)

    for pattern in patterns['inRules']:
        if pattern['type'] == 'regex':
            regex = re.compile(b64decode(pattern['pattern'].encode()))
            occurrences = pattern['occurences']
            matches = regex.findall(data)
            if len(matches) >= occurrences:
                return True
        elif pattern['type'] == 'string' or pattern['type'] == 'hex':
            strpat = b64decode(pattern['pattern'])
            occurrences = pattern['occurences']
            matches = data.count(strpat)
            if matches >= occurrences:
                return True
    return False

def check_out(file_path, data):
    with open(file_path, 'r') as f:
        patterns = json.load(f)

    for pattern in patterns['outRules']:
        if pattern['type'] == 'regex':
            regex = re.compile(b64decode(pattern['pattern'].encode()))
            occurrences = pattern['occurences']
            matches = regex.findall(data)
            if len(matches) >= occurrences:
                return True
        elif pattern['type'] == 'string' or pattern['type'] == 'hex':
            strpat = b64decode(pattern['pattern'])
            occurrences = pattern['occurences']
            matches = data.count(strpat)
            if matches >= occurrences:
                return True
    return False
