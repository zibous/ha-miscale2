#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

try:
    import os
    import signal
    import time  

    from conf import *
    from lib import logger
    from lib import mqtt

except Exception as e:
    print(f"Import error: {str(e)} line {sys.exc_info()[-1].tb_lineno}, check requirements.txt")
    sys.exit(1)


log = logger.Log("SignalTestcase", MI2_SHORTNAME, 10)
print(__name__, MI2_SHORTNAME, 20)

# store default handler of signal.SIGINT
# default_handler = signal.getsignal(signal.SIGINT)

def publish(state:str="Online"):
    mqtt_client = mqtt.client()
    if mqtt_client and mqtt_client.ready:
        mqtt_client.publish_simple("tele/apptest/LWT", state, True)    

def handler(signum, frame):
    publish('Offline')
    log.debug("Ende Application")
    exit(0)
   
def main():
    while True:
        try:
            pass
            time.sleep(30)
        except Exception as e:
            Log.error(f"Error while running the script: {str(e)},  line {sys.exc_info()[-1].tb_lineno}")


if __name__ == "__main__":
    log.debug("Start Application")
    signal.signal(signal.SIGINT, handler)
    publish('Online')
    main()
