#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

try:

    import paho.mqtt.publish as publish
    import os
    import json

    from config import *
    from common import logger

except Exception as e:
    print('Import error {}, check requirements.txt'.format(e))

log = logger.Log(__name__, MI2_SHORTNAME, LOG_LEVEL)


class client:
    """MQTT Message to mqtt brocker
    """
    version = "1.0.1"
    ready = False

    # Constructor
    def __init__(self, host: str = MQTT_HOST, port: int = MQTT_PORT, clientId: str = os.uname().nodename, auth=None):
        self.mqttBrocker = host
        self.port = port
        self.clientId = clientId
        self.auth = auth
        if self.mqttBrocker:
            self.ready = True

    def publish_simple(self, topic: str = MQTT_AVAILABILITY_TOPIC, payload: str = 'Offline', retain: bool = True, qos: int = 0, keepalive: int = MQTT_TIMEOUT):
        if not self.ready:
            return
        try:
            if payload:
                if(self.auth):
                    # publish with authenification
                    log.info("Publish LWT with authenification {}, {}".format(self.mqttBrocker, topic))
                    publish.single(topic,
                                   payload=payload,
                                   qos=qos,
                                   retain=retain,
                                   hostname=self.mqttBrocker,
                                   port=self.port,
                                   client_id=self.clientId,
                                   keepalive=keepalive,
                                   auth=self.auth)
                else:
                    # publish w/o authenification
                    log.info("Publish LWT w/o authenification {}, {}".format(self.mqttBrocker, topic))
                    publish.single(topic,
                                   payload=payload,
                                   qos=qos,
                                   retain=retain,
                                   hostname=self.mqttBrocker,
                                   port=self.port,
                                   client_id=self.clientId,
                                   keepalive=keepalive)
        except BaseException as e:
            log.error(f"Error Publish LWT {self.mqttBrocker}, {topic}, {str(e)} line {sys.exc_info()[-1].tb_lineno}")
            pass


    # publish data to the defined mqtt brocker
    def publish(self, topic: str = MQTT_TOPIC, payload: dict = None, retain: bool = False, qos: int = 0, keepalive: int = MQTT_TIMEOUT):
        if not self.ready:
            return
        try:
            if payload:
                if(self.auth):
                    # publish with authenification
                    log.info("Publish data with authenification {}, {}".format(self.mqttBrocker, topic))
                    publish.single(topic,
                                   payload=json.dumps(payload),
                                   qos=qos,
                                   retain=retain,
                                   hostname=self.mqttBrocker,
                                   port=self.port,
                                   client_id=self.clientId,
                                   keepalive=keepalive,
                                   auth=self.auth)
                else:
                    # publish w/o authenification
                    log.info("Publish data w/o authenification {}, {}".format(self.mqttBrocker, topic))
                    publish.single(topic,
                                   payload=json.dumps(payload),
                                   qos=qos,
                                   retain=retain,
                                   hostname=self.mqttBrocker,
                                   port=self.port,
                                   client_id=self.clientId,
                                   keepalive=keepalive)
        except BaseException as e:
            log.error(f"Error Publish data {self.mqttBrocker}, {topic}, {str(e)} line {sys.exc_info()[-1].tb_lineno}")
            pass
