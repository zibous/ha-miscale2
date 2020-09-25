/*********
 * ESP32 Xiaomi Body Scale to MQTT/AppDaemon bridge
 * The ESP32 scans BLE for the scale and posts it 
 * to an MQTT topic when found.
 *
 * Uses the formulas and processing from
 * https://github.com/lolouk44/xiaomi_mi_scale
*********/

#include <Arduino.h>
#include <ArduinoJson.h>
#include <BLEAdvertisedDevice.h>
#include <BLEDevice.h>
#include <BLEScan.h>
#include <BLEUtils.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <WiFiUdp.h>

#include "config.h"

#define appversion "1.0.0"


String mqtt_clientId = String(clientId + base_topic);                                  //esp32_bodyscale
String mqtt_topic_subscribe = String(mqtt_command + base_topic);                       //cmnd/bodyscale
String mqtt_topic_telemetry = String(mqtt_telemetry + base_topic + mqtt_tele_status);  //tele/bodyscale/status
String mqtt_topic_attributes = String(mqtt_stat + base_topic + mqtt_attributes);       //tele/bodyscale/measurement
String mqtt_topic_lwt = String(mqtt_stat + base_topic + mqtt_tele_lwt);                //tele/bodyscale/LWT

uint32_t unMillis = 1000;
uint64_t unNextTime = 0;

String publish_data;
String lastTimestamp = "1900-01-01 00:00:00";

WiFiClient espClient;
PubSubClient mqtt_client(espClient);

const int wdtTimeout = 1000000;  //time in ms to trigger the watchdog
hw_timer_t *timer = NULL;

uint8_t unNoImpedanceCount = 0;

void IRAM_ATTR resetModule() {
    ets_printf("reboot due to watchdog timeout\n");
    esp_restart();
}

int16_t stoi(String input, uint16_t index1) {
    return (int16_t)(strtol(input.substring(index1, index1 + 2).c_str(), NULL, 16));
}

int16_t stoi2(String input, uint16_t index1) {
    // We can print out all the stuff we find...
    // Serial.print("Substring : ");
    // Serial.println((input.substring(index1 + 2, index1 + 4) + input.substring(index1, index1 + 2)).c_str());
    return (int16_t)(strtol((input.substring(index1 + 2, index1 + 4) + input.substring(index1, index1 + 2)).c_str(), NULL, 16));
}

// MQTT Callback if we need to receive stuff
void callback(char *topic, byte *payload, unsigned int length) {
    Serial.print("MQTT Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    // Copy payload into message buffer
    char message[length + 1];
    for (int i = 0; i < length; i++) {
        message[i] = (char)payload[i];
    }

    message[length] = '\0';

    if (strcmp(topic, mqtt_topic_subscribe.c_str()) == 0) {  //if the incoming message is on the command topic...
        // Parse message into JSON

        const size_t bufferSize = JSON_OBJECT_SIZE(6);
        DynamicJsonDocument jsonBuffer(bufferSize);

        auto error = deserializeJson(jsonBuffer, message);

        if (error) {
            mqtt_client.publish(mqtt_topic_telemetry.c_str(), "!root.success(): invalid JSON on ...");
            return;
        }

        JsonObject root = jsonBuffer.as<JsonObject>();

        if (root.containsKey("reset")) {
            int reset = root["reset"];
            if (reset > 0) {
                Serial.print("Resetting...");
                mqtt_client.publish(mqtt_topic_telemetry.c_str(), "Resetting by Request");
                delay(500);
                esp_restart();
            }
        }
    }
}  //end callback

void connectWifi() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println();
        Serial.print("Connecting to ");
        Serial.println(ssid);

        // WiFi.config(ip, gateway, subnet);

        WiFi.mode(WIFI_STA);
        WiFi.begin(ssid, password);
        WiFi.waitForConnectResult();

        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());

        // WiFi.config(ip, gateway, subnet);

        while (WiFi.status() != WL_CONNECTED) {
            delay(500);
            Serial.print(".");
        }
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

// wifi/MQTT needs to connect each time we get new BLE scan data
// as wifi and ble appear to work best when mutually exclusive
void reconnect() {
    int nFailCount = 0;

    if (WiFi.status() != WL_CONNECTED)
        connectWifi();

    // Loop until we're reconnected
    while (!mqtt_client.connected()) {
        Serial.print("Attempting MQTT connection...");

        mqtt_client.setServer(mqtt_server, mqtt_port);

        // Attempt to connect
        // client.connect(dev_hash,mqtt_username,mqtt_password,mqtt_topic_lwt,0,true,lwt_message)

        if (mqtt_client.connect(mqtt_clientId.c_str(), mqtt_userName, mqtt_userPass, mqtt_topic_lwt.c_str(), 0, true, lwt_message)) {
            Serial.println("connected");

            //once connected to MQTT broker, subscribe to our command topic
            bool bSubscribed = false;

            while (!bSubscribed) {
                bSubscribed = mqtt_client.subscribe(mqtt_topic_subscribe.c_str());
            }

            mqtt_client.setCallback(callback);
            mqtt_client.loop();
        } else {
            Serial.print("failed, rc=");
            Serial.print(mqtt_client.state());
            Serial.println(" try again in 200 milliseconds");
            delay(200);
            nFailCount++;
            if (nFailCount > 500)
                esp_restart();
        }
    }
}  //end reconnect()

void publish() {
    if (!mqtt_client.connected()) {
        Serial.println("");
        Serial.println("Attemping Reconnect.");
        reconnect();
    }

    mqtt_client.publish(mqtt_topic_attributes.c_str(), publish_data.c_str(), true);

    Serial.print("Publishing : ");
    Serial.println(publish_data.c_str());
    Serial.print("to : ");
    Serial.println(mqtt_topic_attributes.c_str());

    delay(2000);
}

class MyAdvertisedDeviceCallbacks : public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice) {
        Serial.printf("Advertised Device: %s \n", advertisedDevice.toString().c_str());
        Serial.printf("Mac Address : %s \n", advertisedDevice.getAddress().toString().c_str());

        if (advertisedDevice.getAddress().toString() == scale_mac_addr) {
            BLEScan *pBLEScan = BLEDevice::getScan();  // found what we want, stop now
            pBLEScan->stop();
        }
        // We can print out all the stuff we find...
        // Serial.printf("Service Data : %s\n", advertisedDevice.getServiceData().c_str() );
        // Serial.printf("Service Data UUID : %s\n", advertisedDevice.getServiceDataUUID() );
    }
};

void bodyScaleDevice(BLEAdvertisedDevice d) {

    Serial.println("");
    Serial.println("NEW DATA -----------------------------------------");
    String hex;

    if (d.haveServiceData()) {
        std::string md = d.getServiceData();
        uint8_t *mdp = (uint8_t *)d.getServiceData().data();
        char *pHex = BLEUtils::buildHexData(nullptr, mdp, md.length());
        hex = pHex;

        Serial.print("\thex:");
        Serial.println(hex);

        Serial.print("\tphex:");
        Serial.println(pHex);

        Serial.print("\t22:");
        Serial.println(stoi2(hex, 22));

        free(pHex);

        // Controlbyte:Substring : 07e4
        Serial.print("\tControlbyte:");
        Serial.println(stoi2(hex, 4));
    }

    // get the impedance
    float impedance = stoi2(hex, 18);  // * 0.01f * 100;

    if (unNoImpedanceCount < 3 && impedance == 0) {
        unNextTime = millis() + (10 * unMillis);
        unNoImpedanceCount++;
        Serial.println("\tReading incomplete, reattempting");
        return;
    }

    unNoImpedanceCount = 0;

    // get the data
    float measured = stoi2(hex, 22) * 0.01f;
    float weight = stoi2(hex, 22) * 0.01f;
    int user = stoi(hex, 6);
    int units = stoi(hex, 0);

    // decode the units and recalc the weight based on the unit
    String strUnits;
    if (units == 1) {
        // Chinese Catty
        strUnits = "jin";
        weight = weight * 0.50 * 0.50;
    } else if (units == 2) {
        //  MKS kg
        strUnits = "kg";
        weight = weight * 0.50;
    } else if (units == 3) {
        // Imperial pound
        weight = weight * 0.4536;
        strUnits = "lbs";
    }

    String time = String(String(stoi2(hex, 4)) + "-" + String(stoi(hex, 8)) + "-" + String(stoi(hex, 10)) + " " + String(stoi(hex, 12)) + ":" + String(stoi(hex, 14)) + ":" + String(stoi(hex, 16)));

    // Currently we just send the raw values over and let appdaemon figure out the rest...
    if (weight > 0 and impedance > 0 and lastTimestamp != time) {
        lastTimestamp = time;

        publish_data = String("{\"weight\": ");
        publish_data += String(weight);
        publish_data += String(", \"measured\": ");
        publish_data += String(measured);
        publish_data += String(", \"impedance\": ");
        publish_data += String(int(impedance));
        publish_data += String(", \"units\":\"");
        publish_data += String(strUnits);
        publish_data += String("\", \"user\":\"");
        publish_data += String(user);
        publish_data += String("\", \"device\":\"");
        publish_data += String(scale_mac_addr);
        publish_data += String("\", \"version\":\"");
        publish_data += String(appversion);
        publish_data += String("\", \"timestamp\":\"");
        publish_data += time;
        publish_data += String("\"}");

        // --------------------------------------------
        // publish the scale data
        // --------------------------------------------

        // Payload: {
        //            "weight": 70.50,
        //            "measured": 141.00,
        //            "impedance": 460,
        //            "units":"kg",
        //            "user":"7",
        //            "device":"5c:ca:d3:4c:ee:74",
        //            "version":"1.0.0",
        //            "timestamp":"2020-9-24 17:17:6"
        //           }
        // to : tele/bodyscale/measurement/7

        String tele_user = "/" + String(user);
        mqtt_topic_attributes = String(mqtt_stat + base_topic + mqtt_attributes + tele_user);
        publish();

        // Got a reading, we can time out for a bit (5 minutes)
        unNextTime = millis() + (5 * 60 * unMillis);
    }
}

void ScanBLE() {
    // Scan often unless we find a reading
    unNextTime = millis() + (30 * unMillis);

    Serial.println("Starting BLE Scan");
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("Disconnecting From MQTT.");
        mqtt_client.disconnect();
        delay(1000);
        Serial.println("Disconnecting WiFi");
        WiFi.disconnect();
        delay(1000);
    }

    BLEDevice::init("");

    BLEScan *pBLEScan = BLEDevice::getScan();  //create new scan
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
    pBLEScan->setActiveScan(true);  //active scan uses more power, but get results faster
    pBLEScan->setInterval(0x50);
    pBLEScan->setWindow(0x30);

    // Scan for 30 seconds.
    BLEScanResults foundDevices = pBLEScan->start(30);

    int count = foundDevices.getCount();

    for (int i = 0; i < count; i++) {
        BLEAdvertisedDevice d = foundDevices.getDevice(i);

        if (d.getAddress().toString() != scale_mac_addr)
            continue;

        Serial.println("");
        Serial.println("NEW DATA -----------------------------------------");
        String hex;

        if (d.haveServiceData()) {
            std::string md = d.getServiceData();
            uint8_t *mdp = (uint8_t *)d.getServiceData().data();
            char *pHex = BLEUtils::buildHexData(nullptr, mdp, md.length());
            hex = pHex;

            Serial.print("\thex:");
            Serial.println(hex);

            Serial.print("\tphex:");
            Serial.println(pHex);

            Serial.print("\t22:");
            Serial.println(stoi2(hex, 22));

            free(pHex);

            // Controlbyte:Substring : 07e4
            Serial.print("\tControlbyte:");
            Serial.println(stoi2(hex, 4));
        }

        // get the impedance
        float impedance = stoi2(hex, 18);  // * 0.01f * 100;

        if (unNoImpedanceCount < 3 && impedance == 0) {
            unNextTime = millis() + (10 * unMillis);
            unNoImpedanceCount++;
            Serial.println("\tReading incomplete, reattempting");
            return;
        }

        unNoImpedanceCount = 0;

        // get the data
        float measured = stoi2(hex, 22) * 0.01f;
        float weight = stoi2(hex, 22) * 0.01f;
        int user = stoi(hex, 6);
        int units = stoi(hex, 0);

        // decode the units and recalc the weight based on the unit
        String strUnits;
        if (units == 1) {
            // Chinese Catty
            strUnits = "jin";
            weight = weight * 0.50 * 0.50;
        } else if (units == 2) {
            //  MKS kg
            strUnits = "kg";
            weight = weight * 0.50;
        } else if (units == 3) {
            // Imperial pound
            weight = weight * 0.4536;
            strUnits = "lbs";
        }

        String time = String(String(stoi2(hex, 4)) + "-" + String(stoi(hex, 8)) + "-" + String(stoi(hex, 10)) + " " + String(stoi(hex, 12)) + ":" + String(stoi(hex, 14)) + ":" + String(stoi(hex, 16)));

        // Currently we just send the raw values over and let appdaemon figure out the rest...
        if (weight > 0 and impedance > 0 and lastTimestamp != time) {
            lastTimestamp = time;

            publish_data = String("{\"weight\": ");
            publish_data += String(weight);
            publish_data += String(", \"measured\": ");
            publish_data += String(measured);
            publish_data += String(", \"impedance\": ");
            publish_data += String(int(impedance));
            publish_data += String(", \"units\":\"");
            publish_data += String(strUnits);
            publish_data += String("\", \"user\":\"");
            publish_data += String(user);
            publish_data += String("\", \"device\":\"");
            publish_data += String(scale_mac_addr);
            publish_data += String("\", \"version\":\"");
            publish_data += String(appversion);
            publish_data += String("\", \"timestamp\":\"");
            publish_data += time;
            publish_data += String("\"}");

            // --------------------------------------------
            // publish the scale data
            // --------------------------------------------

            // Payload: {
            //            "weight": 70.50,
            //            "measured": 141.00,
            //            "impedance": 460,
            //            "units":"kg",
            //            "user":"7",
            //            "device":"5c:ca:d3:4c:ee:74",
            //            "version":"1.0.0",
            //            "timestamp":"2020-9-24 17:17:6"
            //           }
            // to : tele/bodyscale/measurement/7

            String tele_user = "/" + String(user);
            mqtt_topic_attributes = String(mqtt_stat + base_topic + mqtt_attributes + tele_user);
            publish();

            // Got a reading, we can time out for a bit (5 minutes)
            unNextTime = millis() + (5 * 60 * unMillis);
        }
    }
    Serial.println("Finished BLE Scan");
}

void setup() {
    // Initializing serial port for debugging purposes
    Serial.begin(115200);
    delay(10);
    Serial.println(" ");

    connectWifi();

    // setup watchdog timer - shouldn't be necessary but just incase
    timer = timerBegin(0, 80, true);                   //timer 0, div 80
    timerAttachInterrupt(timer, &resetModule, true);   //attach callback
    timerAlarmWrite(timer, wdtTimeout * 1000, false);  //set time in us
    timerAlarmEnable(timer);                           //enable interrupt
    timerWrite(timer, 0);                              //reset timer (feed watchdog)

    Serial.println("Setup Finished.");
    ScanBLE();
}

// runs over and over again
void loop() {
    timerWrite(timer, 0);  //reset timer (feed watchdog)

    uint64_t time = millis();

    // We could deepsleep, but we're scanning fairly frequently...
    if (time > unNextTime) {
        ScanBLE();
        Serial.println("Waiting for next Scan");
    }

    // Shouldn't bee necessary to restart, but we'll do so every 12 hours
    // just to keep things like our timers from losing precision
    if (time > (12 * 60 * 60 * unMillis)) {
        Serial.println("Doing Periodic Restart");
        delay(500);
        esp_restart();
    }

    // Don't need to spin too hard...
    delay(1000);
}
