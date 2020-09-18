#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Body Composition Scale 2 (XMTZC05HM) Data to MQTT / Influxdb
# App to read weight measurements from Xiaomi Body Scales.

# Rootless Setup
# sudo apt-get install libcap2-bin
# sudo setcap 'cap_net_raw,cap_net_admin+eip' `readlink -f \`which python3\``
# sudo setcap 'cap_net_raw+ep' `readlink -f \`which hcitool\``


import sys
sys.path.append("..")

if sys.version_info[0] < 3:
    raise Exception("Python 3 is required to run")

try:
    import os
    import subprocess
    from bluepy import btle
    from bluepy.btle import Scanner, BTLEDisconnectError, BTLEManagementError, DefaultDelegate

    from datetime import datetime
    import time

    from conf import *
    from lib import logger

    from lib.miscale2 import Miscale2Decoder
    from lib.calcdata import CalcData

except Exception as e:
    print('Import error {}, check requirements.txt'.format(e))
    sys.exit(1)


log = logger.Log(__name__, LOG_LEVEL)


class ScanProcessor():

    def __init__(self):
        log.debug("Init ScanProcessor")

    def handleDiscovery(self, dev, isNewDev, isNewData):

        log.debug("Device {}, New:{}, Newdata:{}".format(dev.addr, isNewDev, isNewData))
        # -------------------------------------------
        # decode data form the mi scale 2 device
        # ------------------------------------------
        if dev.addr == MI2_MAC.lower() and isNewDev:
            mi2_decoder = Miscale2Decoder(dev)
            mi_data = mi2_decoder.getData()
            if mi_data:
                mCalc = CalcData(mi_data)
                # publish to mqtt
                if MQTT_HOST:
                    mCalc.publishdata()
                # influxdb
                if INFLUXDB_HOST:
                    mCalc.publish2Influxdb()


def main():

    BluetoothFailCounter = 0

    while True:
        try:
            scanner = btle.Scanner().withDelegate(ScanProcessor())
            log.info("Scanning for devices...")
            devices = scanner.scan(5)  # Adding passive=True to try and fix issues on RPi devices
            time.sleep(TIME_INTERVAL)
        except BTLEDisconnectError as e:
            log.error("BTLE disconnected {}".format(e))
            pass
        except BTLEManagementError as e:
            sys.stderr.write(f"{datetime.now().strftime(DATEFORMAT_MISCAN)} - Bluetooth connection error: {error}\n")
            log.error("Bluetooth connection error:{}".format(e))
            if BluetoothFailCounter >= 4:
                cmd = 'hciconfig ' + HCI_DEV + ' down'
                log.debug("shell command: {}".format(cmd))
                ps = subprocess.Popen(cmd, shell=True)
                time.sleep(1)
                cmd = 'hciconfig hci' + HCI_DEV + ' up'
                log.debug("shell command: {}".format(cmd))
                ps = subprocess.Popen(cmd, shell=True)
                time.sleep(30)
                BluetoothFailCounter = 0
            else:
                BluetoothFailCounter += 1
        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            log.error(f"Error while running the script: {str(e)},  line {sys.exc_info()[-1].tb_lineno}")
            pass


if __name__ == "__main__":
    main()
