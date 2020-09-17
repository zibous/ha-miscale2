import sys
import json

# import body_metrics as body
from .body_metrics import bodyMetrics

def getData(data: dict = None, printInfo: str="print"):
    try:
        lib = bodyMetrics(data['weight'], data['height'], int(data['age']), data['sex'], data['impedance'])

        if printInfo == 'print':
            print("LBM = {}".format(lib.getLBMCoefficient()))
            print("Body fat = {}".format(lib.getFatPercentage()))
            # print("Body fat scale = {}".format(lib.getFatPercentageScale()))
            print("Water = {}".format(lib.getWaterPercentage()))
            # print("Water scale = {}".format(lib.getWaterPercentageScale()))
            print("Bone mass = {}".format(lib.getBoneMass()))
            # print("Bone mass scale = {}".format(lib.getBoneMassScale()))
            print("Muscle mass = {}".format(lib.getMuscleMass()))
            # print("Muscle mass scale = {}".format(lib.getMuscleMassScale()))
            print("Visceral fat = {}".format(lib.getVisceralFat()))
            # print("Visceral fat scale = {}".format(lib.getVisceralFatScale()))
            print("BMI = {}".format(lib.getBMI()))
            # print("BMI scale = {}".format(lib.getBMIScale()))
            print("BMR = {}".format(lib.getBMR()))
            # print("BMR scale = {}".format(lib.getBMRScale()))
            # print("Ideal weight = {}".format(lib.getIdealWeight()))
            # print("Ideal weight scale = {}".format(lib.getIdealWeightScale()))
            if lib.getFatMassToIdeal()['type'] == 'to_lose':
                print("Fat mass to lose = {}".format(lib.getFatMassToIdeal()['mass']))
            else:
                print("Fat mass to gain = {}".format(lib.getFatMassToIdeal()['mass']))
            print("Protein percentage = {}".format(lib.getProteinPercentage()))
            # print("Protein percentage scale = {}".format(lib.getProteinPercentageScale()))
            # print("Body type = {}".format(lib.getBodyTypeScale()[lib.getBodyType()]))
            return True
        if printInfo == 'data' or printInfo == 'string':
            data['LMC']= lib.getLBMCoefficient()
            data['FAT']= lib.getFatPercentage()
            data['MUSCLE'] = lib.getMuscleMass()
            data['WATER']= lib.getWaterPercentage()
            data['BONES']= lib.getBoneMass()
            data['VISFAT']= lib.getVisceralFat()
            data['BMI']= lib.getBMI()
            data['BMR']= lib.getBMR()
            data['PROTEIN']= lib.getProteinPercentage(False)
            if printInfo == 'data':
                return data
            else:
                return json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)  

    except Exception as e:
        print(f"Error {__name__}, {str(e)} line {sys.exc_info()[-1].tb_lineno}")