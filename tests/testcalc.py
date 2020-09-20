#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

try:
    import matplotlib as mlp
    import matplotlib.pyplot as plt
    import numpy as np
    from datetime import datetime

    from conf import *
    from lib import logger
    from lib import calcdata

except Exception as e:
    print('Import error {}, check requirements.txt'.format(e))
    sys.exit(1)

log = logger.Log(__name__, MI2_SHORTNAME, LOG_LEVEL)


def libcheck():
    try:
        from lib_scale2 import mibcs_test
        data = {
            "weight": 70.65,
            "height": 178,
            "age": 14.56,
            "sex": 'male',
            "impedance": 466
        }
        res = mibcs_test.getData(data, 'print')
        print(res)
    except Exception as e:
        print(f"Error {__name__}, {str(e)} line {sys.exc_info()[-1].tb_lineno}")

# simple testcase, simulate the miscale data


def testcase1():
    data_peter = {
        "measured": 70.65,
        "calcweight": 70.65,
        "unit": 'kg',
        "impedance": 485,
        "timestamp": str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')),
        "scantime": str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    }

    data_reni = {
        "measured": 49.50,
        "calcweight": 49.50,
        "unit": 'kg',
        "impedance": 495,
        "timestamp": str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')),
        "scantime": str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    }

    data = data_peter

    log.info('Calcluation based on data:{}'.format(data))
    mCalc = calcdata.CalcData(data, True)
    mi_data = mCalc.getData('data')
    if mCalc.ready:
        mCalc.publishdata()

    else:
        log.error("No data present !")


def testcase2():

    xmax = 600
    ymax = 10

    data = dict()
    data['fat'] = dict()
    data['visceral'] = dict()
    data['muscle'] = dict()
    data['bone'] = dict()
    data['water'] = dict()

    for impedance in range(450, 600):
        miscale_peter = {
            "measured": 70.65,
            "calcweight": 70.65,
            "unit": 'kg',
            "impedance": impedance,
            "timestamp": str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')),
            "scantime": str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        }

        miscale_reni = {
            "measured": 50.65,
            "calcweight": 50.65,
            "unit": 'kg',
            "impedance": impedance,
            "timestamp": str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')),
            "scantime": str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        }
        mCalc = calcdata.CalcData(miscale_peter)
        result = mCalc.getData('full', 'data')

        y = result['fat']
        # if y>ymax: ymax = y+0.10
        data['fat'][impedance] = y

        y = result['visceral']
        # if y>ymax: ymax = y+0.10
        data['visceral'][impedance] = y

        y = result['muscle']
        # if y>ymax: ymax = y+0.10
        data['muscle'][impedance] = y

        y = result['water']
        # if y>ymax: ymax = y+0.10
        data['water'][impedance] = y

        y = result['bone']
        # if y>ymax: ymax = y+0.10
        data['bone'][impedance] = y

    # draw the grid
    fig, ax = plt.subplots(1, figsize=(8, 6))
    plt.suptitle("Testcase Body Calculator Impedance {}".format(result['timestamp']), fontsize=12)
    plt.title("Result for User {} ({}), Years:{}, Weight:{}{}, ".format(result['user'], result['sex'], result['age'], result['measured'], result['unit'], result['timestamp']), fontsize=10)
    # Show the major grid lines with dark grey lines
    ax.minorticks_on()
    ax.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.75)

    # Show the minor grid lines with very faint and almost transparent grey lines
    ax.minorticks_on()
    ax.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.1)

    # primary y:
    ax.plot(*zip(*sorted(data['fat'].items())), label='1-fat', color="red")
    ax.plot(*zip(*sorted(data['visceral'].items())), label='2-visceral', color="orange")
    ax.plot(*zip(*sorted(data['bone'].items())), label='5-bone', color="lime")
    ax.set_ylabel("1-fat, 2-visceral, 5-Bone %")
    ax.set_xlabel("Impedance (Ω)")

    # secondary y:
    ax2 = ax.twinx()
    ax2.plot(*zip(*sorted(data['muscle'].items())), label='3-muscle', color="green")
    ax2.plot(*zip(*sorted(data['water'].items())), label='4-water', color="blue")
    ax2.set_ylabel("3-Muscle, 4-Water %")

    # add legend
    lines_1, labels_1 = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    lines = lines_1 + lines_2
    labels = labels_1 + labels_2
    ax.legend(lines, labels, loc="center left")

    plt.savefig("impedance.png", dpi=600)
    plt.show()


testcase1()

# libcheck()
# testcase2()
