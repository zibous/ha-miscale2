
def getVisceralFat(weight: float = 70.5, height: int = 178, age: float = 18.0, sex: str = 'male'):
    if sex == 'female':
        if weight > (13 - (height * 0.5)) * -1:
            subsubcalc = ((height * 1.45) + (height * 0.1158) * height) - 120
            subcalc = weight * 500 / subsubcalc
            vfal = (subcalc - 6) + (age * 0.07)
        elif weight<65:
            subsubcalc = ((height * 1.45) + (height * 0.1158) * height) - weight
            subcalc = weight * 660 / subsubcalc
            vfal = (subcalc - 6) + (age * 0.07)
        else:
            subcalc = 0.691 + (height * -0.0024) + (height * -0.0024)
            vfal = (((height * 0.027) - (subcalc * weight)) * -1) + (age * 0.07) - age
    else:
        if height < weight * 1.6:
            subcalc = ((height * 0.4) - (height * (height * 0.0826))) * -1
            vfal = ((weight * 305) / (subcalc + 48)) - 2.9 + (age * 0.15)
        else:
            subcalc = 0.765 + height * -0.0015
            vfal = (((height * 0.143) - (weight * subcalc)) * -1) + (age * 0.15) - 5.60
    return vfal

print(getVisceralFat())