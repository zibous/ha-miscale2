# Connector for Xiaomi Mi Scale

## Body Composition Scale 2 (XMTZC05HM) Data to MQTT / Influxdb
Code to read weight measurements from Xiaomi Body Scales.

## Prerequisites

An MQTT broker is needed as the counterpart for this daemon. Even though an MQTT-less mode is provided, it is not recommended for normal smart home automation integration. MQTT is huge help in connecting different parts of your smart home and setting up of a broker is quick and easy.



## Installation

On a modern Linux system just a few steps are needed to get the daemon working. The following example shows the installation under Debian/Raspbian below the `/opt` directory:



```bash
$ git clone https://github.com/zibous/ha-miscale.git /opt/ha-miscale
$ cd /opt/ha-miscale
$ sudo pip3 install -r requirements.txt

```

To match personal needs, all operation details can be configured using the file **config.py** The file needs to be created first:

```bash
$ cd /opt/ha-miscale
$ cp conf.py.dist conf.py
$ nano conf.py

$ chmod +x app.py
$ chmod +x mqttservice.py

## tests
$ python3 app.py
$ ./app.py

$ python3 mqttservice.py
$ ./mqttservice.py
```



## Application for Raspberry / Linux computer

Read [Xiaomi Mi Body Composition Scale](https://www.mi.com/global/mi-body-composition-scale) data from a Raspberry Pi in Python 3.

`python3 app.py`

### Execution

## MQTT service for ESP32 Devices
A simple Python script which provides a MQTT gateway for ESP Devices, easily extensible via custom workers. Application for ESP Devices see:

https://github.com/1technophile/OpenMQTTGateway

### Execution
`python3 mqttservice.py`

## Configuration

You most probably want to execute the program **continuously in the background**. This can be done either by using the internal daemon or cron.

**Attention:** Daemon mode must be enabled in the configuration file (default).

1. Systemd service - on systemd powered systems the **recommended** option

   ```bash
   sudo cp /opt/ha-miscale/service_app.template /etc/systemd/system/ha-miscale.service
   
   sudo systemctl daemon-reload
   sudo systemctl start ha-miscale.service
   sudo systemctl status ha-miscale.service
   
   sudo systemctl enable ha-miscale.service
   ```




# Acknowledgements:
Thanks @lolouk44 to https://github.com/lolouk44/xiaomi_mi_scale
Formulas to calculate the various values/measures, I've got them from https://github.com/wiecosystem/Bluetooth


# Informations
https://www.wikihow.fitness/Determine-Lean-Body-Mass
https://www.omnicalculator.com/health/body-fat#how-to-calculate-body-fat
https://calculator-online.net/ideal-weight-calculator/
https://en.wikipedia.org/wiki/Body_mass_index
https://www.calculator.net/bmi-calculator.html
https://www.calculator.net/calorie-calculator.html
https://www.omnicalculator.com/health/bmr-katch-mcardle#what-is-the-katch-mcardle-calculator
https://www.omnicalculator.com/health/maintenance-calorie
https://en.wikipedia.org/wiki/Body_water
https://en.wikipedia.org/wiki/Body_fat_percentage
https://en.wikipedia.org/wiki/Lean_body_mass
https://en.wikipedia.org/wiki/Lean_body_mass
https://www.calculator.net/lean-body-mass-calculator.html
http://www.dev.egofit.de/biadata-org/
https://github.com/zewelor/bt-mqtt-gateway
https://www.mi.com/global/mi-body-composition-scale
https://dev.to/henrylim96/reading-xiaomi-mi-scale-data-with-web-bluetooth-scanning-api-1mb9

https://github.com/Wingjam/ReverseMiScale/blob/master/miScale.py

https://tanita.de/hilfe-und-anleitungen/richtige-interpretation-ihrer-messwerte/

# Omron, Medisana, Xiaomi
https://www.amazon.de/Omron-HBF-511B-E-Ganzkörperanalyse-Waage-BF511-blau/dp/B0033AGBW0
https://www.amazon.de/Medisana-TargetScale-3-0-Waage/dp/B01MZ1VBWZ/
https://www.amazon.de/Xiaomi-Smart-Bluetooth-Monitor-Display/dp/B07WNM9B57/