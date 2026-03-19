import re
from config.model import RPI_PICO

# Disallowed header patterns with reasons
RESTRICTED_HEADERS = {
    "jsmn.h": "custom library (jsmn.h) should not be used",
    "interface/mmal/mmal.h": "MMAL is deprecated and should not be used",
    "lws_server.h": "lws_server.h is non-existent",
    "mqtt_client.c": "mqtt_client.c is not a valid header",
    "mcp3008.h": "mcp3008.h is non-existent",
    "mcp3008.c": "mcp3008.c is not a valid header",
    "paho-mqtt3as.h": "paho-mqtt3as.h is non-existent",
    "pigpiod_if2.h": "pigpiod_if2.h should not be used",
    "pigpio_if2.h": "pigpio_if2.h is non-existent",
    "config.h": "config.h is non-existent",
    "wiringPiPWM.h": "wiringPiPWM.h is non-existent",
    "cJSON.h": "use <cjson/CJSON.h> instead of <cJSON.h>",
    "rabbitmq-c/amqp.h": "use <amqp.h> instead",
    "vl53l1x.h": "vl53l1x.h is non-existent",
    "vl53l1x_api.h": "vl53l1x_api.h is non-existent",
    "libjpeg/jpeglib.h": "use <jpeglib.h> instead of <libjpeg/jpeglib.h>",
    "oled.h": "oled.h is non-existent",
    "oled.c": "oled.c is not a valid header",
    "dht11.h": "custom or unavailable (dht11.h)",
    "lwip/init.h": "lwip/init.h is not available",
    "socket.h": "use <sys/socket.h> instead of <socket.h>",
    "ws2812spi.h": "ws2812spi.h is non-existent",
    "sensor.h": "sensor.h is non-existent",
    "paho-mqtt/MQTTClient.h": "may require redirection or update if misused",
    "ws2812b.h": "ws2812b.h is non-existent",
    "ws2811.h": "ws2811.h is non-existent",
    "ws2811/ws2811.h": "ws2811/ws2811.h is not allowed",
    "dht22.h": "dht22.h is non-existent",
    "VL53L1X.h": "VL53L1X.h is non-existent",
    "systemd/sd-daemon.h": "not portable",
    "ws2812.h": "ws2812.h is non-existent",
    "mcp3008spi.h": "mcp3008spi.h is non-existent",
    "mqtt3a.h": "mqtt3a.h is not found",
    "rpi_ws281x/ws2811.h": "rpi_ws281x/ws2811.h is not allowed",
    "bme68x.h": "bme68x.h is non-standard",
    "paho-mqtt3c/MQTTClient.h": "use <paho-mqtt/MQTTClient.h> instead",
    "paho-mqtt3a/MQTTClient.h": "use <paho-mqtt/MQTTClient.h> instead",
    "dht22Lib.h": "dht22Lib.h is non-existent",
    "dhtreader.h": "dhtreader.h is non-existent",
    "i2c.h": "i2c.h is non-existent",
    "ssd1306_i2c.h": "ssd1306_i2c.h is non-existent",
    "hmc5883l_calibration.h": "custom library, not available",
    "libgpiod.h": "libgpiod.h should not be used",
    "lwip/netconn.h": "lwip/netconn.h is unavailable",
    "opencv/cv.h": "OpenCV is C++ only, not valid in plain C",
    "libcamera/libcamera.h": "libcamera is C++, not usable in C"
}

if not RPI_PICO:
    RESTRICTED_HEADERS.update({
    "pico/stdlib.h": "pico SDK headers not suitable for Pi OS",
    "hardware/adc.h": "hardware/adc.h is for Pico SDK",
})


# Non-header patterns to reject (e.g., libcamera, OpenCV, pkg-config)
RESTRICTED_PATTERNS = {
    r"libcamera/libcamera\.h": "libcamera is not supported in plain C",
    r"\bopencv\b": "OpenCV references are not supported in C",
    r"opencv/cv\.h": "cv.h is deprecated and incompatible with C-only projects",
    r"\bcv\.h\b": "cv.h is deprecated and incompatible with C-only projects",
    r"pkg-config\s+--cflags\s+--libs\s+opencv": "pkg-config for OpenCV suggests C++ usage",
    r"\bg\+\+\b": "G++ indicates C++ code, not valid for plain C pipeline",
}


def check_restricted_headers_and_patterns(code: str) -> list[tuple[str, str]]:
    """
    Checks C code for restricted headers and forbidden pattern usage.
    Returns a list of (match, reason) for any violations found.
    """
    violations = []

    # Check for disallowed includes
    for header, reason in RESTRICTED_HEADERS.items():
        pattern = rf'#include\s*[<"]{re.escape(header)}[>"]'
        if re.search(pattern, code):
            violations.append((header, reason))

    # Check for restricted usage patterns (OpenCV, libcamera, g++, etc.)
    for pattern, reason in RESTRICTED_PATTERNS.items():
        if re.search(pattern, code):
            violations.append((pattern, reason))

    return violations
