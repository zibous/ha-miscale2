#include <Arduino.h>

// Scale Mac Address (lower!)
// If you don't know it, you can scan with serial debugging
// enabled and uncomment the lines to print out everything you find
// You should use the scale while this is running
#define scale_mac_addr "5c:ca:d3:4c:ee:74"


// network details
const char *ssid = "wlan1";
const char *password = "theSecretOne";


// MQTT Details
const char *mqtt_server = "localhost";
const int mqtt_port = 1883;
const char *mqtt_userName = "miscale";
const char *mqtt_userPass = "mqttPass2;o";
const char *clientId = "esp32_";

String base_topic = "bodyscale";

const char *mqtt_command = "cmnd/";
const char *mqtt_stat = "tele/";
const char *mqtt_attributes = "/measurement";
const char *mqtt_telemetry = "tele/";
const char *mqtt_tele_status = "/status";

const char *mqtt_tele_lwt = "/LWT";
const char *lwt_message = "offline";

