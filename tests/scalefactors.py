#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

try:
    import csv
    import json
    import matplotlib as mlp
    import matplotlib.pyplot as plt
    import numpy as np
    from datetime import datetime
    from lib import calcdata
    from conf import *
    from lib import logger

except Exception as e:
    print(f"Import error: {str(e)} line {sys.exc_info()[-1].tb_lineno}, check requirements.txt")
    sys.exit(1)

log = logger.Log("scalefactors", MI2_SHORTNAME, 20)


def round_to_value(number, roundto: float = 0.5):
    return (round(float(number) / roundto) * roundto)


def plotResults(results: list = None, title: str = "Results", output: str = "result.png"):

    try:
        data = dict()
        data['bmi'] = dict()
        data['fat'] = dict()
        data['visceral'] = dict()
        data['muscle'] = dict()
        data['bone'] = dict()
        data['water'] = dict()

        for result in results:
            kg = result['weight']
            y = result['bmi']
            data['bmi'][kg] = y
            y = float(result['fat']) * 0.533333
            data['fat'][kg] = y
            y = result['visceral']
            data['visceral'][kg] = y
            y = result['muscle']
            data['muscle'][kg] = y
            y = result['water']
            data['water'][kg] = y
            y = result['bone']
            data['bone'][kg] = y

        # draw the grid
        fig, ax = plt.subplots(1, figsize=(8, 6))
        plt.suptitle(title, fontsize=12)

        plt.ylim(0, 30)
        plt.xlim(60, 80)

        # Show the major grid lines with dark grey lines
        ax.minorticks_on()
        ax.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.75)

        # Show the minor grid lines with very faint and almost transparent grey lines
        ax.minorticks_on()
        ax.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.1)

        # primary y:
        ax.plot(*zip(*sorted(data['bmi'].items())), label='BMI', color="gray")
        ax.plot(*zip(*sorted(data['fat'].items())), label='1-fat', color="red")
        ax.plot(*zip(*sorted(data['visceral'].items())), label='2-visceral', color="orange")
        ax.plot(*zip(*sorted(data['bone'].items())), label='5-bone', color="lime")
        ax.set_ylabel("1-fat, 2-visceral, 5-Bone %")
        ax.set_xlabel("Weight (kg)")

        # secondary y:
        ax2 = ax.twinx()
        ax2.set_ylim(40, 80)

        ax2.plot(*zip(*sorted(data['muscle'].items())), label='3-muscle', color="green")
        ax2.plot(*zip(*sorted(data['water'].items())), label='4-water', color="blue")
        ax2.set_ylabel("3-Muscle, 4-Water %")

        # add legend
        lines_1, labels_1 = ax.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        lines = lines_1 + lines_2
        labels = labels_1 + labels_2
        ax.legend(lines, labels, loc="center left")

        plt.savefig(output, dpi=600)
        # plt.show()

    except Exception as e:
        print(f"Plot results error: {str(e)} line {sys.exc_info()[-1].tb_lineno}")
        pass


def doCalc(scaledata: dict = None, useAge: bool = False, useAthletic: bool = False):

    mCalc = calcdata.CalcData(scaledata, useAge)
    user = mCalc.getUserData()
    mCalc.athletic = useAthletic

    log.info("User: {}\t Athletic: {} \tAge: {} \tyears Weight: {}kg \tImpedance: {}".format(mCalc.user, mCalc.athletic, round(mCalc.age, 2), mCalc.weight, mCalc.impedance))
    results = mCalc.getData('full', 'data')
    mCalc = None

    return results


def checkdata():
    try:
        file_path = "../data/rcf_peter.json"
        with open(file_path, "r") as f:
            wdata = f.read()
            data = json.loads(wdata)
        d1 = []
        d2 = []
        d3 = []
        if wdata:
            for kg in data:

                scaledata = {
                    "measured": float(kg),
                    "calcweight": float(kg) * 2.00,
                    "unit": 'kg',
                    "impedance": int(data[kg]['impedance'])
                }

                index = int(float(kg) * 10)

                # test mode - standard
                d1.append(doCalc(scaledata, True, False))

                # default mode with recalibrated
                # d2.append(doCalc(scaledata, False, True))

                # test mode
                # d3.append(doCalc(scaledata, True, True))
                print(" ")

        print(" ")
        plotResults(d1, "Calculation standard: Age:True, Athletic mode: False", "d1-result_age_no_athletic_no.png")
        # plotResults(d2,"Calculation recalibrated: Age:False, Athletic mode: True", "d2-result_age_yes_athletic_no.png")
        # plotResults(d3,"Caclulation testcase: Age:True, Athletic mode: True", "d3-result_age_yes_athletic_yes.png")

    except Exception as e:
        print(f"Checkdata error: {str(e)} line {sys.exc_info()[-1].tb_lineno}")
        pass


def plotCompare(results: list = None, title: str = "Xiami vs. VitaDock", output: str = "result.png"):

    try:
        variables_file = '../data/peter.csv'
        reader = csv.DictReader(open(variables_file, 'r'), delimiter=',')
        scaledata = dict()
        d1 = dict()
        d2 = dict()

        plotdata = list()

        useAge = True
        useAthletic = True

        for data in reader:
            d1 = {
                "weight": float(data['gewicht']),
                "impedance": int(data['impedance']),
                "bone": float(data['knochen']),
                "fat": float(data['fett']),
                "water": float(data['wasser']),
                "muscle": float(data['muskeln']),
                "bmi": float(data['bmi'])
            }

            scaledata = {
                "measured": float(data['gewicht']),
                "calcweight": float(data['gewicht']) * 2.00,
                "unit": 'kg',
                "impedance": int(data['impedance']),
                "timestamp": data['datum'] + " " + data['zeit'],
                "scantime": data['datum'] + " " + data['zeit']
            }

            results = doCalc(scaledata, useAge, useAthletic)

            d2 = {
                "index": float(d1['weight']),
                "weight": float(d1['weight']) - float(results['weight']),
                "impedance": int(d1['impedance']) - int(results['impedance']),
                "bone": float(d1['bone']) - float(results['bone']),
                "fat": float(d1['fat']) - float(results['fat']),
                "water": float(d1['water']) - float(results['water']),
                "muscle": float(d1['muscle']) - float(results['muscle']),
                "bmi": float(d1['bmi']) - float(results['bmi'])
            }

            plotdata.append(d2)

        data = dict()
        data['bmi'] = dict()
        data['fat'] = dict()        
        data['muscle'] = dict()
        data['bone'] = dict()
        data['water'] = dict()

        for result in plotdata:
            kg = result['index']
            data['bmi'][kg] = float(result['bmi'])   
            data['bone'][kg] = float(result['bone'])        
            data['fat'][kg] = float(result['fat'])
            data['muscle'][kg] = float(result['muscle'])
            data['water'][kg] =float(result['water'])

        # draw the grid
        fig, ax = plt.subplots(1, figsize=(8, 6))
        plt.suptitle(title, fontsize=12)
        plt.title("Calc mode Age:{} Athletic {})".format(useAge,useAthletic), fontsize=10)

        # Show the major grid lines with dark grey lines
        ax.minorticks_on()
        ax.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.75)

        # Show the minor grid lines with very faint and almost transparent grey lines
        ax.minorticks_on()
        ax.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.1)

        # primary y:
        ax.plot(*zip(*sorted(data['bmi'].items())), label='BMI', color="gray")              ## result o.k
        ax.plot(*zip(*sorted(data['bone'].items())), label='5-bone', color="lime")          ## result o.k

        ax.plot(*zip(*sorted(data['fat'].items())), label='fat', color="red")
        ax.plot(*zip(*sorted(data['muscle'].items())), label='muscle', color="green")
        ax.plot(*zip(*sorted(data['water'].items())), label='water', color="blue")

        # add legend
        lines_1, labels_1 = ax.get_legend_handles_labels()
        #ax.legend(lines_1, labels_1, loc="center left")
        ax.legend(lines_1, labels_1)

        plt.savefig(output, dpi=600)

    except Exception as e:
        print(f"Checkdata error: {str(e)} line {sys.exc_info()[-1].tb_lineno}")
        pass


def main():
    try:
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
            #  doCalc(scaledata: dict = None, useAge: bool = False, useAthletic: bool = False):
            results = doCalc(scaledata, False, False)

            cf1[index] = {
                "fat": round(float(cf[index]['fat']) / float(results['fat']), 3),
                "visceral": round((float(cf[index]['fat']) / float(results['fat'])) * 0.82, 3),
                "water": round(float(cf[index]['water']) / float(results['water']), 3),
                "bone": round(float(cf[index]['bone']) / float(results['bone']), 3),
                "muscle": round(float(cf[index]['muscle']) / float(results['muscle']), 3),
                "impedance": scaledata["impedance"]

            }
            line_count += 1

        log.info("Processed {} lines, Recalibrate data for: {}".format(line_count, results['user']))
        print("  ")
        print(json.dumps(cf1, sort_keys=True, indent=4, ensure_ascii=False))

        if cf1:
            with open("../data/rcf_peter.json", "w") as outfile:
                json.dump(cf1, outfile)

    except Exception as e:
        print(f"Checkdata error: {str(e)} line {sys.exc_info()[-1].tb_lineno}")
        pass


if __name__ == "__main__":
    log.info("Start get recalibrate factors ")
    # main()
    # checkdata()
    plotCompare()
    log.info("End get recalibrate factors ")
