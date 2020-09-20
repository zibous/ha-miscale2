#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import math
import datetime

# https://www.calculator.net/ideal-weight-calculator.html

AGE = 18  # 64.878
WEIGHT = 72.5
HEIGHT = 178
SEX = 'male'
FAT = 14.80
PAL = 2.5
IMPEDANCE = 525

# -------------------------------------------------------------------
#  Body Mass Index
# -------------------------------------------------------------------
# Get BMI
# The BMI is universally expressed in kg/m2, resulting from mass in kilograms and height in metres
# see: https://en.wikipedia.org/wiki/Body_mass_index


def getBMI(weight: float = WEIGHT, height: int = HEIGHT):
    bmi = weight / ((height / 100) **2)
    return round(bmi, 2)

# Ponderal Index
# The Ponderal Index (PI) is similar to BMI in that it measures the leanness or corpulence of a
# person based on their height and weight.
# see: https://www.calculator.net/bmi-calculator.html?ctype=metric&cage=65&csex=m&cheightfeet=5&cheightinch=10&cpound=160&cheightmeter=180&ckg=72.5&printit=0&x=41&y=24


def getPonderalIndex(weight: float = WEIGHT, height: int = HEIGHT):
    h = height / 100
    poi = weight / (h**3)
    return round(poi, 2)


# -------------------------------------------------------------------
# Calorie Calculators
# -------------------------------------------------------------------
# This Calorie Calculator is based on several equations, and the results of
# the calculator are based on an estimated average
# Basal Metabolic Rate Calculator or BMR Calculator is a tool to know the minimum amount of energy your body needs to stay alive.
# see:
# https://www.calculator.net/calorie-calculator.html?ctype=metric&cage=65&csex=m&cheightfeet=5&cheightinch=10&cpound=165&cheightmeter=178&ckg=72.5&cactivity=1.465&cmop=0&coutunit=c&cformula=m&cfatpct=20&printit=0&x=53&y=16
# https://calculator-online.net/bmr-calculator/
# BMR (kcal/day)


# ---------------------------------
# Mifflin-St Jeor Equation:
# ---------------------------------
# For men:   BMR = 10W + 6.25H – 5A + 5
# For women:  BMR = 10W + 6.25H – 5A – 161
def getBMR_Mifflin(weight: float = WEIGHT, height: int = HEIGHT, age: float = AGE, sex: str = SEX):
    BMR = 10 * weight + 6.25 * height - 5 * age + 5
    if sex == 'female':
        BMR = 10 * weight + 6.25 * height - 5 * aget - 161
    return round(BMR, 2)

# -------------------------------
# Katch-McArdle Formula:
# -------------------------------
# see https://www.omnicalculator.com/health/bmr-katch-mcardle#what-is-the-katch-mcardle-calculator
# BMR (kcal/day)
# BMR = 370 + 21.6(1 – F)W


def getBMR_KatchMcArdle(weight: float = WEIGHT, fat: float = FAT):
    # BMR = 370 + (21.6 * Lean Body Mass[kg])
    # BMR = 370.00 + 21.60 * (1.00 - fat/100) * weight
    BMR = 370 + (21.6 * getLBMCoefficient())
    return round(BMR, 2)


# ---------------------------------
# Revised Harris-Benedict Equation
# ---------------------------------
# BMR (kcal/day)
# For men:   BMR = 13.397W + 4.799H – 5.677A + 88.362
# For women: BMR = 9.247W + 3.098H – 4.330A + 447.593
def getBMR_HarrisBenedict(weight: float = WEIGHT, height: int = HEIGHT, age: float = AGE, sex: str = SEX):
    BMR = 13.397 * weight + 4.799 * height - 5.677 * age + 88.362
    if sex == 'female':
        BMR = 9.247 * weight + 3.098 * height - 4.330 * age + 447.593
    return round(BMR, 2)


# Maintenance calorie calculator TDEE (kcal/day)
# see: https://www.omnicalculator.com/health/maintenance-calorie
def getDalyEnergyExpenditure(pal: float = 1.4):
    TDEE = getBMR_Mifflin() * pal
    return round(TDEE, 2)

# Macronutrient distribution
# see: https://www.omnicalculator.com/health/maintenance-calorie
# kcal/day


def getMacronutrientDistribution(pal: float = PAL):
    TDEE = getDalyEnergyExpenditure(pal)
    return {
        "protein": round(TDEE * 0.35, 2),
        "carbohydrates": round(TDEE * 0.50, 2),
        "fat": round(TDEE * 0.15, 2)
    }


# -------------------------------------------------------------------
# Body water
# -------------------------------------------------------------------
# see: https://en.wikipedia.org/wiki/Body_water
# C is a coefficient for the expected percentage of weight made up of free water.
# For adult, non-elderly males, C = 0.6. For adult elderly males, malnourished males,
# or females, C = 0.5. For adult elderly or malnourished females C = 0.45.
def getWaterPercentage(weight: float = WEIGHT, sex: str = SEX):
    tbw = weight * 0.45
    return round(tbw, 2)

# https://en.wikipedia.org/wiki/Body_fat_percentage
# 1.39 * BMI + (0.16 * age) - (10.34 * gender) - 9
# From BMI


# -------------------------------------------------------------------
# Body Fat
# -------------------------------------------------------------------
def getFatPercentage(age: float = AGE, sex: str = SEX):
    gender = 1  # men
    BMI = getBMI()
    if sex == 'female':
        gender = 0
    fat = 1.39 * BMI + (0.16 * age) - (10.34 * gender) - 9
    return round(fat, 2)

# Get fat percentage


def getFatPercentage2(weight: float = WEIGHT, height: int = HEIGHT, age: float = AGE, sex: str = SEX):
    # Set a constant to remove from LBM
    if sex == 'female' and age <= 49:
        const = 9.25
    elif sex == 'female' and age > 49:
        const = 7.25
    else:
        const = 0.8

    # Calculate body fat percentage
    LBM = getLBMCoefficient()

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
    fatPercentage = (1.0 - (((LBM - const) * coefficient) / weight)) * 100

    # Capping body fat percentage
    if fatPercentage > 63:
        fatPercentage = 75
    return round(fatPercentage, 2)


# https://www.omnicalculator.com/health/body-fat#how-to-calculate-body-fat
# Body Fat Calculator in %
def getFatPercentage3(weight: float = WEIGHT, height: int = HEIGHT, age: float = AGE, sex: str = SEX):
    gender = 0
    if sex == 'female':
        gender = 1
    BMI = getBMI()
    fatPercentage = -44.988 + (0.503 * age) + (10.689 * gender) + (3.172 * BMI) - \
        (0.026 * BMI * BMI) + (0.181 * BMI * gender) - \
        (0.02 * BMI * age) - (0.005 * BMI * BMI * gender) + \
        (0.00021 * BMI * BMI * age)
    return round(fatPercentage, 2)

# Body Fat Calculator in %


def getFatPercentage4(f: float = 1.00):
    fatPercentage = round((1.281 * getBMI()) - 10.13, 2)
    return round(fatPercentage * f, 2)


# ------------------------------------------------------------
# Lean body mass (LBM), sometimes conflated with fat-free mass,
# is a component of body composition.
#
# Lean body mass is what your body would weight if you didn't have any body fat; 
# that means it counts all the organs, bones, muscles, blood and skin, 
# and everything else which is not fat but has mass
#
# https://www.omnicalculator.com/health/lean-body-mass
# https://en.wikipedia.org/wiki/Lean_body_mass
# ------------------------------------------------------------
# Get LBM coefficient (with impedance)
def getLBMCoefficient(weight: float = WEIGHT, height: int = HEIGHT, impedance: int = IMPEDANCE, age: float = AGE):
    lbm = (height * 9.058 / 100) * (height / 100)
    lbm += weight * 0.32 + 12.226
    lbm -= impedance * 0.0068
    lbm -= age * 0.0542
    return round(lbm, 2)

# https://en.wikipedia.org/wiki/Lean_body_mass
# Boer
# For Men: 0.407 × weight[kg] + 0.267 × height[cm] – 19.2
# For Woman: 0.252 × weight[kg] + 0.473 × height[cm] – 48.3


def getLBMCoefficient2(weight: float = WEIGHT, height: int = HEIGHT, sex: str = SEX):
    if sex == 'female':
        lbm = (0.252 * weight) + (0.473 * height) - 48.3
    else:
        lbm = (0.407 * weight) + (0.267 * height) - 19.2
    return round(lbm, 2)

# https://en.wikipedia.org/wiki/Lean_body_mass
# Hume
# For Men:   0.32810 × weight[kg] + 0.33929 × height[cm] – 29.5336
# For Women: 0.29569 × weight[kg] + 0.41813 × height[cm] – 43.2933


def getLBMCoefficient3(weight: float = WEIGHT, height: int = HEIGHT, sex: str = SEX):
    if sex == 'female':
        # LBM = (0.29569 × W) + (0.41813 × H) − 43.2933
        lbm = (0.29569 * weight) + (0.41813 * height) - 43.2933
    else:
        #  (0.32810 × W) + (0.33929 × H) − 29.5336
        lbm = (0.32810 * weight) + (0.33929 * height) - 29.5336
    return round(lbm, 2)

# https://www.calculator.net/lean-body-mass-calculator.html?ctype=metric&csex=m&cage=n&cheightfeet=5&cheightinch=10&cpound=160&cheightmeter=176&ckg=72.5&x=62&y=16
# The James Formula
# For Men:   1.1 × weight[kg] – 128 × ( weight[kg] / height[cm] ) 2
# For Women: 1.07 × weight[kg] – 148 × ( weight[kg] / height[cm] ) 2


def getLBMCoefficient4(weight: float = WEIGHT, height: int = HEIGHT, sex: str = SEX):
    if sex == 'female':
        # LBMf = 1.07*w - 148* wt2 /h2
        lbm = (1.07 * weight) - (148 * ((weight / height) * (weight / height)))
    else:
        # LBMm = 1.1*w - 128*w2 /h2
        lbm = (1.10 * weight) - (128 * ((weight / height) * (weight / height)))
    return round(lbm, 2)

# Fettmasse (FM), Fat mass
# Fettfreie Masse (FFM), Fat free mass
# 1. FFM and FM


def getFFM(weight: float = WEIGHT, height: int = HEIGHT, age: float = AGE, sex: str = SEX, impedance: int = IMPEDANCE):
    gender = 1.00
    if sex == 'female':
        gender = 0.0
    FFM = -4.104 + ((0.518 * (height**2)) / impedance) + (0.231 * weight) + (0.130 * 0.986) + (4.229 * gender)
    return FFM
# r = 0.986 in: SINGLE PREDICTION EQUATION FOR BIOELECTRICAL IMPEDANCE ANALYSIS IN ADULTS AGED 20-94 YEARS.
#  Kyle UG, Genton L, Karsegard L, Slosman DO, Pichard C. Division of Clinical Nutrition and Dietetics, Geneva University Hospital,
#  Geneva, Switzerland. Nutrition. 2001 Mar;17(3):248-53.

# ------------------------------------------------------------
# Muscle Mass
# ------------------------------------------------------------
# http://www.dev.egofit.de/biadata-org/
# Muscle Mass


def getMuscleMass2(weight: float = WEIGHT, height: int = HEIGHT, age: float = AGE, sex: str = SEX, impedance: int = IMPEDANCE):
    gender = 1.00
    if sex == 'female':
        gender = 0.00
    ASMM = -4.211 + (0.267 * (height**2) / impedance) + (0.095 * weight) + (1.909 * gender) + (-0.012 * age) + (0.058 * impedance)
    return ASMM

# Skeletal muscle mass
# SMM(kg)=[(height2 / resistance x 0,401) + (gender x 3.825) + (age x -0.071)] + 5.102


def getSkeletalMuscleMass(weight: float = WEIGHT, height: int = HEIGHT, age: float = AGE, sex: str = SEX, impedance: int = IMPEDANCE):
    gender = 1.00
    if sex == 'female':
        gender = 0.00
    SMM = (((height**2) / impedance * 0.401) + (gender * 3.825) + (age * 0.071)) + 5.102
    return SMM


def printdata():
    # ----------------------------------------------
    # testcases
    # ----------------------------------------------
    print("getLBMCoefficient app  :", getLBMCoefficient())
    print("getLBMCoefficient Boer :", getLBMCoefficient2())
    print("getLBMCoefficient Hume :", getLBMCoefficient3())
    print("getLBMCoefficient James:", getLBMCoefficient4())
    print("--------------------------------------------")
    print("BMI:", getBMI())
    print("POI:", getPonderalIndex())
    print("getSkeletalMuscleMass:", getSkeletalMuscleMass())
    print("getMuscleMass2:", getMuscleMass2())
    print("--------------------------------------------")
    print("getFatPercentage2:", getFatPercentage2())
    print("getFatPercentage:", getFatPercentage())
    print("getFatPercentage:", getFatPercentage3())
    print("getFFM", getFFM())
    print("--------------------------------------------")
    print("getWaterPercentage:", getWaterPercentage())
    print("--------------------------------------------")
    print("Calorie BMR Mifflin:", getBMR_Mifflin())
    print("Calorie BMR Harris Benedict:", getBMR_HarrisBenedict())
    print("Calorie BMR Katch Mc Ardle:", getBMR_KatchMcArdle())
    print("--------------------------------------------")


printdata()
