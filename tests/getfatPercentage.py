
# Get LBM coefficient (with impedance)
def getLBMCoefficient(weight: float = 50.1, height: int = 168, age: float = 62.75, impedance: int = 534):
    lbm = (height * 9.058 / 100) * (height / 100)
    lbm += weight * 0.32 + 12.226
    lbm -= impedance * 0.0068
    lbm -= age * 0.0542
    return lbm

# Get fat percentage
def getFatPercentage(weight: float = 50.1, age: float = 62.75, sex: str = 'female'):
    # Set a constant to remove from LBM
    if sex == 'female' and age <= 49:
        const = 9.25
    elif sex == 'female' and age > 49:
        const = 7.25
        const = 4.95
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
    # return  checkValueOverflow(fatPercentage, 5, 75) # do not use, otherwise calculation error
    return fatPercentage


print(getFatPercentage())
