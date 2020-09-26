#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

try:
    import csv
    from datetime import datetime
    from lib import calcdata
    from conf import *
    from lib import logger

except Exception as e:
    print(f"Import error: {str(e)} line {sys.exc_info()[-1].tb_lineno}, check requirements.txt")
    sys.exit(1)

log = logger.Log("csvtestcase", MI2_SHORTNAME, 10)

def doCalc(scaledata, data) -> dict:

    mCalc = calcdata.CalcData(scaledata, True)
    user = mCalc.getUserData()
    mCalc.impedance = (int(user['height'])**2) / float(data['wasser'])

    # get the data from the calculation
    result = mCalc.getData('full', 'data')
    useAthletic = result['athletic']
    useAthletic = False
    # try to rescale the calculated values
    if useAthletic:

        #result['fat'] = round(result['fat'] - 8.34, 2)
        result['fat'] = round(result['fat'] * 0.6225, 2)
        result['bone'] = round(result['bone'] * 1.302, 2)
        result['water'] = round(result['water'] * 1.033, 2)
        result['muscle'] = round(result['muscle'] * 0.852, 2)
        result['visceral'] = round(result['visceral'] * 0.475, 2)

    # Körperfettanteil + Knochenmasse + Muskelmasse = 100 % der Körperzusammensetzung
    result['check'] = round(float(result['fat']) + float(result['bone']) + float(result['muscle']) + float(result['water']), 2)
    return result

def round_to_value(number,roundto:float=0.5):
    return (round(float(number) / roundto) * roundto)

def calcRecalibrate():
    variables_file = '../data/gewichtsdaten.csv'
    reader = csv.DictReader(open(variables_file, 'r'), delimiter=',')
    dict_list = []
    for line in reader:
        dict_list.append(line)
    line_count = 0
    cf = {}
    cf1 = {}
    for data in dict_list:
        d = str(round_to_value(data['gewicht']))
        cf[d] = {
            'water': data['wasser'],
            "fat": data['fett'],
            "bone": data['knochen'],
            "muscle": data['muskeln']
        }
        # simulate the impedance from the history values
        impedance = int((450 / 54) * float(data['wasser']))
        scaledata = {
            "measured": float(data['gewicht']),
            "calcweight": 70.65,
            "unit": 'kg',
            "impedance": impedance,
            "timestamp": str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')),
            "scantime": str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        }
        results = doCalc(scaledata, data)
        cf1[d] = {
            "fat": round(float(cf[d]['fat']) / float(results['fat']), 3),
            "visceral": round((float(cf[d]['fat']) / float(results['fat'])) * 0.82, 3),
            "water": round(float(cf[d]['water']) / float(results['water']), 3),
            "bone": round(float(cf[d]['bone']) / float(results['bone']), 3),
            "muscle": round(float(cf[d]['muscle']) / float(results['muscle']), 3),

        }
        line_count += 1
    print(f'Processed {line_count} lines.')
    print(cf1)
    return line_count


def testcase1():
    variables_file = '../data/gewichtsdaten.csv'
    reader = csv.DictReader(open(variables_file, 'r'), delimiter=',')
    dict_list = []
    for line in reader:
        dict_list.append(line)

    line_count = 0
    for data in dict_list:
        # simulate the impedance from the history values
        # impedance = int((450 / 54) * float(data['wasser']))
        impedance = int((175**2) / float(data['wasser']))
        scaledata = {
            "measured": float(data['gewicht']),
            "calcweight": 70.65,
            "unit": 'kg',
            "impedance": impedance,
            "timestamp": str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')),
            "scantime": str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        }
        mCalc = calcdata.CalcData(scaledata, True)
        user = mCalc.getUserData()
        mCalc.impedance = int( (user['height']**2) / float(data['wasser']))

        # get the data from the calculation
        results = mCalc.getData('full', 'data')

        print('BMI', results['bmi'], "Weight", results['weight'], 'Fat', results['fat'], 'Bones:', results['bone'], 'Water', results['water'], 'Muscle', results['muscle'], 'Visceral', results['visceral'])
        line_count += 1

    print(f'Processed {line_count} lines.')
    return line_count

def updateInfluxDb():

    log.debug("Start Update Influxdb data")
    
    variables_file = '../data/peter.csv'
    reader = csv.DictReader(open(variables_file, 'r'), delimiter=',')
    dict_list = []
    for line in reader:
        dict_list.append(line)

    line_count = 0
    
    for data in dict_list:

        # recalc the impedance and build the measurement data
        scaledata = {
            "measured": float(data['gewicht']),
            "calcweight": float(data['gewicht']),
            "unit": 'kg',
            "impedance": data['impedance'],
            "timestamp": data['datum'] + " " + data['zeit'],
            "scantime": data['datum'] + " " + data['zeit']
        }

        log.info("Scale data: {}".format(scaledata))  
        # start the calculation modul
        mCalc = calcdata.CalcData(scaledata, True)

        # get the userdata
        user = mCalc.getUserData()
       
        # get the data from the calculation
        # results = mCalc.getData('full', 'data')

        # publish data to the influxDB
        log.info("Update row{}, User{}".format(line_count, user['name']))
        datasections = {"influxdb": True}
        mCalc.publishdata(datasections)

        line_count += 1

    print(f'Processed {line_count} records to influxDB.')
    return line_count


# calcRecalibrate()
# testcase1()
updateInfluxDb()