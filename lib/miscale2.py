#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

try:
    from datetime import datetime
    import time
    import pytz

    import paho.mqtt.publish as publish
    import json

    from conf import *
    from lib import logger
    from lib import mqtt

except Exception as e:
    print('Import error {}, check requirements.txt'.format(e))


log = logger.Log(__name__, MI2_SHORTNAME, LOG_LEVEL)


def last_timeStamp(action: str = "set", value: str = None):
    global LAST_TIMESTAMP
    if action == 'set':
        if value:
            LAST_TIMESTAMP = value
        else:
            LAST_TIMESTAMP = str(datetime.today().strftime(DATEFORMAT_MISCAN))
    if action == 'get':
        if LAST_TIMESTAMP is None:
            LAST_TIMESTAMP = str(datetime.today().strftime(DATEFORMAT_MISCAN))
        return LAST_TIMESTAMP


class Miscale2Decoder():

    resultData = None
    version = '1.0.0'

    def __init__(self, dev):

        log.debug("Init Miscale2Decoder")

        self.bledevice = dev
        self.manufacturer = None
        self.scaninfo = "0-waiting..."
        self.scanData = dev.getScanData()
        self.data = None
        self.devicedata = list()

        self.loadRemoved = False
        self.isStabilized = False
        self.hasImpedance = False

        self.timestamp = None
        self.measured = 0.00
        self.calcweight = 0.00
        self.impedance = 0
        self.unit = 'kg'

        self.devicestate = 'unknown'
        self.lastscan = last_timeStamp('get')

        self.resultData = None

        if self.bledevice and self.scanData:
            self.__decodedata__()
        else:
            log.debug("NO DEVICE OR DATA present !")

    def getData(self):
        return self.resultData

    def __decodeWeight__(self):

        if self.data:
            # get weight
            self.measured = 0.00
            self.unit = None

            self.measured = float(int((self.data[28:30] + self.data[26:28]), 16) * 0.01)
            log.debug("Measured 1:{}, p1:{}, p2:{}".format(self.measured, self.data[28:30], self.data[26:28]))

            # get unit
            measunit = self.data[4:6]
            if measunit.startswith(('03', 'b3')):
                # Imperial pound
                self.unit = 'lbs'
                self.calcweight = round(self.measured * 0.4536, 2)
            if measunit.startswith(('12', 'b2')):
                # Chinese Catty
                self.unit = 'jin'
                self.calcweight = round(self.measured * 0.50 * 0.5, 2)
            if measunit == "02" or measunit.startswith(('22', 'a2')):
                # MKS kg
                self.unit = 'kg'
                self.measured = self.measured * 0.50
                self.calcweight = self.measured

            log.debug("Unit: {}, Measunit:{}".format(self.unit, measunit))

    def __decodeImpedance__(self):
        # get impedance
        self.impedance = int(str(int((self.data[24:26] + self.data[22:24]), 16)))
        log.debug("Impedance  = {} Ω,  p1:{}, p2:{}".format(self.impedance, self.data[24:26], self.data[22:24]))

    def __decodeTimestamp__(self):
        try:
            if self.data:
                mi_timestamp = "{}-{}-{} {}:{}:{}".format(
                    int((self.data[10:12] + self.data[8:10]), 16),
                    int((self.data[12:14]), 16),
                    int((self.data[14:16]), 16),
                    int((self.data[16:18]), 16),
                    int((self.data[18:20]), 16),
                    int((self.data[20:22]), 16)
                )
                mi_datetime = datetime.strptime(mi_timestamp, DATEFORMAT_MISCAN)
                log.debug("Mi-Date: {}, Current time: {} vs. Last scan time: {}".format(mi_timestamp, mi_datetime, LAST_TIMESTAMP))
                return mi_datetime
        except BaseException as e:
            log.error(f"Error {__name__}, topic: {topic} {str(e)} line {sys.exc_info()[-1].tb_lineno}")
            return datetime.utcnow().strftime(DATEFORMAT_UTC)

    def __setResults__(self):
        if self.measured and self.impedance:
            self.resultData = {
                "measured": float(self.measured),
                "calcweight": float(self.calcweight),
                "unit": self.unit,
                "impedance": int(self.impedance),
                "timestamp": str(self.timestamp),
                "scantime": str(datetime.today().strftime(DATEFORMAT_MISCAN))
            }
            return True

        return False

    def __checkControlByte__(self):
        # 02a6e4070908152707d4012837
        data2 = bytes.fromhex(self.data[4:])
        ctrlByte1 = data2[1]
        self.loadRemoved = ctrlByte1 & (1 << 7)
        self.isStabilized = ctrlByte1 & (1 << 5) != 0
        self.hasImpedance = ctrlByte1 & (1 << 1) != 0
        log.debug("Control bytes:{} Emptyload:{},Stabilized:{},Has Impedanz:{}".format(ctrlByte1, self.loadRemoved, self.isStabilized, self.hasImpedance))
        return self.loadRemoved and self.hasImpedance

    def __publishStateInfo__(self):
        try:
            self.devicestate = {
                'mac': self.bledevice.addr,
                'type': self.bledevice.addrType,
                'rssi': self.bledevice.rssi,
                'info': self.scaninfo,
                'load': self.loadRemoved,
                'stabilized': self.isStabilized,
                'measured': self.measured,
                'impedance': self.impedance,
                'unit': self.unit,
                'lastscan': self.lastscan,
                'version': self.version,
                'timestamp': str(datetime.today().strftime(DATEFORMAT_MISCAN)),
                'attribution': ATTRIBUTION
            }
            topic = "{}/state".format(MQTT_PREFIX)
            self.__publishdata__(topic, self.devicestate)
        except BaseException as e:
            log.error(f"Error {__name__}, topic: {topic} {str(e)} line {sys.exc_info()[-1].tb_lineno}")
            pass

    def __publishstatus__(self, devicestate: str = 'scanning'):
        try:
            data = {
                'mac': self.bledevice.addr,
                'type': self.bledevice.addrType,
                'rssi': self.bledevice.rssi,
                'info': self.scaninfo,
                'status': devicestate,
                'lastscan': self.lastscan,
                'version': self.version,
                'timestamp': str(datetime.today().strftime(DATEFORMAT_MISCAN)),
                'attribution': ATTRIBUTION
            }
            topic = "{}/status".format(MQTT_PREFIX)
            self.__publishdata__(topic, data)
        except BaseException as e:
            log.error(f"Error {__name__}, topic: {topic} {str(e)} line {sys.exc_info()[-1].tb_lineno}")
            pass

    def __publishdata__(self, topic: str = None, data: dict = None):
        try:
            if MQTT_HOST and MQTT_PREFIX and topic and data:
                mqtt_client = mqtt.client()
                if mqtt_client.ready:
                    mqtt_client.publish(topic, data, True)
        except BaseException as e:
            log.error(f"Error {__name__}, topic: {topic} {str(e)} line {sys.exc_info()[-1].tb_lineno}")
            pass

    def __decodedata__(self):

        log.info("Device {} {} {} dBm. Lastscan:{}".format(self.bledevice.addr, self.bledevice.addrType, self.bledevice.rssi, self.lastscan))

        # log.debug("Scandata:{}".format(self.bledevice.getScanData()))
        # Scandata:[
        # (1, 'Flags', '06'),
        # (2, 'Incomplete 16b Services', '0000181b-0000-1000-8000-00805f9b34fb'),
        # (22, '16b Service Data', '1b1802a6e4070908152707d4012837'),
        # (9, 'Complete Local Name', 'MIBFS'),
        # (255, 'Manufacturer', '57015ccad34cee74')
        # ]

        try:
            # For each of the device's advertising data items, print a description of the data type and value of the data itself
            # getScanData returns a list of tupples: adtype, desc, value
            # where AD Type (sdid) means “advertising data type,” as defined by Bluetooth convention:
            # https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile
            # desc is a human-readable description of the data type and value is the data itself
            for (sdid, desc, data) in self.scanData:

                self.data = data

                # MiScale Raw Data Schema
                # +------+------------------------+
                # | byte |        function        |
                # +------+------------------------+
                # | 0    | Bit 0: unknown         |
                # |      | Bit 1: kg              |
                # |      | Bit 2: lbs             |
                # |      | Bit 3: unknown         |
                # |      | Bit 4: jin unit        |
                # |      | Bit 5: stabilized      |
                # |      | Bit 6: unknown         |
                # |      | Bit 7: load removed    |
                # +------+------------------------+
                # | 1-2  | weight (little endian) |
                # +------+------------------------+
                # | 3-7  | unknown                |
                # +------+------------------------+
                # | 8-9  | sequence (big endian)  |
                # +------+------------------------+

                # (22, '16b Service Data', '1b1802a6e4070908152707d4012837'),
                self.devicedata.append(data)

                if data.startswith(MI2_SCALE2ID) and sdid == MI2_DATAREADY:

                    log.debug("SSID:{}, Type:{}".format(sdid, data[1:4]))

                    self.scaninfo = "{}-{}-{}".format(sdid, desc, data)

                    self.__publishstatus__()

                    # check control byte
                    if not self.__checkControlByte__():
                        log.debug("Not stabilized....")
                        continue

                    # get weight
                    self.__decodeWeight__()
                    if not self.measured:
                        log.debug("No measure data found...")
                        continue

                    # get impedance
                    self.__decodeImpedance__()

                    if not all([self.isStabilized, self.unit, self.hasImpedance]):
                        log.debug("Not stabilized....")
                        continue

                    if self.impedance:

                        # get timestamp from the device
                        self.timestamp = self.__decodeTimestamp__()

                        self.__publishStateInfo__()

                        # final check and build result data
                        if self.timestamp and (str(self.timestamp) > self.lastscan):
                            self.lastscan = str(self.timestamp)
                            last_timeStamp('set', str(self.timestamp))
                            self.__setResults__()

                    else:
                        log.debug("Device {} {} is sleeping !".format(self.bledevice.addr, self.bledevice.addrType))
                        self.__publishstatus__('sleeping')

                elif sdid == MI2_DATAFLAG or sdid == MI2_NOSERVICE or sdid == MI2_LOCALNAME:
                    # (1, 'Flags', '06'),
                    # (2, 'Incomplete 16b Services', '0000181b-0000-1000-8000-00805f9b34fb'),
                    # (9, 'Complete Local Name', 'MIBFS'),
                    log.debug(("SSID:{}, Data:{}").format(sdid, data))
                    continue
                elif sdid == MI2_MANUFACTORID:
                    # (255, 'Manufacturer', '57015ccad34cee74')
                    log.debug(("SSID:{}, Data:{}").format(sdid, data))
                    continue
                else:
                    log.error("New unknown packet: type={} data={} !".format(sdid, data))

        except Exception as e:
            log.error(f"Error {__name__}: {str(e)},  line {sys.exc_info()[-1].tb_lineno}")
            pass
