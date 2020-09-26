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
#include "time.h"
#define appversion "1.0.4"

String mqtt_clientId = String(clientId + base_topic);                                  //esp32_bodyscale
String mqtt_topic_subscribe = String(mqtt_command + base_topic);                       //cmnd/bodyscale
String mqtt_topic_telemetry = String(mqtt_telemetry + base_topic + mqtt_tele_status);  //tele/bodyscale/status
String mqtt_topic_attributes = String(mqtt_stat + base_topic + mqtt_attributes);       //tele/bodyscale/measurement
String mqtt_topic_lwt = String(mqtt_stat + base_topic + mqtt_tele_lwt);                //tele/bodyscale/LWT

uint32_t unMillis = 1000;
uint64_t unNextTime = 0;

String publish_data;
String lastTimestamp = "1900-01-01 00:00:00";
String timestamp = lastTimestamp;

WiFiClient espClient;
PubSubClient mqtt_client(espClient);

const int wdtTimeout = 1000000;  //time in ms to trigger the watchdog
hw_timer_t *timer = NULL;

uint8_t unNoImpedanceCount = 0;

// ntp server
// see: https://lastminuteengineers.com/esp32-ntp-server-date-time-tutorial/
const char *ntpServer = "europe.pool.ntp.org";
// For UTC +1.00 : 1 * 60 * 60 : 3600
const long gmtOffset_sec = 3600;
const int daylightOffset_sec = 0;  // no daylightOffset !

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

void setTimestamp() {
    time_t rawtime;
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
        Serial.println("Failed to obtain time");
        return;
    }
    char timeStringBuff[50];  //50 chars should be enough
    // strftime(timeStringBuff, sizeof(timeStringBuff), "%A, %B %d %Y %H:%M:%S", &timeinfo);
    strftime(timeStringBuff, sizeof(timeStringBuff), "%Y-%m-%d %H:%M:%S", &timeinfo);
    // print like "const char*"
    // Serial.println(timeStringBuff);
    //Optional: Construct String object
    String asString(timeStringBuff);
    timestamp = String(timeStringBuff);
}

void printLocalTime() {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
        Serial.println("Failed to obtain time");
        return;
    }
    Serial.println(&timeinfo, "%Y-%m-%d %H:%M:%S");

    // Serial.print("Day of week: ");
    // Serial.println(&timeinfo, "%A");
    // Serial.print("Month: ");
    // Serial.println(&timeinfo, "%B");
    // Serial.print("Day of Month: ");
    // Serial.println(&timeinfo, "%d");
    // Serial.print("Year: ");
    // Serial.println(&timeinfo, "%Y");
    // Serial.print("Hour: ");
    // Serial.println(&timeinfo, "%H");
    // Serial.print("Hour (12 hour format): ");
    // Serial.println(&timeinfo, "%I");
    // Serial.print("Minute: ");
    // Serial.println(&timeinfo, "%M");
    // Serial.print("Second: ");
    // Serial.println(&timeinfo, "%S");

    // Serial.println("Time variables");
    // char timeHour[3];
    // strftime(timeHour, 3, "%H", &timeinfo);
    // Serial.println(timeHour);
    // char timeWeekDay[10];
    // strftime(timeWeekDay, 10, "%A", &timeinfo);
    // Serial.println(timeWeekDay);
    Serial.println();
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

        WiFi.mode(WIFI_STA);
        WiFi.begin(ssid, password);
        WiFi.waitForConnectResult();

        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());

        while (WiFi.status() != WL_CONNECTED) {
            delay(500);
            Serial.print(".");
        }

        configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
    }

    printLocalTime();
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

            mqtt_client.setBufferSize(1024);

            //once connected to MQTT broker, subscribe to our command topic
            bool bSubscribed = false;

            while (!bSubscribed) {
                bSubscribed = mqtt_client.subscribe(mqtt_topic_subscribe.c_str());
            }

            String lwtState = "Online";
            mqtt_client.publish(mqtt_topic_lwt.c_str(), lwtState.c_str(), true);

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

    if (mqtt_client.connected()) {
        Serial.print(mqtt_topic_attributes.c_str());
        Serial.print(":");
        Serial.print(publish_data.c_str());
        Serial.println("");
        mqtt_client.publish(mqtt_topic_attributes.c_str(), publish_data.c_str(), true);
    } else {
        Serial.print("ERROR: No Connection to ");
        Serial.println(mqtt_server);
    }

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
        String hex;

        if (d.haveServiceData()) {
            std::string md = d.getServiceData();
            uint8_t *mdp = (uint8_t *)d.getServiceData().data();
            char *pHex = BLEUtils::buildHexData(nullptr, mdp, md.length());
            hex = pHex;

            setTimestamp();
            Serial.println(" ");
            Serial.print("Scanning for new data:");
            Serial.println(timestamp);
            Serial.print("\thex:");
            Serial.println(hex);

            Serial.print("\tphex:");
            Serial.println(pHex);

            Serial.print("\t22:");
            Serial.println(stoi2(hex, 22));

            free(pHex);

            // Controlbyte:Substring : 07e4
            int controlByte = stoi2(hex, 4);
            Serial.print("\tControlbyte:");
            Serial.println(controlByte);
            int isWeightRemoved = controlByte & (1 << 7);
            bool isStabilized = controlByte & (1 << 5) != 0;
            Serial.print("\tWeightRemoved:");
            Serial.println(isWeightRemoved);
            Serial.print("\tStabilized:");
            Serial.println(isStabilized);
            if (!isStabilized and isWeightRemoved) {
                Serial.println("\tNot stabilized, skip and wait for the next one....");
                // return;
            }                
            
        }else{
            return;
        }

        // get the impedance
        float impedance = stoi2(hex, 18);  // * 0.01f * 100;
        int sequence =  stoi(hex, 8);
        Serial.print("\tSequence: ");
        Serial.println(sequence);

        if (unNoImpedanceCount < 3 && impedance == 0) {
            unNextTime = millis() + (10 * unMillis);
            unNoImpedanceCount++;
            Serial.println("\tReading incomplete, reattempting");
            return;
        }

        unNoImpedanceCount = 0;

        // get the data weight, user and units
        float measured = stoi2(hex, 22) * 0.01f;
        float weight = measured;
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

        char dt[32];
        sprintf(dt, "%s-%02d-%02d %02d:%02d:%02d", String(stoi2(hex, 4)), stoi(hex, 8), stoi(hex, 10), stoi(hex, 12), stoi(hex, 14), stoi(hex, 16));
        String scaleTime = String(dt);

        Serial.print("\tLastTimestamp:");
        Serial.println(lastTimestamp);

        Serial.print("\tScaleTime:");
        Serial.println(scaleTime);

        // Currently we just send the raw values over and mqqt service figure out the rest...
        if (weight > 0 and impedance > 0 and lastTimestamp != scaleTime) {
            // publish only if we have new weight, impedance and a new scan
            setTimestamp();
            publish_data = String("{\"measured\": ");
            publish_data += String(weight);
            publish_data += String(", \"calcweight\": ");
            publish_data += String(measured);
            publish_data += String(", \"impedance\": ");
            publish_data += String(int(impedance));
            publish_data += String(", \"unit\":\"");
            publish_data += String(strUnits);
            publish_data += String("\", \"user\":\"");
            publish_data += String(user);
            publish_data += String("\", \"id\":\"");
            publish_data += String(scale_mac_addr);
            publish_data += String("\", \"version\":\"");
            publish_data += String(appversion);
            publish_data += String("\", \"timestamp\":\"");
            publish_data += timestamp;
            publish_data += String("\", \"lastscan\":\"");
            publish_data += lastTimestamp;
            publish_data += String("\", \"scantime\":\"");
            publish_data += scaleTime;
            publish_data += String("\"}");

            // --------------------------------------------
            // publish the scale data
            // --------------------------------------------
            lastTimestamp = String(scaleTime);

            Serial.print("\tPublishing Data:");
            Serial.println(timestamp);
            publish();
            Serial.println(" ");
            
        }
        // Got a reading, we can time out for a bit (... minutes)
        unNextTime = millis() + (60 * unMillis);
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
