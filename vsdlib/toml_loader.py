import re
from collections import defaultdict
col_or_row_re = re.compile(r'[cr]\d+$')
def normalize(data):
    col_to_row_data = defaultdict(dict)
    for k1, v1 in data.items():
        if not isinstance(k1, str) or not col_or_row_re.match(k1):
            continue
        if not isinstance(v1, dict):
            continue
        for k2, v2 in data[k1].items():
            if not isinstance(k2, str) or not col_or_row_re.match(k2):
                continue
            if not isinstance(v2, dict):
                continue

            if (k1.startswith('c') and k2.startswith('r')):
                kc = k1
                kr = k2
            else:  # (k1.startswith('r') and k2.startswith('c')):
                kr = k1
                kc = k2
            col_to_row_data[kc][kr] = v2
    return col_to_row_data
