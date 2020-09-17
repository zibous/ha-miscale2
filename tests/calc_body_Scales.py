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


class bodyScales:
    # date:     21.06.2014
    # weight:	72.00
    # bones:    3.60
    # fat:      16.80
    # water:    62.30
    # muscle:   42.30
    # bmi:      23.50
    def __init__(self, weight: float = 72.00, height: int = 175, age: float = 64.20, impedance: int = 460, sex: str = 'male'):
        self.weight = weight
        self.height = height
        self.age = age
        self.sex = sex
        self.isMale = (self.sex == 'male') * 1
        self.impedance = impedance

    # Body mass index (BMI)
    # Is a value derived from the mass (weight) and height of a person.
    # The BMI is defined as the body mass divided by the square of the body height,
    # and is universally expressed in units of kg/m2, resulting from mass in
    # kilograms and height in metres.
    def BMI(self) -> float:
        return round(self.weight / (self.height / 100) ** 2, 2)

    # Corpulence index - Ponderal Index (PI)
    # The Corpulence Index (CI) or Ponderal Index (PI) is a measure of leanness (corpulence)
    # of a person calculated as a relationship between mass and height.
    # It was first proposed in 1921 as the "Corpulence measure" by Swiss physician
    # Fritz Rohrer and hence is also known as Rohrer's Index.
    # It is similar to the body mass index, but the mass is normalized with the
    # third power of body height rather than the second power.

    def getPonderalIndex(self, weight: float = 70.00, height: int = 160):
        poi = weight / ((height / 100) ** 3)
        return round(poi, 2)

    # FFMI
    # Body Mass Index (BMI) is a general estimate of one’s health and it’s a decent estimation
    # for the general population. However, its limitations make it worthless to those who exercise
    # regularly and to those who lift weights. FFMI is a much more effective gauge of ones
    # fitness level for athletes, fitness enthusiasts and individuals who have more muscle
    # mass than the general population. FFMI is a much more effective gauge for ones fitness level,
    # for anyone who takes their fitness seriously.

    def getFatfreemass(self, calcmode: str = 'normalised') -> float:
        BF = self.getBodyFatPercentage()
        if calcmode == 'normalised':
            # FFMI is normalised due to taller athletes usually being bigger overall.
            FFMI = (self.weight * (1 - (BF / 100))) + 6.10 * (1.8 - (self.height / 100))
        else:
            FFMI = (self.weight * (1 - (BF / 100)))
        return round(FFMI, 2)

    def getFatfreemassIndex(self, calcmode: str = 'normalised') -> float:
        return round(self.getFatfreemass(calcmode) / ((self.height / 100)**2), 2)

    # Lean Body Weight (LBW in kg)
    # LBM is a part of body composition that is defined as the difference between total
    # body weight and body fat weight. This means that it counts the mass of all
    # organs except body fat, including bones, muscles, blood, skin, and everything else.
    # While the percentage of LBM is usually not computed, it on average ranges
    # between 60-90% of total body weight.
    # Generally, men have a higher proportion of LBM than women do.
    # The dosages of some anesthetic agents, particularly water-soluble drugs,
    # are routinely based on the LBM. Some medical exams also use the LBM values.
    # For body fitness and routine daily life, people normally care more about
    # body fat percentage than LBM.

    def getLBMCoefficient(self, calcmode: str = 'miscale') -> float:
        LBM = 0.00
        if calcmode == 'miscale':
            LBM = (self.height * 9.058 / 100) * (self.height / 100)
            LBM += self.weight * 0.32 + 12.226
            LBM -= self.impedance * 0.0068
            LBM -= self.age * 0.0542
        if calcmode == 'boer':
            if self.isMale:
                LBM = (0.407 * self.weight) + (0.267 * self.height) - 19.2
            else:
                LBM = (0.252 * self.weight) + (0.473 * self.height) - 48.3
        if calcmode == 'hume':
            if self.isMale:
                LBM = (0.32810 * self.weight) + (0.33929 * self.height) - 29.5336
            else:
                LBM = (0.29569 * self.weight) + (0.41813 * self.height) - 43.2933
        if calcmode == 'james':
            if self.isMale:
                LBM = (1.10 * self.weight) - (128 * ((self.weight / self.height) * (self.weight / self.height)))
            else:
                LBM = (1.07 * self.weight) - (148 * ((self.weight / self.height) * (self.weight / self.height)))
        if calcmode == 'bmi-based':
            fat = self.getBodyFatPercentage('bmi-based3') / 100.00
            LBM = self.weight - (self.weight * fat)

        return round(LBM, 2)

    # Water Percentage = (Total body water (volume) / Body Weight) * 100

    def getWaterPercentage(self, calcmode: str = 'watson') -> float:
        if calcmode == 'miscale':
            waterPercentage = (100 - self.getBodyFatPercentage()) * 0.7
            if (waterPercentage <= 50):
                coefficient = 1.02
            else:
                coefficient = 0.98
            if waterPercentage * coefficient >= 65:
                waterPercentage = 75
            return round(waterPercentage * coefficient, 2)
        else:
            TBW_LITER = self.getBodyWater(calcmode)
            return round((TBW_LITER / self.weight) * 100, 2)

    # Total Body Water (TBW)
    # Body water is defined as the water content in the tissues, blood, bones and elsewhere
    # in the body. All the percentages of body water sum up to total body water (TBW).
    # Ensuring this value remains constant and within healthy limits is part of homeostasis.
    # The most commonly used rough estimate of body water is based on the rule that the
    # average human adult body consists of approximately 60% water, thus we are
    # able to deduct TBW via a person’s weight.
    def getBodyWater(self, calcmode: str = 'watson') -> float:
        # TBW_LITER = Total body water (volume)
        if calcmode == 'watson':
            if self.isMale:
                TBW_LITER = 2.447 - 0.09156 * self.age + 0.1074 * self.height + 0.3362 * self.weight
            else:
                TBW_LITER = -2.097 + 0.1069 * self.height + 0.2466 * self.weight
        if calcmode == 'humeweyer':
            if self.isMale:
                TBW_LITER = (0.194786 * self.height) + (0.296785 * self.weight) - 14.012934
            else:
                TBW_LITER = (0.344547 * self.height) + (0.183809 * self.weight) - 35.270121
        if calcmode == 'lee':
            if self.isMale:
                TBW_LITER = -28.3497 + (0.243057 * self.height) + (0.366248 * self.weight)
            else:
                TBW_LITER = -26.6224 + (0.262513 * self.height) + (0.232948 * self.weight)
        if calcmode == 'chumlea':
            if self.isMale:
                TBW_LITER = 23.04 - (0.03 * self.age) + (0.50 * self.weight) - (0.62 * self.BMI())
            else:
                TBW_LITER = -10.50 - (0.01 * self.age) + (0.20 * self.weight) + (0.18 * self.height)
        if calcmode == 'matias':
            # for athletes: Matias et al. (2015):
            TBW_LITER = 0.286 + (0.195 * self.height * self.height / self.impedance) + (0.385 * self.weight) + (5.086 * self.isMale)
        if calcmode == 'tbw58':
            TBW_LITER = 0.58 * self.weight
        if calcmode == 'default':
            TBW_LITER = (0.372 * self.height * self.height / self.impedance) + (0.142 * self.weight) - (0.069 * self.age) + (3.05 * self.isMale)
        # Water Percentage = (Total body water (volume) / Body Weight) * 100
        return TBW_LITER

    # Body Fat Percentage (BFP)
    # Body Fat Percent is calculated by dividing the total weight of the fat divided by the body weight.
    # Every human needs to have a certain amount of essential fat.
    # The essential fat percent varies hugely between women and men.

    def getBodyFatPercentage(self, calcmode: str = 'default', lbm_mode: str = 'miscale') -> float:
        if calcmode == 'default':
            BFP = (1.20 * self.BMI()) + (0.23 * self.age) - (10.8 * self.isMale) - 5.4

        if calcmode == 'miscale':
            if self.sex == 'female' and self.age <= 49:
                const = 9.25
            elif self.sex == 'female' and self.age > 49:
                const = 7.25
            else:
                const = 0.8
            LBM = self.getLBMCoefficient(lbm_mode)
            if self.sex == 'male' and self.weight < 61:
                coefficient = 0.98
            elif self.sex == 'female' and self.weight > 60:
                coefficient = 0.96
                if self.height > 160:
                    coefficient *= 1.03
            elif self.sex == 'female' and self.weight < 50:
                coefficient = 1.02
                if self.height > 160:
                    coefficient *= 1.03
            else:
                coefficient = 1.0
            BFP = (1.0 - (((LBM - const) * coefficient) / self.weight)) * 100
            # Capping body fat percentage
            if BFP > 63:
                BFP = 75.00

        if calcmode == 'bmi-based1':
            BFP = 1.281 * self.BMI() - 10.13
        if calcmode == 'bmi-based2':
            # https://www.omnicalculator.com/health/body-fat#how-to-calculate-body-fat
            BMI = self.BMI()
            gender = (self.isMale == 0) * 1  # Gender value: male = 0 and female = 1
            BFP = -44.988 + (0.503 * self.age) + (10.689 * gender) + (3.172 * BMI) - (0.026 * (BMI**2)
                                                                                      ) + (0.181 * BMI * gender) - (0.02 * BMI * self.age) - (0.005 * (BMI**2) * gender) + (0.00021 * (BMI**2) * self.age)
        if calcmode == 'bmi-based3':
            BFP = 1.39 * self.BMI() + (0.16 * self.age) - (10.34 * self.isMale) - 9

        return round(BFP, 2)

    # Get bone mass
    def getBoneMass(self):
        if self.sex == 'female':
            base = 0.245691014
        else:
            base = 0.18016894
        boneMass = (base - (self.getLBMCoefficient() * 0.05158)) * -1
        if boneMass > 2.2:
            boneMass += 0.1
        else:
            boneMass -= 0.1
        # Capping boneMass
        if self.sex == 'female' and boneMass > 5.1:
            boneMass = 8
        elif self.sex == 'male' and boneMass > 5.2:
            boneMass = 8
        return round(boneMass,2)


    def print(self):
        print('BMI', self.BMI(), 'kg/m2')
        print('Is Male', self.isMale)
        print(" ")
        print('Total Body Water ----------------------------------------')
        print('WATER Watson     :', self.getWaterPercentage('watson'), '%')
        print('WATER Hume-Weyer :', self.getWaterPercentage('humeweyer'), '%')
        print('WATER Lee        :', self.getWaterPercentage('lee'), '%')
        print('WATER Chumlea    :', self.getWaterPercentage('chumlea'), '%')
        print('WATER Athletes   :', self.getWaterPercentage('matias'), '%')
        print('WATER tbw58      :', self.getWaterPercentage('tbw58'), '%')
        print('WATER Default    :', self.getWaterPercentage('default'), '%')
        print('WATER Miscale    :', self.getWaterPercentage('miscale'), '%')
        print(" ")
        print('Lean body mass (LBM) -------------------------------------')
        print('LBM Miscale      :', self.getLBMCoefficient('miscale'), 'kg')
        print('LBM Boer Formula :', self.getLBMCoefficient('boer'), 'kg')
        print('LBM Hume Formula :', self.getLBMCoefficient('hume'), 'kg')
        print('LBM James Formula:', self.getLBMCoefficient('james'), 'kg')
        print('LBM Simple       :', self.getLBMCoefficient('bmi-based'), 'kg')

        print(" ")
        print('Body Fat Calculation ------------------------------------')
        print('FAT default     :', self.getBodyFatPercentage(), '%')
        print('FAT miscale     :', self.getBodyFatPercentage('miscale'), '%')
        print('FAT BMI 1       :', self.getBodyFatPercentage('bmi-based1'), '%')
        print('FAT BMI 2       :', self.getBodyFatPercentage('bmi-based2'), '%')
        print('FAT BMI 3       :', self.getBodyFatPercentage('bmi-based3'), '%')
        print('Free Fat Mass   :', self.getFatfreemass(), 'kg')
        print('FFMI Index      :', self.getFatfreemassIndex(), '')
        print(" ")
        print('Bone Mass       :',self.getBoneMass() )
        return True


# Testcase
bs = bodyScales()
print(bs.print())
