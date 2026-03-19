#include <stdio.h>
#include <pigpio.h>
#include <unistd.h>

#define BUZZER_GPIO 18     // GPIO 18 = Physical Pin 12
#define TONE_FREQUENCY 1000 // Hz
#define DURATION_MS 500     // 0.5 second

int main() {
    if (gpioInitialise() < 0) {
        fprintf(stderr, "pigpio init failed\n");
        return 1;
    }

    printf("Starting buzzer loop: 0.5s buzz every 2 seconds...\n");

    while (1) {
        // Start tone using hardware PWM
        gpioHardwarePWM(BUZZER_GPIO, TONE_FREQUENCY, 500000); // 50% duty

        // Keep tone on for 0.5 seconds
        usleep(DURATION_MS * 1000);

        // Stop tone
        gpioHardwarePWM(BUZZER_GPIO, 0, 0);

        // Wait for remaining time (2s - 0.5s = 1.5s)
        sleep(2);
    }

    gpioTerminate();
    return 0;
}
