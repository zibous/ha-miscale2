#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import math
import datetime


# ------------------------------------------------------
# Different Formula’s For Calculating Ideal Body Weight:
# ------------------------------------------------------
# IBW formulas were specifically developed to facilitate drug dosage calculations.
# The given formulas vary in the values used depends on the research of the
# scientists involved in their development and their findings.
# The Devine formula is well-known for finding IBW. Our ideal body weight
# calculator is also using the given formula to calculate ideal body weight for men and women.
# see: https://calculator-online.net/ideal-weight-calculator/

AGE = 14.878
WEIGHT = 72.5
HEIGHT = 178
SEX = 'male'
FAT = 14.80
PAL = 2.5
IMPEDANCE = 435


# -------------------------------
# J. D. Robinson Formula (1983):
# -------------------------------
# For Men:  IBW = 52 + (1.9 x (Ht – 60))
# For Women: IBW = 49 + (1.7 x (Ht – 60))
def IBW_robinson(height: int = HEIGHT, sex: str = SEX) -> float:
    if sex == "female":
        IBW = 49 + (1.7 * (height - 60))
    else:
        IBW = 52 + (1.9 * (height - 60))
    return IBW


# -----------------------------
# D. R. Miller Formula (1983):
# -----------------------------
def IBW_miller(height: int = HEIGHT, sex: str = SEX) -> float:
    if sex == "female":
        IBW = 53.1 + (1.36 * (height - 60))
    else:
        IBW = 56.2 + (1.41 * (height - 60))
    return IBW
