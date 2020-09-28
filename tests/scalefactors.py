#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

try:
    import csv
    import json
    from datetime import datetime
    from lib import calcdata
    from conf import *
    from lib import logger

except Exception as e:
    print(f"Import error: {str(e)} line {sys.exc_info()[-1].tb_lineno}, check requirements.txt")
    sys.exit(1)

log = logger.Log("scalefactors", MI2_SHORTNAME, 10)


def round_to_value(number, roundto: float = 0.5):
    return (round(float(number) / roundto) * roundto)


def main():

    variables_file = '../data/peter.csv'
    reader = csv.DictReader(open(variables_file, 'r'), delimiter=',')
    dict_list = []
    for line in reader:
        dict_list.append(line)
    line_count = 0
    cf = {}
    cf1 = {}

    for data in dict_list:

        index = str(round_to_value(data['gewicht']))
        # history data from the csv file
        cf[index] = {
            'impedance': data['impedance'],
            'water': data['wasser'],
            "fat": data['fett'],
            "bone": data['knochen'],
            "muscle": data['muskeln']
        }

        if line_count == 0:
            log.info("Historydata: {}".format(cf))

        # data for the calculation
        scaledata = {
            "measured": float(data['gewicht']),
            "calcweight": float(data['gewicht']) * 2.00,
            "unit": 'kg',
            "impedance": int(data['impedance']),
            "timestamp": data['datum'] + " " + data['zeit'],
            "scantime": data['datum'] + " " + data['zeit']
        }
        # recalc the values

        mCalc = calcdata.CalcData(scaledata, False)
        user = mCalc.getUserData()

        if line_count == 0:
            log.info("Recalibrate for: {}".format(mCalc.user))

        # get the recalibrate factors
        mCalc.athletic = False
        results = mCalc.getData('full', 'data')
        
        cf1[index] = {
            "fat": round(float(cf[index]['fat']) / float(results['fat']), 3),
            "visceral": round((float(cf[index]['fat']) / float(results['fat'])) * 0.82, 3),
            "water": round(float(cf[index]['water']) / float(results['water']), 3),
            "bone": round(float(cf[index]['bone']) / float(results['bone']), 3),
            "muscle": round(float(cf[index]['muscle']) / float(results['muscle']), 3),

        }
        line_count += 1

    log.info("Processed {} lines, Recalibrate data for: {}".format(line_count, mCalc.user))
    print("  ")
    print(json.dumps(cf1, sort_keys=True, indent=4, ensure_ascii=False))

    if cf1:
        with open("../data/rcf_peter.json", "w") as outfile:
            json.dump(cf1, outfile)


if __name__ == "__main__":
    log.info("Start get recalibrate factors ")
    main()
    log.info("End get recalibrate factors ")
