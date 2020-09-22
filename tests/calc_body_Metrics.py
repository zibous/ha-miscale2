#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

try:
    # from calc_body_Scales import bodyScales
    from math import floor
except Exception as e:
    print('Import error {}, check requirements.txt'.format(e))
    sys.exit(1)


class bodyMetrics:
    # date:     21.06.2014
    # weight:	72.00
    # bones:    3.60
    # fat:      16.80
    # water:    62.30
    # muscle:   42.30
    # bmi:      23.50
    def __init__(self, weight: float = 72.00, height: int = 175, age: float = 64.20, sex: str = 'male'):
        self.weight = weight
        self.height = height
        self.age = age
        self.sex = sex
        self.isMale = (self.sex == 'male') * 1

    # Maximum Muscular Potential Calculator
    # Calculate Your Genetic Drug Free Muscle Gaining Potential
    def maxMuscular(self, calcmode: str = 'martins') -> float:
        if calcmode == 'martins':
            # Martin's formula: Height in centimeters - (98 - 102) = Body weight in kilos.
            MMP = self.height - 102
        return MMP

    # Maintenance Caloric Range: 2,218 - 2,534
    # Deficit Caloric Range: 1,774 - 2,028
    def getMaintenanceCaloricRange(self) -> int:
        return {
            'caloricmin': int(self.weight * 30.80),
            'caloricmax': int(self.weight * 35.20),
            'deficitmin': int(self.weight * 24.60),
            'Ddeficitmax': int(self.weight * 28.20)
        }

    def print(self):
        print('Max Muscular   :', self.maxMuscular(), 'kg')
        print('Caloric Ranges :', self.getMaintenanceCaloricRange(), 'Cal')


# testcase
bm = bodyMetrics()
bm.print()
