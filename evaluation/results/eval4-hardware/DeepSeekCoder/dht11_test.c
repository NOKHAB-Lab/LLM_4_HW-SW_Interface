#include <stdio.h>
#include <pigpio.h>
#include <unistd.h>
#include <time.h>

#define DHT11_GPIO 7

int read_dht11(int gpio, int *temp, int *hum) {
    uint8_t data[5] = {0};
    int lastState = PI_HIGH;
    int bitIdx = 0;

    gpioSetMode(gpio, PI_OUTPUT);
    gpioWrite(gpio, PI_LOW);
    gpioDelay(18000); // 18ms
    gpioWrite(gpio, PI_HIGH);
    gpioDelay(30);    // 30us
    gpioSetMode(gpio, PI_INPUT);

    for (int i = 0; i < 85; i++) {
        int count = 0;
        while (gpioRead(gpio) == lastState) {
            count++;
            gpioDelay(1);
            if (count >= 255) break;
        }
        lastState = gpioRead(gpio);

        if (i >= 4 && i % 2 == 0) {
            data[bitIdx / 8] <<= 1;
            if (count > 40)
                data[bitIdx / 8] |= 1;
            bitIdx++;
        }
    }

    if (bitIdx >= 40 && ((data[0] + data[1] + data[2] + data[3]) & 0xFF) == data[4]) {
        *hum = data[0];
        *temp = data[2];
        return 0;
    } else {
        return -1;
    }
}

void print_timestamp() {
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    char buffer[30];
    strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", t);
    printf("[%s] ", buffer);
}

int main() {
    if (gpioInitialise() < 0) {
        fprintf(stderr, "Failed to initialize pigpio.\n");
        return 1;
    }

    printf("Starting periodic DHT11 read every 5 seconds...\n");

    while (1) {
        int temp = 0, hum = 0;
        int result = read_dht11(DHT11_GPIO, &temp, &hum);

        print_timestamp();
        if (result == 0 && (temp > 0 || hum > 0)) {
            printf("Temperature: %d°C, Humidity: %d%%\n", temp, hum);
        } else {
            printf("Sensor read failed or returned 0 values. Retrying in next cycle...\n");
        }

        sleep(5);
    }

    gpioTerminate();
    return 0;
}
