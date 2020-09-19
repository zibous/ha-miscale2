# Get LBM coefficient (with impedance)
def getLBMCoefficient(weight: float = 50.1, height: int = 168, age: float = 62.75, impedance: int = 534):
    lbm = (height * 9.058 / 100) * (height / 100)
    lbm += weight * 0.32 + 12.226
    lbm -= impedance * 0.0068
    lbm -= age * 0.0542
    return lbm


# Get bone mass
def getBoneMass(sex:str='female'):
    if  sex == 'female':
        base = .245691014
    else:
        base = 0.18016894

    boneMass = (base - ( getLBMCoefficient() * 0.05158)) * -1
    
    if  sex == 'female':
        boneMass = (base - ( getLBMCoefficient() * 0.07158)) * -1

    if boneMass > 2.2:
        boneMass += 0.1
    else:
        boneMass -= 0.1

    # Capping boneMass
    if  sex == 'female' and boneMass > 5.1:
        boneMass = 8
    elif  sex == 'male' and boneMass > 5.2:
        boneMass = 8
    return  boneMass

print(getBoneMass()) 