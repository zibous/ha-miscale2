#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

try:
    import os
    import os.path
    from datetime import datetime, date, timedelta
    import paho.mqtt.publish as publish
    import time
    import json
    import csv
    from conf import *
    from lib import logger
    from lib import body_metrics
    from lib import body_score
    from lib import mqtt
    from lib import influxdata

except Exception as e:
    print('Import error {}, check requirements.txt'.format(e))
    sys.exit(1)

log = logger.Log(__name__, MI2_SHORTNAME, LOG_LEVEL)


class CalcData():

    version = '1.0.1'

    def __init__(self, data: dict = None, useAgeCalc: bool = True):
        self.useAgeCalc = useAgeCalc
        # current user settings
        self.user = 'default'
        self.dob = None
        self.height = 175
        self.age = 18
        self.sex = 'male'
        self.athletic = False
        self.userscores = None
        self.adjustments = None
        self.userid = "none"
        self.ready = False
        self.unit = 'kg'
        self.timestamp = datetime.utcnow().strftime(DATEFORMAT_UTC)
        # all from miscale
        self.data = data
        self.simpledata = {}
        self.bodyscores = {}
        if self.data and "measured" in self.data and "impedance" in self.data:
            self.weight = float(self.data["measured"])
            self.data['weight'] = self.weight
            self.impedance = int(self.data["impedance"])
            if "unit" in self.data:
                self.unit = self.data["unit"]
            if "timestamp" in self.data:
                self.timestamp = self.data["timestamp"]
            else:
                self.data["timestamp"] = self.timestamp
            self.__setUserData__()
            # check valid data
            self.ready = self.__checkdata__()

    def setData(self, name, value):
        self.data[name] = value

    def doCalc(self, mode: str = 'simple'):
        try:
            if self.ready:
                if mode == 'simple':
                    self.__setSimpledata__()
                elif mode == 'userdata':
                    self.getUserData()
                else:
                    self.__setBodyMetricsdata__()
                return True
            else:
                return False
        except BaseException as e:
            log.error(f"Error {__name__}, {str(e)} line {sys.exc_info()[-1].tb_lineno}")
            pass

    def getData(self, mode: str = 'simple', dataformat: str = 'debug'):
        try:
            if self.ready:
                if mode == 'simple':
                    self.__setSimpledata__()
                else:
                    self.__setBodyMetricsdata__()
                if dataformat == 'data':
                    return self.data
                if dataformat == "string":
                    return json.dumps(self.data)
                return json.dumps(self.data, sort_keys=True, indent=4, ensure_ascii=False)
            else:
                return None
        except BaseException as e:
            log.error(f"Error {__name__}, {str(e)} line {sys.exc_info()[-1].tb_lineno}")
            pass

    def getUserData(self) -> dict:
        try:
            if self.ready:
                return {
                    "userid": self.userid,
                    "name": self.user,
                    "dob": self.dob,
                    "height": self.height,
                    "age": self.age,
                    "sex": self.sex,
                    "male": (self.sex == 'male') * 1,
                    "athletic": self.athletic,
                    "targetweight": self.userscores['WEIGHT'],
                    "adjustments": self.adjustments,
                    "scaledata": {
                        "weight": self.weight,
                        "unit": self.unit,
                        "impedance": self.impedance,
                        "timestamp": self.timestamp,
                    },
                    "ready": self.ready,
                    "appversion": self.version
                }
        except BaseException as e:
            log.error(f"Error {__name__}, {str(e)} line {sys.exc_info()[-1].tb_lineno}")
            return None

    def round_to_value(self, number, roundto: float = 0.5) -> str:
        return str(round(float(number) / roundto) * roundto)

    def __recalibrate__(self):
        try:
            if self.adjustments and self.athletic:
                # idx = str(self.round_to_value(self.weight))
                idx = str(round(self.weight, 1))
                if idx in self.adjustments:
                    log.debug(' *** Calibration data found for {}, weight: {}{}'.format(self.user, self.weight, self.unit))
                    cf = self.adjustments[idx]
                    if 'fat' in cf:
                        self.data['fat'] = round(float(self.data['fat']) * float(cf['fat']), 2)
                        # self.data['visceral'] = round(float(self.data['visceral']) * float(cf['visceral']), 2)
                    if 'water' in cf:
                        self.data['water'] = round(float(self.data['water']) * float(cf['water']), 2)
                    if 'bone' in cf:
                        self.data['bone'] = round(float(self.data['bone']) * float(cf['bone']), 2)
                    if 'muscle' in cf:
                        self.data['muscle'] = round(float(self.data['muscle']) * float(cf['muscle']), 2)
                else:
                    log.debug('No calibration data found for {}, weight: {}{}'.format(self.user, self.weight, self.unit))
        except BaseException as e:
            log.error(f"Error {__name__}, {str(e)} line {sys.exc_info()[-1].tb_lineno}")
            pass

    def __getAge__(self) -> float:
        try:
            if self.dob:
                d1 = datetime.strptime(self.dob, DATEFORMAT_YMD)
                d2 = datetime.strptime(datetime.today().strftime(DATEFORMAT_YMD), DATEFORMAT_YMD)
                return abs((d2 - d1).days) / 365
            else:
                return 20.00
        except BaseException as e:
            log.error(f"Error {__name__}, {str(e)} line {sys.exc_info()[-1].tb_lineno}")
            pass

    def __getDOB__(self):
        # simulate the DOB for 18 Years old
        current_date = date.today().isoformat()
        return (date.today() - timedelta(days=365 * 18)).isoformat()

    # Maximum Muscular Potential Calculator
    # Calculate Your Genetic Drug Free Muscle Gaining Potential
    def maxMuscular(self, calcmode: str = 'martins') -> float:
        if calcmode == 'martins':
            # Martin's formula: Height in centimeters - (98 - 102) = Body weight in kilos.
            MMP = self.height - 102
        return MMP

    def getMuscleMass2(self):
        gender = 1.00
        if self.sex == 'female':
            gender = 0.00
        ASMM = -4.211 + (0.267 * (self.height**2) / self.impedance) + (0.095 * self.weight) + (1.909 * gender) + (-0.012 * self.age) + (0.058 * self.impedance)
        return ASMM

    # Maintenance Caloric Range: 2,218 - 2,534
    # Deficit Caloric Range: 1,774 - 2,028
    def getMaintenanceCaloricRange(self) -> int:
        return {
            'caloricmin': int(self.weight * 30.80),
            'caloricmax': int(self.weight * 35.20),
            'deficitmin': int(self.weight * 24.60),
            'deficitmax': int(self.weight * 28.20)
        }

    # Maintenance calorie calculator TDEE (kcal/day)
    # see: https://www.omnicalculator.com/health/maintenance-calorie

    def getDalyEnergyExpenditure(self):
        if USER1_ACTIVITY and self.data['bmr']:
            self.data['tdee'] = int(round(self.data['bmr'] * USER1_ACTIVITY, 0))
            return self.data['tdee']
        else:
            return 0

    # Macronutrient distribution
    # see: https://www.omnicalculator.com/health/maintenance-calorie
    # kcal/day

    def getMacronutrientDistribution(self):
        if "tdee" in self.data:
            return {
                "protein": round(self.data['tdee'] * 0.35, 0),
                "carbohydrates": round(self.data['tdee'] * 0.50, 0),
                "fat": round(self.data['tdee'] * 0.15, 0)
            }
        else:
            return None

    # Skeletal muscle mass
    # SMM(kg)=[(height2 / resistance x 0,401) + (gender x 3.825) + (age x -0.071)] + 5.102

    def getSkeletalMuscleMass(self):
        gender = 1.00
        if self.sex == 'female':
            gender = 0.00
        SMM = (((self.height**2) / self.impedance * 0.401) + (gender * 3.825) + (self.age * 0.071)) + 5.102
        return SMM

    # Corpulence index - Ponderal Index (PI)
    # The Corpulence Index (CI) or Ponderal Index (PI) is a measure of leanness (corpulence)
    # of a person calculated as a relationship between mass and height.
    # It was first proposed in 1921 as the "Corpulence measure" by Swiss physician
    # Fritz Rohrer and hence is also known as Rohrer's Index.
    # It is similar to the body mass index, but the mass is normalized with the
    # third power of body height rather than the second power.

    def getPonderalIndex(self):
        poi = self.weight / ((self.height / 100) ** 3)
        return round(poi, 2)

    # FFMI
    # Body Mass Index (BMI) is a general estimate of one’s health and it’s a decent estimation
    # for the general population. However, its limitations make it worthless to those who exercise
    # regularly and to those who lift weights. FFMI is a much more effective gauge of ones
    # fitness level for athletes, fitness enthusiasts and individuals who have more muscle
    # mass than the general population. FFMI is a much more effective gauge for ones fitness level,
    # for anyone who takes their fitness seriously.

    def getFatfreemass(self, calcmode: str = 'normalised') -> float:
        BF = float(self.data['fat'])
        if calcmode == 'normalised':
            # FFMI is normalised due to taller athletes usually being bigger overall.
            FFMI = (self.weight * (1 - (BF / 100))) + 6.10 * (1.8 - (self.height / 100))
        else:
            FFMI = (self.weight * (1 - (BF / 100)))
        return round(FFMI, 2)

    def getFatfreemassIndex(self, calcmode: str = 'normalised') -> float:
        return round(self.getFatfreemass(calcmode) / ((self.height / 100)**2), 2)

    def __setUserData__(self):
        if self.data:
            self.user = self.user
            if int(self.weight) > USER1_GT:
                self.user = USER1_NAME
                self.height = USER1_HEIGHT
                self.dob = USER1_DOB
                if self.useAgeCalc:
                    self.age = self.__getAge__()
                self.sex = USER1_SEX
                self.athletic = USER1_ATHLETIC
                if USER1_ADJUSTMENTS and USER1_ATHLETIC:
                    self.adjustments = USER1_ADJUSTMENTS
                if USER1_SCORES:
                    self.userscores = USER1_SCORES
                self.userid = "USER1"

            elif int(self.weight) < USER2_LT:
                self.user = USER2_NAME
                self.height = USER2_HEIGHT
                self.dob = USER2_DOB
                if self.useAgeCalc:
                    self.age = self.__getAge__()
                self.sex = USER2_SEX
                self.athletic = USER2_ATHLETIC
                if USER2_ADJUSTMENTS and USER2_ATHLETIC:
                    self.adjustments = USER2_ADJUSTMENTS
                if USER2_SCORES:
                    self.userscores = USER2_SCORES
                self.userid = "USER2"

            else:
                self.user = USER3_NAME
                self.height = USER3_HEIGHT
                self.dob = USER3_DOB
                if self.useAgeCalc:
                    self.age = self.__getAge__()
                self.sex = USER3_SEX
                self.athletic = USER3_ATHLETIC
                if USER3_ADJUSTMENTS and USER3_ATHLETIC:
                    self.adjustments = USER3_ADJUSTMENTS
                if USER3_SCORES:
                    self.userscores = USER3_SCORES
                self.userid = "USER3"

            log.debug("User data loaded  for {}".format(self.user))

    def __divval__(self, v1: float = 0.00, v2: float = 0.00) -> str:
        idx = 1
        if v1 < v2:
            idx = 0
        if v1 == v2:
            idx = 1
        if v1 > v2:
            idx = 2
        return DIFF_TEXT_DE[idx]

    def __calcdatadiff__(self) -> dict:
        if self.data and self.ready:
            file_path = "{}miscale-{}.json".format(DATA_DIR, self.user)
            try:
                if os.path.isfile(file_path):
                    with open(file_path, "r") as f:
                        _prevdat = f.read()
                        log.debug("Previous data loaded {}, start calculation for {}".format(file_path, self.user))
                        # compare to the current...
                        data_prev = json.loads(_prevdat)
                        if data_prev:
                            result = dict()
                            result['user'] = self.user
                            # values to the previous data
                            result['weight'] = round(self.data['weight'] - data_prev['weight'], 2)
                            result['fat'] = round(self.data['fat'] - data_prev['fat'], 2)
                            result['water'] = round(self.data['water'] - data_prev['water'], 2)
                            result['muscle'] = round(self.data['muscle'] - data_prev['muscle'], 2)
                            result['visceral'] = round(self.data['visceral'] - data_prev['visceral'], 2)
                            result['protein'] = round(self.data['protein'] - data_prev['protein'], 2)
                            if DIFF_TEXT_DE:
                                # 0:lower, 1: equal, 2: greater
                                result['wstate'] = self.__divval__(self.data['weight'], data_prev['weight'])
                                result['fstate'] = self.__divval__(self.data['fat'], data_prev['fat'])
                                result['mstate'] = self.__divval__(self.data['muscle'], data_prev['muscle'])
                                result['vstate'] = self.__divval__(self.data['visceral'], data_prev['visceral'])
                                result['pstate'] = self.__divval__(self.data['protein'], data_prev['protein'])
                            return result
            except BaseException as e:
                log.error(f"Error Read previous file {file_path}, {str(e)} line {sys.exc_info()[-1].tb_lineno}")
                pass

        return None

    def __savedata__(self):
        if self.data and self.ready:
            # first save the current data
            file_path = "{}miscale-{}.json".format(DATA_DIR, self.user)
            with open(file_path, 'w') as f:
                f.write(json.dumps(self.data, ensure_ascii=False))
                log.debug("Data to file {}".format(file_path))

            # write the historydata
            file_path = "{}{}-{}.csv".format(DATA_DIR, str(datetime.today().strftime(DATEFORMAT_YM)), self.user)
            log.debug("Save Data to file {}".format(file_path))
            if os.path.isfile(file_path):
                addHeader = False
            else:
                addHeader = True
            try:
                with open(file_path, 'a') as f:
                    if addHeader:
                        datastring = ",".join(map(str, list(self.data.keys())))
                        f.write(datastring + '\n')
                    datastring = ",".join(map(str, list(self.data.values())))
                    f.write(datastring + '\n')
                    log.debug("Reportdata saved to file {}".format(file_path))
            except Exception as e:
                log.error(f"Error {__name__}: {str(e)},  line {sys.exc_info()[-1].tb_lineno}")
                pass

    def __checkdata__(self):
        fields = [
            "weight",
            "unit",
            "impedance",
            "timestamp"
        ]
        valid = True
        for field in fields:
            if(not field in self.data):
                valid = False
                log.error("Error {}: Datafield {} is missing".format(__name__, field))
                break

        return valid

    def __setSimpledata__(self):
        try:
            if self.ready:
                self.simpledata['user'] = self.user
                self.simpledata['sex'] = self.sex
                self.simpledata['athletic'] = self.athletic
                self.simpledata['age'] = round(self.age, 2)
                self.simpledata['weight'] = round(self.weight, 2)
                self.simpledata['unit'] = self.unit
                self.simpledata['impedance'] = self.impedance
                # simple caclulation for the water, fat.....
                self.simpledata['bmi'] = round((self.weight / (self.height ** 2)) * 10000, 2)
                self.simpledata['water'] = round(0.72 * (-1.976 + 0.907 * self.weight), 2)
                self.simpledata['fat'] = round((1.281 * self.simpledata['bmi']) - 10.13, 2)
                self.simpledata['timestamp'] = self.timestamp
                self.simpledata['version'] = self.version
                self.simpledata["icon"] = "mdi:scale-bathroom"
                self.simpledata['attribution'] = ATTRIBUTION
        except Exception as e:
            log.error(f"Error {__name__}: {str(e)},  line {sys.exc_info()[-1].tb_lineno}")
            pass

    def __setBodyMetricsdata__(self) -> dict():
        try:

            if self.data and 'bmr' in self.data:
                # allready calculated
                return True

            if self.ready:
                log.debug("Set Body Metrics data for {}, Weight:{}".format(self.user, self.weight))
                # Körperfettanteil + Knochenmasse + Muskelmasse = 100 % der Körperzusammensetzung
                lib = body_metrics.bodyMetrics(self.weight, self.height, self.age, self.impedance, self.sex)

                # user data
                self.data['user'] = self.user
                self.data['sex'] = self.sex
                self.data['athletic'] = self.athletic
                self.data['age'] = round(self.age, 2)
                self.data['metabolic_age'] = round(lib.getMetabolicAge(), 2)
                self.data['impedance'] = self.impedance
                self.data['bmi'] = round(lib.getBMI(), 2)
                self.data['poi'] = self.getPonderalIndex()
                self.data['bodytype'] = BODY_SCALE_TYPES[lib.getBodyType()]

                # weight
                self.data['weight'] = round(self.weight, 2)
                self.data['idealweight'] = round(lib.getIdealWeight(), 2)
                self.data['targetweight'] = self.userscores['WEIGHT']
                self.data['unit'] = self.unit

                # fat
                self.data['lbm'] = round(lib.getLBMCoefficient(), 2)
                self.data['fat'] = round(lib.getFatPercentage(), 2)
                self.data['fattype'] = lib.getFatMassToIdeal()['type']
                # not a valid data from getFatMassToIdeal, use usersettings instead
                if self.userscores and self.userscores['FAT']:
                    self.data['idealfat'] = self.userscores['FAT']
                else:
                    self.data['idealfat'] = round(lib.getFatMassToIdeal()['mass'], 2)
                self.data['visceral'] = round(lib.getVisceralFat(), 2)

                # water, bone, muscle, protein
                self.data['water'] = round(lib.getWaterPercentage(), 2)
                self.data['bone'] = round(lib.getBoneMass(), 2)
                self.data['muscle'] = round(lib.getMuscleMass(), 2)

                self.data['ffm'] = self.getFatfreemass()
                self.data['ffmi'] = self.getFatfreemassIndex()
                self.data['protein'] = round(lib.getProteinPercentage(), 2)
                self.data['bmr'] = round(lib.getBMR(), 0)
                self.data['timestamp'] = self.timestamp
                self.data['version'] = self.version

                self.__recalibrate__()

                if self.userscores:
                    self.setBodyScores()

                return True

        except Exception as e:
            log.error(f"Error {__name__}: {str(e)},  line {sys.exc_info()[-1].tb_lineno}")
            pass

    def setBodyScores(self):
        try:
            if self.userscores and self.ready:
                score = body_score.bodyScore(self.age,
                                             self.sex,
                                             self.height,
                                             self.weight,
                                             self.data['bmi'],
                                             float(self.userscores['FAT']),
                                             float(self.userscores['MUSCLE']),
                                             float(self.userscores['WATER']),
                                             float(self.userscores['VISCERAL']),
                                             float(self.userscores['BONES']),
                                             int(self.userscores['BMR']),
                                             float(self.userscores['PROTEIN']))

                self.bodyscores = {}
                self.bodyscores['user'] = self.user
                self.bodyscores['score'] = score.getBodyScore()
                result = self.__calcdatadiff__()
                if result:
                    self.bodyscores['deltas'] = {}
                    self.bodyscores['deltas']['weight'] = result['weight']
                    self.bodyscores['deltas']['fat'] = result['fat']
                    self.bodyscores['deltas']['water'] = result['water']
                    self.bodyscores['deltas']['muscle'] = result['muscle']
                    self.bodyscores['deltas']['visceral'] = result['visceral']
                    self.bodyscores['deltas']['protein'] = result['protein']
                    if DIFF_TEXT_DE:
                        self.bodyscores['states'] = {}
                        self.bodyscores['states']['weight'] = result['wstate']
                        self.bodyscores['states']['fat'] = result['fstate']
                        self.bodyscores['states']['water'] = result['mstate']
                        self.bodyscores['states']['muscle'] = result['vstate']
                        self.bodyscores['states']['protein'] = result['pstate']
                self.bodyscores['scores'] = {}
                self.bodyscores['scores']['bmi'] = score.getBmiDeductScore()
                self.bodyscores['scores']['fat'] = score.getBodyFatDeductScore()
                self.bodyscores['scores']['visceral'] = score.getVisceralFatDeductScore()
                self.bodyscores['scores']['muscle'] = score.getMuscleDeductScore()
                self.bodyscores['scores']['water'] = score.getWaterDeductScore()
                self.bodyscores['scores']['bones'] = score.getBoneDeductScore()
                self.bodyscores['scores']['bmr'] = score.getBasalMetabolismDeductScore()
                self.bodyscores['scores']['protein'] = score.getProteinDeductScore()
                self.bodyscores['caloric'] = self.getMaintenanceCaloricRange()
                self.bodyscores['engergieexp'] = self.getDalyEnergyExpenditure()
                self.bodyscores['macronut'] = self.getMacronutrientDistribution()

                self.bodyscores['version'] = self.version
                self.bodyscores['timestamp'] = self.timestamp

                log.debug("Bodyscores found for {}: {}".format(self.user, self.bodyscores))

        except Exception as e:
            log.error(f"Error {__name__}: {str(e)},  line {sys.exc_info()[-1].tb_lineno}")
            pass

    def bodyScores2Influxdb(self):
        if not self.ready:
            return False
        if self.bodyscores and INFLUXDB_MEASUREMENT:
            try:
                measurement = "{}{}{}".format(INFLUXDB_MEASUREMENT, self.user.lower(), '_scores')
                ifx = influxdata.InfuxdbCient()
                ifx_flields = {}
                ifx_flields['score'] = self.bodyscores['score']
                ifx_flields['weight'] = self.bodyscores['deltas']['weight']
                ifx_flields['fat'] = self.bodyscores['deltas']['fat']
                ifx_flields['water'] = self.bodyscores['deltas']['water']
                ifx_flields['muscle'] = self.bodyscores['deltas']['muscle']
                ifx_flields['visceral'] = self.bodyscores['deltas']['visceral']
                ifx_flields['protein'] = self.bodyscores['deltas']['protein']
                ifx_flields['energie'] = self.bodyscores['engergieexp']
                ifx_flields['macro_prot'] = self.bodyscores['macronut']['protein']
                ifx_flields['macro_kh'] = self.bodyscores['macronut']['carbohydrates']
                ifx_flields['macro_fat'] = self.bodyscores['macronut']['fat']
                if ifx_flields:
                    log.info("Publish to INFLUXDB: {}, Time:{}, fields:{}".format(measurement, self.data['timestamp'], ifx_flields))
                    ifx.post(ifx_flields, measurement, self.data['timestamp'])
                    return True

            except BaseException as e:
                log.error(f"Error {__name__}, Tag: {INFLUXDB_MEASUREMENT + self.user.lower()} {str(e)} line {sys.exc_info()[-1].tb_lineno}")
                pass

    def publish2Influxdb(self):

        if not self.ready:
            return False

        if self.data and INFLUXDB_MEASUREMENT:
            try:
                measurement = "{}{}".format(INFLUXDB_MEASUREMENT, self.user.lower())
                ifx = influxdata.InfuxdbCient()
                if IFLUXDB_DATALIST:
                    ifx_flields = {}
                    for field in IFLUXDB_DATALIST:
                        if field in self.data:
                            ifx_flields[field] = self.data[field]
                else:
                    ifx_flields = self.data
                if ifx_flields:
                    log.info("Publish to INFLUXDB: {}, Time:{}, fields:{}".format(measurement, self.data['timestamp'], ifx_flields))
                    ifx.post(ifx_flields, measurement, self.data['timestamp'])
                    return True

            except BaseException as e:
                log.error(f"Error {__name__}, Tag: {INFLUXDB_MEASUREMENT + self.user.lower()} {str(e)} line {sys.exc_info()[-1].tb_lineno}")
                pass

    def publishdata(self, datasections: dict = None):

        if not self.ready:
            return False

        try:
            if not datasections:
                # default
                datasections = {
                    "fulldata": True,
                    "scores": True,
                    "simpledata": True,
                    "influxdb": True
                }

            self.__setBodyMetricsdata__()

            if "fulldata" in datasections:
                # publish 'tele/user/data' the body metrics data for the current user
                self.data["icon"] = "mdi:scale-bathroom"
                self.data['attribution'] = ATTRIBUTION
                topic = "{}/{}/data".format(MQTT_PREFIX, self.user)
                self.__publishdata__(topic, self.data)

            if "scores" in datasections:
                if self.bodyscores and 'score' in self.bodyscores:
                    # publish 'tele/user/scores' the body metrics data for the current user
                    topic = "{}/{}/scores".format(MQTT_PREFIX, self.user)
                    self.bodyscores["icon"] = "mdi:scale-bathroom"
                    self.bodyscores['attribution'] = ATTRIBUTION
                    self.__publishdata__(topic, self.bodyscores)

            if DATA_DIR:
                # save the data ti the history files
                log.debug("Save {} data to file".format(self.user))
                self.__savedata__()

            if "simpledata" in datasections:
                # publish 'tele/user/measured' the body metrics data for the current user
                self.__setSimpledata__()
                topic = "{}/{}/measured".format(MQTT_PREFIX, self.user)
                self.__publishdata__(topic, self.simpledata)

            if "influxdb" in datasections and INFLUXDB_HOST:
                # publish data to influxdb
                self.publish2Influxdb()
                self.bodyScores2Influxdb()
            return True

        except BaseException as e:
            log.error(f"Error {__name__}, Data for: {self.user}, Error: {str(e)} line {sys.exc_info()[-1].tb_lineno}")
            pass

    def __publishdata__(self, topic: str = MQTT_PREFIX, data: dict = None):
        if not self.ready:
            return False
        if MQTT_HOST and MQTT_PREFIX and data:
            try:
                if data and topic:
                    log.info("MQTT publish {},  payload:{}.".format(topic, json.dumps(data)))
                    mqtt_client = mqtt.client()
                    if mqtt_client.ready:
                        mqtt_client.publish(topic, data, True)
                        return True
                else:
                    log.error()("MQTT publish failed, not data present!")
                    return False
            except BaseException as e:
                log.error(f"Error {__name__}, topic: {topic} {str(e)} line {sys.exc_info()[-1].tb_lineno}")
                pass
