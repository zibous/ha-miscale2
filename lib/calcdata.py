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
    from lib import influxdata

except Exception as e:
    print('Import error {}, check requirements.txt'.format(e))
    sys.exit(1)

log = logger.Log(__name__, LOG_LEVEL)


class CalcData():

    version = '1.0.0'

    def __init__(self, data: dict = None, useAgeCalc: bool = True):
        self.useAgeCalc = useAgeCalc
        # current user settings
        self.user = 'default'
        self.dob = None
        self.height = 178
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
        self.simpledata = data
        self.bodyscores = {}
        if self.data and "measured" in self.data and "impedance" in self.data:
            self.weight = float(self.data["measured"])
            self.impedance = int(self.data["impedance"])
            if self.data["unit"] and "unit" in self.data:
                self.unit = self.data["unit"]
            if self.data["timestamp"] and "timstamp" in self.data:
                self.timestamp = self.data["timestamp"]
            self.__setUserData__()
            self.ready = True

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

    def round_to_value(self, number, roundto: float = 0.5) -> str:
        return str(round(float(number) / roundto) * roundto)

    def __recalibrate__(self):
        if self.adjustments and self.athletic:
            idx = self.round_to_value(self.weight)
            if idx in self.adjustments:
                log.debug('Calibration data found for {}, weight: {}{}'.format(self.user, self.weight, self.unit))    
                cf = self.adjustments[idx]
                self.data['fat'] = round(float(self.data['fat']) * float(cf['fat']), 2)
                #self.data['visceral'] = round(float(self.data['visceral']) * float(cf['visceral']), 2)
                self.data['water'] = round(float(self.data['water']) * float(cf['water']), 2)
                self.data['bone'] = round(float(self.data['bone']) * float(cf['bone']), 2)
                # self.data['muscle'] = round(float(self.data['muscle'])*float(cf['muscle']),2)
            else:
                log.debug('No calibration data found for {}, weight: {}{}'.format(self.user, self.weight, self.unit))    

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
        current_date = date.today().isoformat()
        return (date.today() - timedelta(days=365 * 18)).isoformat()

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

    def __calcdatadiff__(self) -> dict:
        if self.data:
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
                            result['weight'] = round(self.data['weight'] - data_prev['weight'], 2)
                            result['fat'] = round(self.data['fat'] - data_prev['fat'], 2)
                            result['water'] = round(self.data['water'] - data_prev['water'], 2)
                            result['muscle'] = round(self.data['muscle'] - data_prev['muscle'], 2)
                            result['visceral'] = round(self.data['visceral'] - data_prev['visceral'], 2)
                            result['protein'] = round(self.data['protein'] - data_prev['protein'], 2)
                            return result
            except BaseException as e:
                log.error(f"Error Read previous file {file_path}, {str(e)} line {sys.exc_info()[-1].tb_lineno}")
                pass

        return None

    def __savedata__(self):
        if self.data:
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

    def __setSimpledata__(self):
        try:
            self.simpledata['user'] = self.user
            self.simpledata['sex'] = self.sex
            self.simpledata['athletic'] = self.athletic
            self.simpledata['age'] = round(self.age, 2)
            self.simpledata['weight'] = round(self.weight, 2)
            self.simpledata['unit'] = self.unit
            self.simpledata['impedance'] = self.impedance
            self.simpledata['bmi'] = round((self.weight / (self.height ** 2)) * 10000, 2)
            self.simpledata['water'] = round(0.72 * (-1.976 + 0.907 * self.weight), 2)
            self.simpledata['fat'] = round((1.281 * self.data['bmi']) - 10.13, 2)
            self.simpledata['leanfat'] = round((1.281 * self.data['bmi']) - 10.13, 2)
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

            log.debug("Set Body Metrics data for {}, Weight:{}".format(self.user,self.weight))
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
            self.data['bodytype'] = BODY_SCALE_TPYES[lib.getBodyType()]

            # weight
            self.data['weight'] = round(self.weight, 2)
            self.data['idealweight'] = round(lib.getIdealWeight(), 2)
            self.data['targetweight'] = self.userscores['WEIGHT']
            self.data['unit'] = self.unit

            self.data['lbm'] = round(lib.getLBMCoefficient(), 2)
            # fat
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
            self.data['protein'] = round(lib.getProteinPercentage(), 2)

            self.data['bmr'] = round(lib.getBMR(), 2)
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
            self.bodyscores['bmi'] = score.getBmiDeductScore()
            self.bodyscores['fat'] = score.getBodyFatDeductScore()
            self.bodyscores['visceral'] = score.getVisceralFatDeductScore()
            self.bodyscores['muscle'] = score.getMuscleDeductScore()
            self.bodyscores['water'] = score.getWaterDeductScore()
            self.bodyscores['bones'] = score.getBoneDeductScore()
            self.bodyscores['bmr'] = score.getBasalMetabolismDeductScore()
            self.bodyscores['protein'] = score.getProteinDeductScore()
            self.bodyscores['version'] = self.version
            self.bodyscores['timestamp'] = self.timestamp
            log.debug("Bodyscores for {}: {}".format(self.user, self.bodyscores))

            # publish the data
            topic = "{}/{}/scores".format(MQTT_PREFIX, self.user)
            self.bodyscores["icon"] = "mdi:scale-bathroom"
            self.bodyscores['attribution'] = ATTRIBUTION
            self.__publishdata__(topic, self.bodyscores)

        except Exception as e:
            log.error(f"Error {__name__}: {str(e)},  line {sys.exc_info()[-1].tb_lineno}")
            pass

    def publish2Influxdb(self):
        if self.data:
            try:
                ifx = influxdata.InfuxdbCient()
                ifx.post(self.data, 'MISCALEDATA_' + self.user)
                return True
            except BaseException as e:
                log.error(f"Error {__name__}, Tag: {'MISCALEDATA_' + self.user} {str(e)} line {sys.exc_info()[-1].tb_lineno}")
                pass

    def publishSimpeData(self):
        self.__setSimpledata__()
        if self.simpledata:
            topic = "{}/{}/measured".format(MQTT_PREFIX, self.user)
            self.__publishdata__(topic, self.simpledata)


    def publishdata(self):
        # publish the body metrics data for the current user
        self.__setBodyMetricsdata__()

        self.data["icon"] = "mdi:scale-bathroom"
        self.data['attribution'] = ATTRIBUTION
        topic = "{}/{}/data".format(MQTT_PREFIX, self.user)
        self.__publishdata__(topic, self.data)

        # publish the body metrics changes for the current user
        diffdata = self.__calcdatadiff__()
        if diffdata:
            topic = "{}/{}/prevdata".format(MQTT_PREFIX, self.user)
            self.__publishdata__(topic, diffdata)

        # save the data ti the history files
        if DATA_DIR:
            log.debug("Save {} data to file".format(self.user))
            self.__savedata__()

        self.publishSimpeData()

    def __publishdata__(self, topic: str = MQTT_PREFIX, data: dict = None):
        try:
            if data:
                log.debug("MQTT publish {} payload: {}".format(topic, self.user, json.dumps(data)))
                publish.single(
                    topic,
                    payload=json.dumps(data),
                    qos=0,
                    retain=False,
                    hostname=MQTT_HOST,
                    port=MQTT_PORT,
                    client_id=MQTT_CLEINTID,
                    keepalive=MQTT_KEEPALIVE,
                    auth={'username': MQTT_USERNAME, 'password': MQTT_PASSWORD}
                )
            else:
                log.debug("MQTT publish failed, not data present!")
        except BaseException as e:
            log.error(f"Error {__name__}, topic: {topic} {str(e)} line {sys.exc_info()[-1].tb_lineno}")
            pass
