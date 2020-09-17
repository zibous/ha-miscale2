#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

try:
    import matplotlib as mlp
    import matplotlib.pyplot as plt
    import numpy as np

    from testlib import *

except Exception as e:
    print('Import error {}, check requirements.txt'.format(e))
    sys.exit(1)

ymax = 10
xmax = 81
mlist = ("getFatPercentage", "getFatPercentage2", "getFatPercentage3", "getFatPercentage4","LBM")
WEIGHT = 72.50
HEIGHT = 178
SEX = "male"
IMPEDANCE = 500
KF = 0.65

# WEIGHT = 50.50
# HEIGHT = 168
# SEX = "female"
# IMPEDANCE = 485
# KF = 0.95
printdata()

BMI = getBMI(WEIGHT, HEIGHT)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.tick_params(axis="x", labelsize=8)
ax.tick_params(axis="y", labelsize=8)

for m in mlist:
    results = dict()
    for age in range(20, xmax):
        if m == 'getFatPercentage':
            y = getFatPercentage(BMI, age, SEX)
            if y > ymax: ymax = y+5.00
            results[age] = y
            label = "1 - BMI,AGE,SEX"
        if m == 'getFatPercentage3':
            y = getFatPercentage3(WEIGHT, HEIGHT, age, SEX)
            if y > ymax: ymax = y+5.00
            results[age] = y
            label = "3 - Omnicalculator"    
        if m == 'getFatPercentage2':
            y = getFatPercentage2(WEIGHT,HEIGHT,age,SEX)
            if y > ymax: ymax = y+5.00
            results[age] = y
            label = "2 - WEIGHT,HEIGHT,AGE,SEX"        
        if m == 'getFatPercentage4':
            y = getFatPercentage4(KF)
            if y > ymax: ymax = y+5.00
            results[age] = y
            label = "4 - Simple BMI based"
        # if m == 'LBM':
        #    results[age] = getLBMCoefficient(WEIGHT,HEIGHT,IMPEDANCE,AGE)

    plt.plot(*zip(*sorted(results.items())), label=label)
    plt.legend(fontsize=8)

plt.title("Body Fat Calculator: {}, {}kg, {}cm".format(SEX, WEIGHT, HEIGHT),fontsize=12)
plt.xlabel('Age (years)',fontsize=10)
plt.ylabel('Fat (%)',fontsize=10)

plt.xlim(18,xmax)
plt.ylim(-10,ymax)

plt.grid(True,which="both", linestyle='--')

plt.savefig("fatdata-{}.png".format(SEX), dpi=600)
plt.show()
plt.close()
