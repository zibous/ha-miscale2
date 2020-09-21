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
    import asyncio
    from bluepy import btle
    from bluepy.btle import Scanner, BTLEDisconnectError, BTLEManagementError, DefaultDelegate

    from datetime import datetime
    import time

    from conf import *
    from lib import logger
    from lib import mqtt

    from lib.miscale2 import Miscale2Decoder
    from lib.calcdata import CalcData

except Exception as e:
    print('Import error {}, check requirements.txt'.format(e))
    sys.exit(1)


log = logger.Log(__name__, MI2_SHORTNAME, LOG_LEVEL)


def publishDeviceState(topicmode: str = 'Online', payload: dict = None):
    mqtt_client = mqtt.client()
    if mqtt_client and mqtt_client.ready:
        if topicmode == 'Online':
            mqtt_client.publish_simple()(MQTT_AVAILABILITY_TOPIC, topicmode, True)
        elif topicmode == 'Offline':
            mqtt_client.publish_simple()(MQTT_AVAILABILITY_TOPIC, topicmode, True)
        else:
            if payload:
                mqtt_client.publish_simple()(topicmode, payload, True)


class ScanProcessor():

    def __init__(self):
        log.debug("Init ScanProcessor")

    def handleDiscovery(self, dev, isNewDev, isNewData):
        # when this python script discovers a BLE broadcast packet, we can decode the data packet
        # for each device  in the list of devices
        if dev.addr == MI2_MAC.lower() and isNewDev:
            # ------------------------------------------
            # decode data form the mi scale 2 device
            # ------------------------------------------
            log.debug("Device {}, New:{}, Newdata:{}".format(dev.addr, isNewDev, isNewData))
            if isNewDev:
                payload = {
                    'application': __name__,
                    'message': "new device",
                    'mac': dev.addr,
                    'error': False,
                    "timestamp": str(datetime.today().strftime(DATEFORMAT_MISCAN))
                }
                publishDeviceState(MQTT_PREFIX + '/info', payload)
            if isNewData:
                payload = {
                    'application': __name__,
                    'message': "new data",
                    'mac': dev.addr,
                    'error': False,
                    "timestamp": str(datetime.today().strftime(DATEFORMAT_MISCAN))
                }
                publishDeviceState(MQTT_PREFIX + '/info', payload)
            mi2_decoder = Miscale2Decoder(dev)
            mi_data = mi2_decoder.getData()
            if mi_data:
                log.debug("New data present, make calulations and publish...")
                mCalc = CalcData(mi_data)
                if mCalc.ready:
                    mCalc.publishdata()


def main():

    BluetoothFailCounter = 0

    while True:
        try:
            scanner = btle.Scanner().withDelegate(ScanProcessor())
            # create a list of unique devices that the scanner discovered during a 10-second scan
            devices = scanner.scan(10)
            time.sleep(TIME_INTERVAL)
        except BTLEDisconnectError as e:
            log.error("BTLE disconnected {}".format(e))
            payload = {
                'application': __name__,
                'message': str(e),
                'error': True,
                "timestamp": str(datetime.today().strftime(DATEFORMAT_MISCAN))
            }
            publishDeviceState(MQTT_PREFIX + '/info', payload)
            pass
        except BTLEManagementError as e:
            log.error("Bluetooth connection error:{}".format(e))
            if BluetoothFailCounter >= 4:
                publishDeviceState('Offine')
                cmd = 'hciconfig ' + HCI_DEV + ' down'
                log.info("shell command: {}".format(cmd))
                ps = subprocess.Popen(cmd, shell=True)
                time.sleep(1)
                cmd = 'hciconfig hci' + HCI_DEV + ' up'
                log.debug("shell command: {}".format(cmd))
                ps = subprocess.Popen(cmd, shell=True)
                time.sleep(30)
                BluetoothFailCounter = 0
                publishDeviceState('Online')
            else:
                BluetoothFailCounter += 1
        except KeyboardInterrupt:
            publishDeviceState('Offine')
            log.info("Xiaomi Mi Scale Service Application stopped.")
            print('')
            sys.exit(0)
        except Exception as e:
            payload = {
                'application': __name__,
                'message': str(e),
                'error': True,
                "timestamp": str(datetime.today().strftime(DATEFORMAT_MISCAN))
            }
            publishDeviceState(MQTT_PREFIX + '/info', payload)
            log.error(f"Error while running the script: {str(e)},  line {sys.exc_info()[-1].tb_lineno}")
            pass


if __name__ == "__main__":
    log.info("Start Xiaomi Mi Scale Service Application")
    time.sleep(10)
    publishDeviceState('Online')
    main()
