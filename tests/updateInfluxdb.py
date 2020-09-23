#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

try:
    import csv
    from datetime import datetime

    from conf import *
    from lib import logger
    from lib import calcdata

except Exception as e:
    print('Import error {}, check requirements.txt'.format(e))
    sys.exit(1)


log = logger.Log(__name__, MI2_SHORTNAME, LOG_LEVEL)


def main():

    dict_list = []          # list previous data
    line_count = 0          # number of lines

    scaledata = dict()      # data object for the calc module
    height = 175            # height for the user
    try:
        # file with the data from the previous scale
        # datum,zeit,gewicht,knochen,fett,wasser,muskeln,bmi,timestamp
        # 31.12.2013,12:35,77.90,3.70,21.00,59.20,40.60,25.40,1388493300
        # ....
        variables_file = '../data/gewichtsdaten.csv'
        reader = csv.DictReader(open(variables_file, 'r'), delimiter=',')

        # build the dict list
        for line in reader:
            dict_list.append(line)

        for data in dict_list:
            # calculate  the impedance from the history values
            impedance = (int(height)**2) / float(data['wasser'])
            dt_object = datetime.fromtimestamp(int(data['timestamp']))
            scaledata = {
                "measured": float(data['gewicht']),
                "calcweight": float(data['gewicht']),
                "unit": 'kg',
                "impedance": impedance,
                "timestamp": str(dt_object.strftime(DATEFORMAT_UTC)),
                "scantime": str(dt_object.strftime('%Y-%m-%d %H:%M:%S'))
            }

            log.info('Calcluation based on data:{}'.format(scaledata))

            # initialize the calc module with the data from the csv file
            mCalc = calcdata.CalcData(scaledata, True)

            # get the userdata
            mi_userdata = mCalc.getUserData()

            # calculate all miscale data
            log.info('Calcluation for user :{}, Date:{}'.format(mi_userdata['name'], scaledata['timestamp']))

            mi_data = mCalc.getData('alldata')
            if mCalc.ready:
                # publish data to influxdb
                datasections = {
                    "influxdb": True
                }
                mCalc.publishdata(datasections)

            line_count += 1

        log.info('{} previous data found, transfer finished'.format(line_count))

    except BaseException as e:
        log.error(f"Error {__name__}, {str(e)} line {sys.exc_info()[-1].tb_lineno}")


if __name__ == "__main__":
    log.info("Update Influxdb with previous data")
    main()
