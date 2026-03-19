# Object storing must have libraries in the programs generated

HEADER_CATEGORIES = {
    "standard": [
        "stdio.h", "stdlib.h", "string.h", "stdbool.h", "stdint.h",
        "time.h", "signal.h", "math.h", "limits.h", "ctype.h", "errno.h"
    ],
    "filesystem": [
        "unistd.h", "fcntl.h", "sys/types.h", "sys/stat.h", "dirent.h",
        "sys/mman.h", "sys/wait.h", "sys/inotify.h"
    ],
    "gpio_wiringpi": [
        "wiringPi.h", "softPwm.h", "lcd.h", "mcp23017.h", "pcf8591.h",
        "wiringPiSPI.h", "wiringPiI2C.h", "wiringSerial.h", "bcm_host.h",
        "pigpio.h", "pigpio_if2.h", "bcm2835.h"
    ],
    "serial_device_io": [
        "sys/ioctl.h", "termios.h", "linux/serial.h", "linux/i2c-dev.h", "linux/spi/spidev.h", "spidev.h"
    ],
    "camera_image": [
        "opencv2/core/core_c.h", "opencv2/highgui/highgui_c.h", "opencv2/imgproc/imgproc_c.h",
        "opencv2/imgcodecs/imgcodecs.h", "opencv2/videoio/videoio_c.h", "turbojpeg.h", 
        "libavcodec/avcodec.h", "libavutil/imgutils.h", "libavutil/opt.h", "libavutil/time.h", "swscale/swscale.h"
    ],
    "mqtt_amqp": [
        "mosquitto.h", "MQTTClient.h", "paho-mqtt/MQTTClient.h",
        "amqp.h", "amqp_tcp_socket.h", "amqp_framing.h",
        "rabbitmq-c/amqp.h", "rabbitmq-c/tcp_socket.h", "paho-mqtt3as.h"
    ],
    "networking": [
        "sys/socket.h", "netinet/in.h", "arpa/inet.h", "netdb.h", 
        "net/if.h", "ifaddrs.h", "sys/un.h", "sys/select.h", 
        "sys/time.h", "poll.h"
    ],
    "encryption_security": [
        "openssl/conf.h", "openssl/err.h", "openssl/evp.h", "openssl/ssl.h"
    ],
    "http_web": [
        "microhttpd.h", "libwebsockets.h"
    ],
    "data_parsing_json": [
        "cJSON.h"
    ],
    "threads_sync": [
        "pthread.h", "semaphore.h"
    ],
    "logging": [
        "syslog.h", "sys/resource.h"
    ],
    "message_queue_ipc": [
        "sys/ipc.h", "sys/msg.h", "mqueue.h", "sys/shm.h", "sys/timerfd.h", "sys/signalfd.h"
    ],
    "misc_system": [
        "assert.h", "stdarg.h", "locale.h", "getopt.h", "sys/utsname.h",
        "xf86drm.h", "xf86drmMode.h", "gbm.h"
    ]
}
