#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

try:
    from datetime import datetime, timezone
    import pytz
except Exception as e:
    print('Import error {}, check requirements.txt'.format(e))
    sys.exit(1)



DATEFORMAT_MISCAN = '%Y-%m-%d %H:%M:%S'
DATEFORMAT_UTC = '%Y-%m-%dT%H:%M:%SZ'

LAST_TIMESTAMP = str(datetime.today().strftime(DATEFORMAT_UTC)) 

mi_timestamp = "{}-{}-{} {}:{}:{}".format(
                2000 + 20,
                9, 23,
                12, 10,
                5)

# current timestamp from the mi scale
mi_datetime = datetime.strptime(mi_timestamp,DATEFORMAT_MISCAN)
print(mi_datetime)

# convert this to utc time
utc = pytz.utc
mytz = pytz.timezone('Europe/Vaduz')
utc_dt = mytz.localize(mi_datetime)
print (utc_dt.astimezone(utc).strftime(DATEFORMAT_UTC))