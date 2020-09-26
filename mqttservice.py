#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
sys.path.append("..")

if sys.version_info[0] < 3:
    raise Exception("Python 3 is required to run")

try:
    import os.path
    import paho.mqtt.client as mqtt
    import json
    import threading
    import time
    from time import sleep

    from conf import *
    from lib import logger
    from lib.calcdata import CalcData

except Exception as e:
    print('Import error {}, check requirements.txt'.format(e))
    sys.exit(1)


# register the application logger
appLogger = logger.Log("MQTTSERVICE", MQTT_CLEINTID, LOG_LEVEL)


def MicsaleData():
    """Main Application
    """

    def on_connect(client, userdata, flags, rc):
        # The callback for when the client receives a CONNACK response from the server.
        if rc == mqtt.CONNACK_ACCEPTED:
            appLogger.debug("{} connected OK, subscribe to topic {}".format(MQTT_HOST, MQTT_DATATOPIC))
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe(MQTT_DATATOPIC)
        else:
            appLogger.error("{} Bad connection, returned code= {}".format(MQTT_HOST, rc))

    def on_publish(client, userdata, mid):
        appLogger.debug("Message Id {} published.".format(str(mid)))

    def on_message(client, userdata, msg):
        # The on_message callback is called for each message received ...
        appLogger.info("New MQTT Message received topic {}".format(msg.topic))
        # make all calculations
        if(msg.topic == MQTT_DATATOPIC):
            # make the calculations
            data = json.loads(str(msg.payload.decode("utf-8")))
            if data:
                mCalc = CalcData(data, True)
                if mCalc.ready:
                    publishmode = {
                        "fulldata": True,
                        "scores": True,
                        "simpledata": True,
                        "influxdb": True
                    }
                    mCalc.publishdata(publishmode)
            else:
                appLogger.error("Missing Data for {}".format(MQTT_DATATOPIC))

    def on_disconnect(client, userdata, rc):
        # he on_disconnect() callback is called when the client disconnects from the broker.
        if rc != 1:
            appLogger.info("MiScale MQTT Client {} {} got disconnected (code: {rc}".format(MQTT_HOST, MQTT_AVAILABILITY_TOPIC, rc))

    def on_log(client, userdata, level, buf):
        appLogger.debug("Mqtt Logmessage {}:  {}".format(level, buf))

    appLogger.debug("MiScale MQTT Client {}".format(MQTT_HOST))
    mqttclient = mqtt.Client()

    # Assign event callbacks
    mqttclient.on_connect = on_connect
    mqttclient.on_publish = on_publish
    mqttclient.on_message = on_message
    mqttclient.on_disconnect = on_disconnect

    # enable /disable logging
    if MQTT_ENABLE_LOGGING:
        appLogger.info("Enable Logging for {}".format(MQTT_HOST))
        mqttclient.on_log = on_log
        mqttclient.enable_logger(appLogger.logger)

    # Connect to mqtt brocker
    appLogger.info("MiScale connect to MQTT Client {}, {}".format(MQTT_HOST, MQTT_AVAILABILITY_TOPIC))

    # To connect with a username and password, call username_pw_set() before connecting:
    mqttclient.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # Set a Will to be sent by the broker in case the client disconnects unexpectedly.
    mqttclient.will_set(MQTT_AVAILABILITY_TOPIC, 'Offline', 2, True)

    # conect to the MQTT Broker
    mqttclient.connect(MQTT_HOST, MQTT_PORT, keepalive=MQTT_KEEPALIVE)

    # Wait until we've connected
    while not not mqttclient.is_connected():  # wait in loop
        appLogger.debug("Waiting for connection {}".format(MQTT_HOST))
        time.sleep(1)

    # publish online state
    mqttclient.publish(MQTT_AVAILABILITY_TOPIC, 'Online', 2, True)

    # The loop_forever call blocks the main thread and so it will never terminate.
    # Press crtl+c to exit
    mqttclient.loop_forever()


# Start main application
while True:
    try:
        appLogger.info("MiScale MQTT service data application start")
        MicsaleData()
    except KeyboardInterrupt:
        appLogger.info("MiScale MQTT service stopped.")
        print('')
        sys.exit(0)
    except Exception as e:
        appLogger.error(f"Error while running the script: {str(e)},  line {sys.exc_info()[-1].tb_lineno}")
