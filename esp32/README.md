# ESP 32 MISCALE 2 BLE SCANNER APP



![app_states](../docs/app_states.png)



## Prerequisites

+ ESP32
<br/>

  ![ESP32 NodeMCU](../docs/ESP32 NodeMCU.png)
<br>
+ Platform IO
+ VSCODIUM
+ ESP APP ( see folder ESP)

<br/>
##Build ESP APP

+ Start VSCODIUM
+ Create a new configuration `cp config_distro.h config.h `
+ Edit configuration `edit config.h`
+ Connect ESP to usb port
+ Deploy esp application to the esp device

**### Example for data payload from ESP32 simple application**

`MQTT TOPIC: tele/bodyscale/data`

PAYLOAD :

```json
   { "measured": 71.00, 
      "calcweight": 142.00, 
      "impedance": 489, 
      "unit":"kg", 
      "user":"7", 
      "id":"5c:ca:d3:4c:ee:74", 
      "version":"1.0.4", 
      "timestamp":"2020-09-26 12:53:53", 
      "lastscan":"2020-09-25 16:23:10", 
      "scantime":"2020-09-26 13:37:44"
   }
```





### Optional use OpenMQTTGateway

https://github.com/1technophile/OpenMQTTGateway
https://github.com/1technophile/OpenMQTTGateway/issues/760

**### Example for data payload from OpenMQTTGateway**

`MQTT TOPIC: tele/BTtoMQTT/5CCAD34CEE74`

PAYLOAD : 

```json
   {  "id":"5C:CA:D3:4C:EE:74",
      "name":"MIBFS",
      "manufacturerdata":"57015ccad34cee74",
      "rssi":-68,
      "distance":2.799256,
      "model":"XMTZC05HM",
       "measured":70.5,
       "impedance":485,
       "unit":"kg",
       "user":"7",
       "calcweight":141,
       "scantime":"2020-09-26 16:26:15"
   }
```
