#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

try:
    from datetime import datetime
    import time
    
    from constants import AD_TYPES, UNITS
    from conf import *
    from lib import logger
    
except Exception as e:
    print('Import error {}, check requirements.txt'.format(e))


log = logger.Log(__name__, LOG_LEVEL)

class Miscale2Decoder():

    resultData = None
    version = '1.0.0'

    def __init__(self, dev):

        log.debug("Init Miscale2Decoder")

        self.bledevice = dev
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
        self.unit = None

        self.lastscan = str(datetime.today().strftime(DATEFORMAT_MISCAN))
        self.resultData = None

        if self.bledevice and self.scanData:
            self.__decodedata__()
        else:
            log.debug("✘ NO DEVICE OR DATA present !")

    def getData(self):
        return self.resultData

    def __decodeWeight__(self):

        if self.data:
            # get weight
            self.measured = 0.00
            self.unit = None

            self.measured = int((self.data[28:30] + self.data[26:28]), 16) * 0.01
            log.debug("✔︎ (Measured 1:{}, p1:{}, p2:{}".format(self.measured, self.data[28:30], self.data[26:28]))

            # data2=bytes.fromhex(self.data[4:])
            # mi_easured = (((data2[12] & 0xFF) << 8) | (data2[11] & 0xFF))  # /200 kg
            # log.debug("✔︎ (Measured 2:{}".format(mi_easured))

            # get unit
            measunit = self.data[4:6]
            if measunit.startswith(('03', 'b3')):
                # Imperial pound
                self.unit = 'lbs'
                self.calcweight = round(self.measured  * 0.4536, 2)
            if measunit.startswith(('12', 'b2')):
                # Chinese Catty
                self.unit = 'jin'
                self.calcweight = round(self.measured * 0.50 * 0.5, 2)
            if measunit == "02" or measunit.startswith(('22', 'a2')):
                # MKS kg
                self.unit = 'kg'
                self.measured = self.measured * 0.50
                self.calcweight = self.measured
                
            log.debug("✔︎ Unit: {}, Measunit:{}".format(self.unit, measunit))

    def __decodeImpedance__(self):
        # get impedance
        self.impedance = str(int((self.data[24:26] + self.data[22:24]), 16))
        log.debug("✔︎ Impedance  = {} Ω,  p1:{}, p2:{}".format(self.impedance, self.data[24:26], self.data[22:24]))

        # data2=bytes.fromhex(self.data[4:])
        # mi_impedance = ((data2[10] & 0xFF) << 8) | (data2[9] & 0xFF)
        # log.debug("✔︎ Impedance2 = {} Ω".format(mi_impedance))

    def __decodeTimestamp__(self):
        if self.data:
            log.debug("✔︎ Timestamp: {}-{}-{} {}:{}:{}".format(
                self.data[10:12] + self.data[8:10],
                self.data[12:14], self.data[14:16],
                self.data[16:18], self.data[18:20],
                self.data[20:22])
            )
            return datetime.strptime(
                str(int((self.data[10:12] + self.data[8:10]), 16))
                + "-"
                + str(int((self.data[12:14]), 16))
                + "-"
                + str(int((self.data[14:16]), 16))
                + " "
                + str(int((self.data[16:18]), 16))
                + ":"
                + str(int((self.data[18:20]), 16))
                + ":"
                + str(int((self.data[20:22]), 16)),
                DATEFORMAT_MISCAN,
            )

    def __setResults__(self):
        if self.measured and self.impedance:
            self.resultData = {
                "measured": self.measured,
                "calcweight": self.calcweight,
                "unit": self.unit,
                "impedance": self.impedance,
                "timestamp": self.timestamp,
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
        log.debug("✔︎ Control bytes:{} Emptyload:{},Stabilized:{},Has Impedanz:{}".format(ctrlByte1, self.loadRemoved, self.isStabilized, self.hasImpedance))
        return self.loadRemoved and self.hasImpedance


    def __decodedata__(self):

        log.info("Device {} {} {} dBm".format(self.bledevice.addr, self.bledevice.addrType, self.bledevice.rssi))

        # log.debug("Scandata:{}".format(self.bledevice.getScanData()))
        # Scandata:[
        # (1, 'Flags', '06'),
        # (2, 'Incomplete 16b Services', '0000181b-0000-1000-8000-00805f9b34fb'),
        # (22, '16b Service Data', '1b1802a6e4070908152707d4012837'),
        # (9, 'Complete Local Name', 'MIBFS'),
        # (255, 'Manufacturer', '57015ccad34cee74')
        # ]

        try:
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

                    log.debug("✔︎ SSID:{}, Type:{}".format(sdid, data[1:4]))

                    # check control byte
                    if not self.__checkControlByte__():
                        log.debug("✘ Not stabilized....")
                        continue

                    # get weight
                    self.__decodeWeight__()
                    if not self.measured:
                        log.debug("✘ No measure data found...")
                        continue

                    # get impedance
                    self.__decodeImpedance__()

                    if not all([self.isStabilized, self.unit, self.hasImpedance]):
                        log.debug("✘ Not stabilized....")
                        continue

                    if self.impedance:

                        # get timestamp from the device
                        self.timestamp = self.__decodeTimestamp__()

                        # final check and build result data
                        if self.timestamp and (str(self.timestamp) > self.lastscan):
                            self.lastscan = str(self.timestamp)
                            self.__setResults__()

                    else:
                        log.debug("✘ Device {} {} is sleeping !".format(self.bledevice.addr, self.bledevice.addrType))

                elif sdid == MI2_DATAFLAG or sdid == MI2_NOSERVICE or sdid == MI2_LOCALNAME:
                    # (1, 'Flags', '06'),
                    # (2, 'Incomplete 16b Services', '0000181b-0000-1000-8000-00805f9b34fb'),
                    # (9, 'Complete Local Name', 'MIBFS'),
                    log.debug(("✘ SSID:{}, Data:{}").format(sdid, data))
                    continue
                elif sdid == MI2_MANUFACTORID:
                    # (255, 'Manufacturer', '57015ccad34cee74')
                    log.debug(("✘ SSID:{}, Data:{}").format(sdid, data))
                    continue
                else:
                    log.debug("✘ New unknown packet: type={} data={} !".format(sdid, data))

        except Exception as e:
            log.error(f"Error {__name__}: {str(e)},  line {sys.exc_info()[-1].tb_lineno}")
            pass
