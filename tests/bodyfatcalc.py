#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

# Lukaski: 				(0.756Ht2/R) + (0.110BM) + (0.107Xc) – 5.463
# 1 All formulae give an estimation of FFM.
# Ht = height in cm,
# R = resistance in Ω,
# BM = body mass = weight in kg,
# Xc = reactance in Ω,
# A = age in years,
# S = sex: men = 1 women = 0.


AGE = 14.878
WEIGHT = 72.5
HEIGHT = 178
SEX = 'male'
FAT = 14.80
PAL = 2.5
IMPEDANCE = 435


def __BMI__(weight: float = WEIGHT, height: int = HEIGHT) -> float:
    return (WEIGHT / ((HEIGHT / 100)**2))


# -----------------------------------------------------------
# Calculate your Lean Body Mass using your height and weight
# -----------------------------------------------------------
# https://www.wikihow.fitness/Determine-Lean-Body-Mass
# Men: LBM = (0.3281 * weight) + (0.33929 * height) - 29.5336
# Women: LBM = (0.29569 * weight) + (0.41813 * height) - 43.2933
def __LBM__(weight: float = WEIGHT, height: int = HEIGHT, sex: str = SEX) -> float:
    gender = 1  # male
    if sex == 'female':
        LBM = (0.29569 * weight) + (0.41813 * height) - 43.2933
    else:
        LBM = (0.32810 * weight) + (0.33925 * height) - 29.553

    print('Result:','LBM',LBM, 'FAT:',round(weight-LBM,2)) 
    print('body fat percentage:', round(( (1.0 - (LBM / weight)) * 100),2)) 

    return LBM    


def __LBM1__(weight: float = WEIGHT, height: int = HEIGHT, age: float = AGE, impedance: int = IMPEDANCE) -> float:
    LBM = (height * 9.058 / 100) * (height / 100)
    LBM += weight * 0.32 + 12.226
    LBM -= impedance * 0.0068
    LBM -= age * 0.0542
    print('Result:','LBM',LBM, 'FAT:',round(weight-LBM,2)) 
    print('body fat percentage:', round(( (1.0 - (LBM / weight)) * 100),2)) 
    return LBM

# ----------------------------------------
# Get FFM percentage Van Loan and Mayclin
# ----------------------------------------
# Van Loan and Mayclin:   (0.00085Ht2) + (0.3736BM) – (0.02375R) – 0.1531A) +17.7868


def getFFM_calcL1(weight: float = WEIGHT, height: int = HEIGHT, impedance: int = IMPEDANCE, age: float = AGE):
    FFM = (0.00085 * (height**2)) + (0.3736 * __BMI__(weight, height)) - (0.02375 * impedance) - (0.1531 * age) + 17.7868
    return round(FFM, 2)


# ----------------------------------------
# Get FFM percentage Segal
# ----------------------------------------
# Segal: (0.00132Ht2) + (0.3052BM) – (0.04394R) – 0.1676A) + 22.66827
def getFFM_calcL2(weight: float = WEIGHT, height: int = HEIGHT, impedance: int = IMPEDANCE, age: float = AGE):
    FFM = (0.00132 * (height**2)) + (0.3052 * __BMI__(weight, height)) - (0.04394 * impedance) - (0.1676 * age) + 22.66827
    return round(FFM, 2)


# ----------------------------------------
# Get FFM percentage Kulkarni
# ----------------------------------------
def getFFM_calcL3(weight: float = WEIGHT, height: int = HEIGHT, impedance: int = IMPEDANCE, age: float = AGE):
    FFM = 15.605 - (0.32 * age) + (0.192 * height) + (0.502 * weight)
    return round(FFM, 2)


# ----------------------------------------
# Get FFM percentage Solomon
# ----------------------------------------
def getFFM_calcL4(weight: float = WEIGHT, height: int = HEIGHT, impedance: int = IMPEDANCE, age: float = AGE, sex: str = SEX):
    BMI = __BMI__(weight, height)
    gender = 1  # male
    if sex == 'female':
        gender = 0
    FFM = (22.93 + 0.68 * weight) - (1.14 * BMI - 0.01 * age) + 9.94 * gender
    return round(FFM, 2)


# ----------------------------------------
# Get FFM percentage Lohman
# ----------------------------------------
# Lohman:(0.476Ht2/R) + (0.295BM) + 5.49
def getFFM_calcL5(weight: float = WEIGHT, height: int = HEIGHT, impedance: int = IMPEDANCE, age: float = AGE):
    FFM = (0.476 * (height**2) / impedance) + (0.295 * __BMI__(weight, height)) + 5.49
    return round(FFM, 2)


# ----------------------------------------
# Get FFM percentage Kyle
# ----------------------------------------
# Kyle:(0.476Ht2/R) + (0.295BM) + 5.49
def getFFM_calcL6(weight: float = WEIGHT, height: int = HEIGHT, impedance: int = IMPEDANCE, age: float = AGE):
    FFM = (0.476 * (height**2) / impedance) + (0.295 * __BMI__(weight, height)) + 5.49
    return round(FFM, 2)


# ----------------------------------------
# Get FFM percentage Janmahasatian
# ----------------------------------------
def getFFM_calcL7(weight: float = WEIGHT, height: int = HEIGHT, impedance: int = IMPEDANCE, age: float = AGE, sex: str = SEX):
    BMI = __BMI__(weight, height)
    FFM = (9270 * weight) / (6680 + (216 * BMI))
    return round(FFM, 2)


# ----------------------------------------
# Get fat percentage
# ----------------------------------------
def getFatFFMPercentage(weight: float = WEIGHT, height: int = HEIGHT, age: float = AGE, sex: str = SEX):
    kg = weight - getFFM_calcL1(weight, height, age)
    print(weight, kg)



# ----------------------------------------
# Get fat percentage
# ----------------------------------------
def getFatPercentage(weight: float = WEIGHT, height: int = HEIGHT, age: float = AGE, sex: str = SEX):
    gender = 1  # men
    if sex == 'female':
        gender = 0
    fat = 1.39 * __BMI__(weight, height) + (0.16 * age) - (10.34 * gender) - 9
    return round(fat, 2)


# ----------------------------------------
# Get fat percentage Deurenberg
# ----------------------------------------
def getFat_calc_deurenberg(weight: float = WEIGHT, height: int = HEIGHT, impedance: int = IMPEDANCE, age: float = AGE, sex: str = SEX):
    gender = 1  # male
    if sex == 'female':
        gender = 0
    BMI = __BMI__(weight, height)
    bodyfat = (1.2 * BMI) + (0.23 * age) - (10.8 * gender) - 5.4
    return round(bodyfat, 2)


# ----------------------------------------
# Get fat percentage
# ----------------------------------------
def getFatPercentage2(weight: float = WEIGHT, height: int = HEIGHT, age: float = AGE, sex: str = SEX, impedance: int = IMPEDANCE):
    # Set a constant to remove from LBM
    if sex == 'female' and age <= 49:
        const = 9.25
    elif sex == 'female' and age > 49:
        const = 7.25
    else:
        const = 0.8

    # LBM coefficient
    lbm = (height * 9.058 / 100) * (height / 100)
    lbm += weight * 0.32 + 12.226
    lbm -= impedance * 0.0068
    lbm -= age * 0.0542

    if sex == 'male' and weight < 61:
        coefficient = 0.98
    elif sex == 'female' and weight > 60:
        coefficient = 0.96
        if height > 160:
            coefficient *= 1.03
    elif sex == 'female' and weight < 50:
        coefficient = 1.02
        if height > 160:
            coefficient *= 1.03
    else:
        coefficient = 1.0
    fatPercentage = (1.0 - (((lbm - const) * coefficient) / weight)) * 100

    # Capping body fat percentage
    if fatPercentage > 63:
        fatPercentage = 75
    return round(fatPercentage, 2)


# ----------------------------------------
# https://www.omnicalculator.com/health/body-fat#how-to-calculate-body-fat
# Body Fat Calculator in %
# ----------------------------------------
def getFatPercentage3(weight: float = WEIGHT, height: int = HEIGHT, age: float = AGE, sex: str = SEX):
    gender = 0
    if sex == 'female':
        gender = 1
    BMI = __BMI__(weight, height)
    fatPercentage = -44.988 + (0.503 * age) + (10.689 * gender) + (3.172 * BMI) - \
        (0.026 * BMI * BMI) + (0.181 * BMI * gender) - \
        (0.02 * BMI * age) - (0.005 * BMI * BMI * gender) + \
        (0.00021 * BMI * BMI * age)
    return round(fatPercentage, 2)


# Body Fat Calculator in %
def getFatPercentage4(weight: float = WEIGHT, height: int = HEIGHT, f: float = 1.00):
    BMI = __BMI__(weight, height)
    fatPercentage = round((1.281 * BMI) - 10.13, 2)
    return round(fatPercentage * f, 2)



def printResults():
    print("------- BMI / LBM ---------------------")
    print("BMI", __BMI__())
    print("LBM", __LBM__())
    print("LBM2", __LBM1__())

    print("------- FFM ---------------------")
    print("Van Loan and Mayclin", getFFM_calcL1())
    print("Segal", getFFM_calcL2())
    print("Kulkarni", getFFM_calcL3())
    print("Solomon", getFFM_calcL4())
    print("Lohman", getFFM_calcL5())
    print("Kyle", getFFM_calcL6())
    print("Janmahasatian", getFFM_calcL7())

    print("------- FAT ---------------------")
    print("getFatPercentage", getFatPercentage())
    print("Deurenberg", getFat_calc_deurenberg())
    print("getFatPercentage2", getFatPercentage2())
    print("getFatPercentage3", getFatPercentage3())
    print("getFatPercentage4", getFatPercentage4())

    print('getFatFFMPercentage', getFatFFMPercentage())


printResults()
