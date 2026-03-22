import json
import argparse
from collections import defaultdict, Counter

# ---------- CONFIGURABLE SETUP ----------

PI_MODELS = [
    "Raspberry Pi 4 Model B",
    "Raspberry Pi 3 Model B+",
    "Raspberry Pi Zero W",
    "Raspberry Pi 5"
]

USE_CONTEXTS = [
    "educational setting", "hobbyist project", "professional monitoring system",
    "research application", "industrial automation", "smart agriculture",
    "robotics project", "wearable technology", "interactive art installation",
    "assistive technology", "environmental science", "home automation", "motion-triggered surveillance",
    "biometric authentication system", "tamper detection system", "entry access logging",
    "threat detection node", "sensor fusion testing", "drone navigation", "aircraft monitoring",
    "vehicle telemetry", "biomedical instrumentation", "real-time health monitoring",
    "remote patient diagnostics", "prosthetic device control", "automated quality control",
    "embedded safety systems", "predictive maintenance", "smart grid management"
]

# Example CATEGORIES (only a subset for brevity; insert full CATEGORIES if needed)
CATEGORIES = {
    "sensor_reading": [
        "temperature sensor", "humidity sensor", "pressure sensor", "light sensor",
        "ultrasonic sensor", "PIR sensor", "soil moisture sensor", "IR sensor",
        "sound sensor", "vibration sensor", "gas sensor", "touch sensor",
        "hall effect sensor", "rain sensor", "water flow sensor", "tilt sensor",
        "flame sensor", "color sensor", "capacitive touch sensor",
        "weight/load cell sensor", "motion sensor", "alcohol sensor",
        "gyroscope sensor", "accelerometer", "magnetometer", "time of flight sensor"
    ],

    # ⚙️ Actuator Options (standalone)
    "actuators": [
        "servo motor", "DC motor", "stepper motor", "relay", "solenoid",
        "LED", "buzzer", "speaker", "vibration motor", "fan", "LCD display",
        "OLED screen", "RGB LED", "relay-controlled lamp", "heater", "cooling fan",
        "valve actuator", "electromagnetic lock", "motor driver"
    ],

    # ⚡ Phase 2: Sensor-Actuator Integration (Expanded)
    "sensor_actuator_combo": [
        "temperature sensor controlling a cooling fan",
        "humidity sensor triggering a dehumidifier",
        "PIR motion sensor activating a light or buzzer",
        "ultrasonic sensor controlling servo for parking assist",
        "soil moisture sensor turning on a water pump",
        "gas sensor activating a ventilation fan",
        "IR sensor triggering a relay to open a door",
        "sound sensor activating an alarm",
        "light sensor adjusting brightness of an LED strip",
        "load cell sensor triggering a locking mechanism",
        "time of flight sensor controlling a gate",
        "rain sensor closing a motorized window",
        "flame sensor activating buzzer and LED",
        "capacitive touch sensor toggling a relay"
    ],

    # 💾 Phase 3: File and Data Logging (Expanded)
    "file_logging": [
        "log temperature readings to a CSV file",
        "log motion detection timestamps to a text file",
        "log gas sensor values with timestamps",
        "write ultrasonic distance readings to a file every second",
        "create daily sensor log files for multiple sensors",
        "log light and sound levels with date/time",
        "store sensor threshold breaches to a log file",
        "save sensor calibration values to file",
        "record ADC readings from multiple channels into CSV",
        "read configuration threshold values from a JSON file"
    ],

    # 🚨 Phase 4: Interrupts and Real-Time Logic (Expanded)
    "interrupt_driven": [
        "motion sensor using GPIO interrupt to turn on light",
        "button interrupt to start or stop data logging",
        "vibration sensor triggering a shutdown routine",
        "PIR sensor GPIO interrupt activating buzzer",
        "external interrupt from a tilt switch",
        "IR receiver decoding input via interrupt",
        "hardware timer interrupt for consistent sampling",
        "Hall effect sensor rotation counting with interrupt",
        "ultrasonic trigger using echo pin interrupt"
    ],

    "config_management": [
        "load sensor thresholds from JSON file",
        "read WiFi credentials from a config.ini file",
        "parse system limits from a configuration file",
        "write runtime statistics to a JSON log"
    ],

    # 📷 Phase 5: Camera and Image Applications (Expanded)
    # "camera_applications": [
    #     "USB camera capturing image every 10 seconds",
    #     "CSI camera capturing grayscale image and saving",
    #     "detect object presence and capture image",
    #     "apply blur filter to image captured via camera",
    #     "stream camera feed and log frame timestamps",
    #     "time-lapse photography using CSI camera",
    #     "save motion-triggered snapshots from camera",
    #     "capture image and resize to 320x240 before saving",
    #     "capture and convert image to black and white",
    #     "camera capture with filename based on timestamp"
    # ],

    # 📤 Phase 6: Simple Communication and Networking (Expanded)
    "networking": [
        "send temperature sensor data over UDP",
        "receive command over TCP to activate actuator",
        "post humidity readings to a web server using HTTP",
        "subscribe to MQTT topic to get control signals",
        #"send camera image snapshot to server via POST",
        "receive configuration from HTTP API",
        #"stream video frames over MJPEG using TCP socket",
        "broadcast light levels over UDP multicast",
        "fetch thresholds for sensors from a cloud endpoint",
        "stream live sensor data over local web server"
    ],
    "sensor_simple": [
        # 🌡️ Temperature Sensor Variations
        "temperature sensor using I2C",
        "temperature sensor using analog input",
        "temperature sensor using SPI",
        "temperature sensor with ADC",
        "temperature sensor with DAC output",
        "temperature sensor logging to file",
        "temperature sensor triggering alert",

        # 💧 Humidity Sensor Variations
        "humidity sensor using I2C",
        "humidity sensor using digital GPIO",
        "humidity sensor logging values with timestamp",
        "humidity sensor triggering a relay",

        # 📈 Pressure Sensor Variations
        "pressure sensor using I2C",
        "pressure sensor with ADC logging",
        "pressure sensor recording altitude values to file",

        # 🔆 Light Sensor Variations
        "light sensor using analog input",
        "light sensor using I2C",
        "light sensor triggering LED brightness",
        "light sensor logging lux levels to file",

        # 🧠 PIR / Motion Sensors
        "PIR sensor with GPIO read",
        "PIR sensor triggering LED or buzzer",
        "PIR sensor with timestamp logging",

        # 🚰 Soil Moisture Sensor
        "soil moisture sensor using analog input",
        "soil moisture sensor with ADC",
        "soil moisture sensor controlling a water pump",

        # 🛑 IR Sensor
        "IR sensor reading using GPIO",
        "IR sensor activating relay",
        "IR sensor logging object presence",

        # 🔊 Sound Sensor
        "sound sensor using analog input",
        "sound sensor with ADC threshold trigger",
        "sound sensor event logging",

        # 🔁 Gyroscope / Accelerometer
        "accelerometer using I2C",
        "gyroscope using SPI",
        "IMU sensor logging X, Y, Z readings to CSV"
    ],
    "IR and Obstacle Sensors": [
        "SainSmart IR Sensor Obstacle Avoidance",
        "Infrared Reflection Module - TCRT5000",
        "E18-D80NK Infrared Obstacle Avoidance Sensor",
        "E18-D50NK Adjustable 3-50cm IR Sensor",
        "Ultra-Small Infrared Digital Obstacle Avoidance Sensor",
        "4-Way Infrared Tracking Module",
        "3-Way Tracing Sensor / Robot Tracing"
    ],
    "Biometric Sensors": [
        "Silicon Labs Si1143/Si1144 Biometric Optical Sensors",
        "Silicon Labs Si117x Optical Biometric Sensor Family",
        "Silicon Labs Si118x Optical Biometric Sensor Family"
  ],
    "Magnetic Sensors": [
        "Adafruit HMC5883L Triple-Axis Magnetometer",
        "Adafruit LIS3MDL Triple-Axis Magnetometer",
        "Adafruit LSM303DLHC Accelerometer + Magnetometer",
        "Adafruit FXOS8700 6-Axis Accelerometer and Magnetometer",
        "Adafruit MLX90393 Wide-Range Triple-Axis Magnetometer",
        "A3144 Hall Speed Sensor",
        "SainSmart Hall Sensor Module",
        "GY-26 HMC1022 Electronic Compass Module",
        "Analog Devices AD22151 Linear Hall Effect Sensor",
        "Analog Devices ADXRS450 High-Performance Gyroscope",
        "Analog Devices ADXL354 Low Noise Accelerometer",
        "Analog Devices ADIS16060 Digital Gyroscope",
        "Melexis MLX90217 Hall Effect Speed Sensor",
        "Melexis MLX90254 Magnetic Speed Sensor",
        "Melexis MLX91204 Current Sensor",
        "Melexis MLX91208 Current Sensor with Overcurrent Detection",
        "Melexis MLX91209 Hall-based Current Sensor",
        "Melexis MLX91211 Integrated Current Sensor",
        "Melexis MLX91219 Compact Hall-Effect Current Sensor",
        "Silicon Labs Si720x Hall Effect Magnetic Sensor",
        "Silicon Labs Si7210 Hall Effect Magnetic Position Sensor",
        "Silicon Labs Si721x Magnetic Field Sensor Series",
        "Texas Instruments DRV5055 Hall-Effect Sensor",
        "Texas Instruments TMAG5170 3D Hall-Effect Sensor",
        "Texas Instruments DRV5032 Hall-Effect Sensor",
        "Texas Instruments TMAG5110 Hall-Effect Latch",
        "Texas Instruments TMAG5273 3D Linear Hall-Effect Sensor",
        "Texas Instruments DRV5053 Analog Hall-Effect Sensor"
    ],
    "Vibration and Tilt Sensors": [
        "Omron D7S Vibration Sensor",
        "Omron D7E-1 Sealed Vibration Sensor",
        "Omron D7E-2 Sealed Tilt Sensor",
        "Omron D7E-3 Sealed Tilt Sensor",
        "Omron D7E-5 Sealed Tilt Sensor"
    ],
    "Color and Light Sensors": [
        "Omron B5WC Color Sensor",
        "Omron B5W-DB Diffuse Reflective Sensor",
        "Omron B5W-DB11A1-A Diffuse Reflective Sensor",
        "Omron B5W-LB Light Convergent Reflective Sensor",
        "Adafruit TSL2561 Luminosity Sensor",
        "Adafruit BH1750 Light Sensor",
        "Adafruit APDS9960 Proximity, Light, RGB, and Gesture Sensor",
        "Adafruit TCS34725 Color Sensor",
        "Adafruit AS7341 10-Channel Light/Color Sensor",
        "Adafruit VEML7700 Lux Sensor","GY-30 Digital Light Intensity Sensor",
        "TCS3200 Color Sensor Module",
        "GY-31 TCS230 / TCS3200 Color Sensor",
        "UV Sensor - GY-ML8511",
        "Photodiode Sensor Module - LM393",
        "Photoresistor Sensor with Small Plate",
        "Analog Devices ADPD105 Photometric Front End",
        "Analog Devices ADPD188BI Optical Sensor",
        "Analog Devices ADPD2210 Ambient Light Sensor",
        "Analog Devices ADPD2140 Gesture Recognition Sensor",
        "Analog Devices ADPD144RI Red and Infrared Photometric Sensor",
        "Melexis MLX75305 Ambient Light Sensor",
        "Silicon Labs Si1120 Ambient Light and Proximity Sensor",
        "Silicon Labs Si1132 UV Index and Ambient Light Sensor",
        "Silicon Labs Si1133 UV/ALS/IR Optical Sensor",
        "Texas Instruments OPT3001 Ambient Light Sensor",
        "Texas Instruments OPT4048D Color Sensor",
        "Texas Instruments OPT301 Photodiode Sensor",
        "Texas Instruments OPT4001 High-Speed Light Sensor",
        "Texas Instruments OPT3101 ToF Distance Sensor",
        "Silicon Labs Si1153 Ambient Light Sensor"
    ],
    "Distance and TOF Sensors": [
        "TDK CH101 Ultrasonic Time-of-Flight Sensor",
        "TDK CH201 Long-range Ultrasonic ToF Sensor",
        "TDK ICU-20201 Ultrasonic Range Sensor",
        "TDK ICU-30201 Ultrasonic ToF Module",
        "TDK DK-CH101 CH101 Development Kit",
        "Omron B5L 3D TOF Sensor Module",
        "TDK InvenSense CH201 Ultrasonic ToF Sensor",
        "TDK InvenSense ICU-20201 Ultrasonic ToF Sensor",
        "STMicroelectronics VL53L0X ToF Sensor",
        "Adafruit VL53L0X Time-of-Flight Distance Sensor",
        "Adafruit VL6180X Time-of-Flight Distance Sensor",
        "Adafruit HC-SR04 Ultrasonic Distance Sensor",
        "Adafruit VL53L1X Time-of-Flight Distance Sensor",
        "Adafruit VL53L4CD Time-of-Flight Sensor",
        "Omron B5L 3D TOF Sensor Module",
        "Ultrasonic Distance Sensor - HC-SR04",
        "Ultrasonic Distance Sensor - HY-SRF05",
        "Ultrasonic Distance Sensor - HC-SR03",
        "Melexis MLX75030 Time-of-Flight Optical Sensor",
        "Melexis MLX75031 ToF VGA Depth Sensor",
        "Silicon Labs Si1102 Optical Proximity Sensor",
        "Silicon Labs Si1120 Ambient Light and Proximity Sensor",
        "Silicon Labs Si114x Proximity and Gesture Sensor",
        "Silicon Labs Si114xM Proximity Sensor (Medical Applications)",
        "Silicon Labs Si115x Proximity/ALS/UV Sensor",
        "STMicroelectronics VL53L0X ToF Distance Sensor",
        "STMicroelectronics VL53L1X ToF Distance Sensor",
        "STMicroelectronics VL53L3CX ToF Multi-Target Sensor",
        "STMicroelectronics VL53L4CX ToF High-Accuracy Sensor",
        "STMicroelectronics VL53L5CX ToF Multi-Zone Sensor",
        "STMicroelectronics VL6180X ToF Proximity Sensor"
    ],
    "Inertial Modules and Orientation Sensors": [
        "Adafruit MPU-6050 6-Axis Accelerometer and Gyroscope",
        "Adafruit LSM9DS1 9-Axis IMU",
        "Adafruit BNO055 Absolute Orientation Sensor",
        "Adafruit LSM6DS33 6-Axis IMU",
        "Adafruit ICM-20948 9-Axis IMU",
        "Adafruit FXAS21002C + FXOS8700 9-Axis IMU",
        "MMA7455 Accelerometer Sensor",
        "GY-45 MMA8451 Digital Triaxial Accelerometer",
        "GY-45-52 MMA8452 Module",
        "ADXL345 IIC / SPI Tilt Sensor",
        "GY-29 ADXL345 Sensor Module",
        "Acceleration Sensor Module - 3-axis",
        "Gyroscope & Accelerometer Module - 3-axis",
        "GY-50 L3G4200D Digital Gyroscope",
        "GY-80 10DOF Nine-Axis Attitude Module",
        "GY-81 ITG3200 / BMA180 10DOF Module",
        "GY-651 HMC5883L BMP085 MWC Module",
        "GY-51 LSM303DLH 3-Axis Electronic Compass",
        "MMA7455 Angle Sensor Module",
        "Analog Devices ADIS16448 6-DoF IMU",
        "Analog Devices ADIS16460 Precision 6-DoF IMU",
        "Analog Devices ADIS16362 6-Axis IMU",
        "Analog Devices ADIS16485 High-Performance IMU",
        "Analog Devices ADIS16488A Tactical Grade IMU",
        "Analog Devices ADXL345 3-Axis Accelerometer",
        "Analog Devices ADXL362 Ultralow Power Accelerometer",
        "Analog Devices ADXL375 High-G Accelerometer",
        "Analog Devices ADXRS290 Dual-Axis Gyroscope",
        "Analog Devices ADIS16266 High-Precision Gyroscope",
        "Analog Devices ADXL335 3-Axis Accelerometer",
        "STMicroelectronics LIS2DH12 3-Axis Accelerometer",
        "STMicroelectronics LIS3DH 3-Axis Accelerometer",
        "STMicroelectronics LIS2DW12 Low-Power Accelerometer",
        "STMicroelectronics LIS2DUXS12 Ultra-Low-Power Accelerometer",
        "STMicroelectronics LSM6DSL 6-Axis IMU",
        "STMicroelectronics IIS2DLPC High-Precision Accelerometer",
        "STMicroelectronics LSM6DSO 6-Axis IMU",
        "STMicroelectronics LSM6DSOX 6-Axis IMU with Machine Learning",
        "STMicroelectronics LSM9DS1 9-Axis IMU",
        "STMicroelectronics ISM330DLC 6-Axis Industrial IMU",
        "STMicroelectronics LSM6DSM 6-Axis IMU",
        "STMicroelectronics LSM6DSR 6-Axis IMU",
        "TDK ICM-20948 9-axis IMU",
        "TDK MPU-6050 6-axis Accelerometer + Gyroscope",
        "TDK MPU-9250 9-axis IMU",
        "TDK ICM-20602 High-performance 6-axis IMU",
        "TDK ICM-42605 Low-noise 6-axis IMU",
        "TDK MPU-6886 Compact 6-axis IMU"
    ],
    "mmWave Radar Sensors": [
        "Texas Instruments IWR1642 mmWave Sensor",
        "Texas Instruments IWR6843 mmWave Sensor",
        "Texas Instruments AWR1642 mmWave Sensor",
        "Texas Instruments IWR1443 mmWave Sensor",
        "Texas Instruments AWR6843 mmWave Sensor"
    ],
    "Microphone Sensors": [
        "TDK ICS-40180 High-performance MEMS Microphone",
        "TDK ICS-40720 Directional MEMS Microphone",
        "InvenSense INMP441 I2S MEMS Microphone",
        "TDK ICS-52000 Stereo Digital MEMS Microphone",
        "TDK ICS-43434 Low-noise MEMS Microphone",
        "TDK InvenSense ICS-40180 MEMS Microphone",
        "STMicroelectronics MP34DT05-A MEMS Microphone",
        "TDK InvenSense INMP441 MEMS Microphone",
        "STMicroelectronics MP23ABS1 MEMS Microphone",
        "TDK InvenSense ICS-43434 MEMS Microphone",
        "Adafruit MAX9814 Electret Microphone Amplifier",
        "Adafruit SPH0645LM4H I2S MEMS Microphone",
        "Adafruit PDM MEMS Microphone Breakout",
        "Adafruit MAX4466 Electret Microphone Amplifier",
        "Adafruit ICS-40180 Analog MEMS Microphone",
        "Analog Devices ADMP441 Omnidirectional MEMS Microphone",
        "Analog Devices ADMP401 MEMS Microphone",
        "Analog Devices ADMP504 Ultralow Noise Microphone",
        "Analog Devices ADMP521 MEMS Microphone with PDM Output",
        "STMicroelectronics MP34DT05-A Digital MEMS Microphone",
        "STMicroelectronics MP23ABS1 Analog MEMS Microphone",
        "STMicroelectronics IMP34DT05 Digital MEMS Microphone",
        "STMicroelectronics MP23DB01HP Digital MEMS Microphone",
        "STMicroelectronics MP34DT06J Digital MEMS Microphone",
        "STMicroelectronics IMP23ABSU Ultrasonic MEMS Microphone"
    ],
    "Flame and Heat Sensors": [
        "SainSmart IR Flame Detection Sensor Module",
        "Flame Sensor with Small Board",
        "Flame Sensor - Fire Fighting Robot",
        "Thermal Sensor Module"
    ],
    "Touch and Capacitive Sensors": [
        "SainSmart Touch Sensor Module - TTP223B",
        "Digital Touch Sensor - 8-channel - TTP226",
        "Touch Sensor Module (Generic)"
    ],
    "Gas and Air Quality Sensors": [
        "Gas & Air Quality Sensor - MQ135",
        "Gas Sensor Module - LPG - MQ2",
        "MQ-131 Ozone Gas Detection Sensor Module",
        "Honeywell CRIR Series CO₂ NDIR Sensor",
        "Honeywell iSeries O₂ Sensor",
        "Honeywell MICROceL CO Sensor",
        "Honeywell MICROpeL Combustible Gas Sensor",
        "Honeywell MICROceL H₂S Sensor",
        "Honeywell MICS-VZ-89TE VOC Sensor",
        "Sensirion SCD41 CO2 Sensor",
        "Sensirion SCD40 CO2 Sensor",
        "Sensirion SCD30 CO2 Sensor"
    ],
    "Differential Pressure Sensors": [
        "Sensirion SDP31 Digital Differential Pressure Sensor (±500 Pa)",
        "Sensirion SDP32 Digital Differential Pressure Sensor (±125 Pa)",
        "Sensirion SDP33 Digital Differential Pressure Sensor (±1500 Pa)",
        "Sensirion SDP810-500Pa Digital Differential Pressure Sensor",
        "Sensirion SDP810-125Pa Digital Differential Pressure Sensor",
        "Sensirion SDP800-500Pa Digital Differential Pressure Sensor"
    ],
    "Flow Sensors": [
        "Honeywell SpiroQuant A+ Flow Sensor",
        "Honeywell AWM5000 Series Airflow Sensor",
        "Honeywell Zephyr HAF Series Flow Sensor",
        "Honeywell AWM3000 Series Airflow Sensor",
        "Honeywell AWM7000 Series Airflow Sensor",
        "Sensirion SLF3S-4000B Liquid Flow Sensor (600 ml/min)",
        "Sensirion SLF3S-1300F Liquid Flow Sensor (40 ml/min)",
        "Sensirion SLF3S-0600F Liquid Flow Sensor (2 ml/min)",
        "Sensirion LD20-2600B Liquid Flow Sensor (16.6 ml/min)",
        "Sensirion LG16-1000D Liquid Flow Sensor (1 ml/min)",
        "Sensirion LG16-2000D Liquid Flow Sensor (5 ml/min)"
    ],
    "Motion Sensors": [
        "TDK InvenSense MPU-6050 Accelerometer/Gyroscope",
        "TDK InvenSense ICM-20948 9-Axis IMU",
        "STMicroelectronics LIS2DH12 Accelerometer",
        "STMicroelectronics LSM6DSO 6-Axis IMU",
        "Texas Instruments DRV5055 Hall-Effect Sensor",
        "Melexis MLX90217 Hall-Effect Sensor",
        "Adafruit MPU-6050 6-Axis Accelerometer and Gyroscope",
        "Adafruit LSM9DS1 9-Axis IMU",
        "Adafruit LIS3DH Triple-Axis Accelerometer",
        "Adafruit ADXL345 Triple-Axis Accelerometer",
        "Adafruit LSM303DLHC Accelerometer + Magnetometer",
        "Adafruit FXOS8700 6-Axis Accelerometer and Magnetometer",
        "Analog Devices ADXL345 3-Axis Accelerometer",
        "Analog Devices ADXL362 Ultralow Power Accelerometer",
        "Analog Devices ADXL375 High-G Accelerometer",
        "Analog Devices ADXRS290 Dual-Axis Gyroscope",
        "Analog Devices ADIS16266 High-Precision Gyroscope",
        "Analog Devices ADXL335 3-Axis Accelerometer"
    ],
    "Pressure Sensors": [
        "Omron D6F-PH Differential Pressure Sensor",
        "TDK InvenSense ICP-10100 Barometric Pressure Sensor",
        "STMicroelectronics LPS22HH Pressure Sensor",
        "Texas Instruments BMP280 Barometric Pressure Sensor",
        "Melexis MLX90824 SENT Pressure Sensor",
        "Melexis MLX90821 Relative Pressure Sensor",
        "Adafruit BMP280 Barometric Pressure and Altitude Sensor",
        "Adafruit BMP388 Precision Barometric Pressure Sensor",
        "Adafruit LPS25HB Barometric Pressure Sensor",
        "Adafruit MPL115A2 Barometric Pressure Sensor",
        "Adafruit BME280 Temperature, Humidity, and Pressure Sensor",
        "Melexis MLX90817 Automotive Absolute Pressure Sensor",
        "Melexis MLX90818 Integrated Pressure Sensor",
        "Melexis MLX90819 High Accuracy Pressure Sensor",
        "Melexis MLX90820 Miniature Pressure Sensor",
        "Melexis MLX90821 Integrated Pressure Sensor",
        "Melexis MLX90822 MEMS Pressure Sensor",
        "Melexis MLX90823 Pressure Sensor with Digital Output",
        "Melexis MLX90824 Automotive Pressure Sensor",
        "Melexis MLX90825 Compact Pressure Sensor",
        "Melexis MLX90830 Analog Pressure Sensor",
        "Melexis MLX90833 High-Performance Pressure Sensor",
        "Melexis MLX90834 Barometric Pressure Sensor",
        "Melexis MLX90329 Integrated Pressure and Temperature Sensor",
        "STMicroelectronics LPS22HH Barometric Pressure Sensor",
        "STMicroelectronics LPS25HB Pressure and Altitude Sensor",
        "STMicroelectronics LPS33HW Water-Resistant Pressure Sensor",
        "STMicroelectronics LPS27HHTW Pressure and Temperature Sensor",
        "STMicroelectronics ILPS28QSW High-Accuracy Pressure Sensor",
        "STMicroelectronics LPS22DF Low-Power Pressure Sensor",
        "TDK ICP-10100 Ultra-low Noise Barometric Pressure Sensor",
        "TDK ICP-10101 Barometric Sensor for Wearables",
        "TDK ICP-10110 Compact Pressure Sensor",
        "TDK ICP-10125 Temperature-Compensated Pressure Sensor",
        "Infineon DPS310 High-resolution Pressure Sensor",
        "Bosch BMP581 Precision Digital Pressure Sensor"
    ],
    "Temperature Sensors": [
        "TDK ICP-10100 Ultra-low Noise Barometric Pressure Sensor",
        "TDK ICP-10101 Barometric Sensor for Wearables",
        "TDK ICP-10110 Compact Pressure Sensor",
        "TDK ICP-10125 Temperature-Compensated Pressure Sensor",
        "Infineon DPS310 High-resolution Pressure Sensor",
        "Bosch BMP581 Precision Digital Pressure Sensor",
        "STMicroelectronics STTS22H High-Accuracy Temperature Sensor",
        "STMicroelectronics STTS751 Temperature Sensor",
        "STMicroelectronics STLM75 Digital Temperature Sensor",
        "STMicroelectronics STTS2004 Temperature and Voltage Sensor",
        "STMicroelectronics STDS75 Temperature Sensor",
        "STMicroelectronics LM75B Temperature Sensor",
        "Silicon Labs Si705x Temperature Sensor Series",
        "Silicon Labs Si706x Temperature Sensor Series",
        "Texas Instruments TMP117 Temperature Sensor",
        "STMicroelectronics STTS22H Temperature Sensor",
        "TDK InvenSense STTS751 Temperature Sensor",
        "Melexis MLX90614 Infrared Thermometer",
        "Texas Instruments TMP102 Temperature Sensor",
        "Melexis MLX90632 Medical-Grade Thermometer",
        "Adafruit TMP117 High Precision Temperature Sensor",
        "Adafruit MCP9808 High Accuracy Temperature Sensor",
        "Adafruit SHT31-D Temperature and Humidity Sensor",
        "Adafruit AM2320 Temperature and Humidity Sensor",
        "Adafruit Si7021 Temperature and Humidity Sensor",
        "Adafruit HTU21D-F Temperature and Humidity Sensor",
        "Digital Temperature Sensor - DS18B20",
        "Waterproof Temperature Sensor - DS18B20",
        "Analog Temperature Sensor - LM35DZ - TO92",
        "TMP36GT9Z Sensor",
        "AM2303 Digital Temperature and Humidity Sensor",
        "Analog Devices ADT7410 High-Accuracy Temperature Sensor",
        "Analog Devices ADT7420 16-Bit Temperature Sensor",
        "Analog Devices TMP36 Low Voltage Temperature Sensor",
        "Analog Devices TMP05 Digital Output Temperature Sensor",
        "Analog Devices ADT7320 High-Accuracy SPI Temperature Sensor",
        "Melexis MLX90614 Infrared Temperature Sensor",
        "Melexis MLX90615 Infrared Temperature Sensor",
        "Melexis MLX90616 Infrared Temperature Sensor",
        "Melexis MLX90617 Infrared Temperature Sensor",
        "Melexis MLX90632 Medical Grade Infrared Temperature Sensor",
        "Melexis MLX90640 Thermal Imaging Array",
        "Melexis MLX90641 Thermal Imaging Array",
        "Melexis MLX90302 Temperature Sensor",
        "Sensirion STS4L Temperature Sensor",
        "Sensirion STS40 Temperature Sensor",
        "Sensirion STS35-DIS Temperature Sensor",
        "Sensirion STS31-DIS Temperature Sensor",
        "Sensirion STS31A-DIS Temperature Sensor",
        "Sensirion STS30-DIS Temperature Sensor",
        "Texas Instruments TMP117 High-Precision Temperature Sensor",
        "Texas Instruments TMP102 Temperature Sensor",
        "Texas Instruments TMP112 Temperature Sensor",
        "Texas Instruments TMP116 Temperature Sensor",
        "Texas Instruments LMT70 Analog Temperature Sensor",
        "Silicon Labs SI7021-A20-GM1R Humidity and Temperature Sensor"
    ],
    "Humidity Sensors": [
        "Texas Instruments HDC2080 Humidity Sensor",
        "TDK InvenSense HTS221 Humidity Sensor",
        "Texas Instruments HDC3020 Humidity Sensor",
        "TDK InvenSense SHTC3 Humidity Sensor",
        "Texas Instruments HDC2010 Humidity Sensor",
        "Adafruit SHT31-D Temperature and Humidity Sensor",
        "Adafruit HTU21D-F Temperature and Humidity Sensor",
        "Adafruit AM2320 Temperature and Humidity Sensor",
        "Adafruit Si7021 Temperature and Humidity Sensor",
        "Adafruit BME280 Temperature, Humidity, and Pressure Sensor",
        "Adafruit SHT40 Temperature and Humidity Sensor",
        "Humidity & Temperature Sensor - DHT11",
        "Digital Temperature & Humidity Sensor - DHT22 / AM2302",
        "Honeywell HIH6000 Series Humidity and Temperature Sensor",
        "Honeywell HIH7000 Series Humidity and Temperature Sensor",
        "Honeywell HIH6100 Series Humidity and Temperature Sensor",
        "Honeywell HIH8000 Series Humidity and Temperature Sensor",
        "Honeywell HIH-4602-A/C Humidity and Temperature Sensor",
        "Honeywell HIH-4000 Series Humidity Sensor",
        "Sensirion SHT45 Humidity and Temperature Sensor",
        "Sensirion SHT85 Humidity and Temperature Sensor",
        "Sensirion SHT35-DIS-B Humidity and Temperature Sensor",
        "Sensirion SHT31-DIS-B Humidity and Temperature Sensor",
        "Sensirion SHTC3 Humidity and Temperature Sensor",
        "Sensirion SHT40 Humidity and Temperature Sensor",
        "Silicon Labs Si7005 Humidity Sensor",
        "Silicon Labs Si7006/Si7013/Si7020/Si7021/Si7034 Humidity Sensor Series",
        "Silicon Labs Si7007/Si7022/Si7023 Humidity Sensor Series",
        "Silicon Labs Si7015 Humidity and Temperature Sensor",
        "ST HTS221 Capacitive Humidity Sensor",
        "TI HDC2010 Temp + Humidity Sensor",
        "TI HDC2080 Low Power Humidity Sensor",
        "Sensirion SHTC3 Compact Humidity Sensor",
        "Sensirion SHT40/SHT41 (SHT4x Series) Humidity Sensors",
        "Texas Instruments HDC2080 Humidity and Temperature Sensor",
        "Texas Instruments HDC3020 Humidity and Temperature Sensor",
        "Texas Instruments HDC2010 Humidity and Temperature Sensor",
        "Texas Instruments HDC1080 Humidity and Temperature Sensor",
        "Texas Instruments HDC1000 Humidity and Temperature Sensor",
        "Silicon Labs SI7021-A20-GM1R Humidity and Temperature Sensor"
    ],
    "Moisture and Water Sensors": [
        "Water Level Sensor",
        "Soil Moisture Sensor"
    ],
    "Networking Data": [
        "send temperature sensor data over UDP",
        "receive command over TCP to activate actuator",
        "post humidity readings to a web server using HTTP",
        "subscribe to MQTT topic to get control signals",
        #"send camera image snapshot to server via POST",
        "receive configuration from HTTP API",
        #"stream video frames over MJPEG using TCP socket",
        "broadcast light levels over UDP multicast",
        "fetch thresholds for sensors from a cloud endpoint",
        "stream live sensor data over local web server"
    ]
}

# Flatten sensor/actuator terms for broad detection
SENSOR_TERMS = set(term.lower() for term in CATEGORIES.get("sensor_reading", []))
ACTUATOR_TERMS = set(term.lower() for term in CATEGORIES.get("actuators", []))


# ---------- ANALYSIS SCRIPT START ----------

# ------------------- UTILS -------------------

def normalize(text):
    return text.lower().strip() if isinstance(text, str) else ""

def get_text_blob(entry):
    return " ".join([
        normalize(entry.get("input", "")),
        normalize(entry.get("prompt", "")),
    ])

def count_matches(text, items):
    return [item for item in items if normalize(item) in text]

def count_category_matches(text, category_map):
    matches = defaultdict(list)
    for cat, subs in category_map.items():
        for sub in subs:
            if normalize(sub) in text:
                matches[cat].append(sub)
    return matches

# ------------------- MAIN ANALYSIS -------------------

def analyze_examples(file_path, output_file):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    complexity_counter = Counter()
    pi_model_counter = Counter()
    context_counter = Counter()
    category_counter = defaultdict(Counter)
    sensor_presence = 0
    actuator_presence = 0

    for entry in data:
        try:
            tags = [normalize(tag) for tag in entry.get("tags", [])]
            text_blob = get_text_blob(entry) + " " + " ".join(tags)

            # Complexity
            complexity = normalize(entry.get("complexity", "unknown"))
            complexity_counter[complexity] += 1

            # Raspberry Pi models
            for model in PI_MODELS:
                if normalize(model) in text_blob:
                    pi_model_counter[model] += 1

            # Contexts
            for context in USE_CONTEXTS:
                if normalize(context) in text_blob:
                    context_counter[context] += 1

            # Category matches
            cat_matches = count_category_matches(text_blob, CATEGORIES)
            for cat, subs in cat_matches.items():
                category_counter[cat].update(subs)

            # Sensor/Actuator presence detection (1 per example)
            if any(term in tags for term in SENSOR_TERMS):
                sensor_presence += 1
            if any(term in tags for term in ACTUATOR_TERMS):
                actuator_presence += 1

        except Exception as e:
            print(f"⚠️ Error processing entry: {e}")

    # ------------------- ORGANIZE & DUMP -------------------

    results = {
        "complexity_distribution": dict(complexity_counter),
        "raspberry_pi_model_mentions": dict(pi_model_counter),
        "context_mentions": dict(context_counter),
        "category_matches": {
            cat: dict(subs) for cat, subs in category_counter.items()
        },
        "sensor_tag_presence": sensor_presence,
        "actuator_tag_presence": actuator_presence,
        "total_examples": len(data)
    }

    with open(output_file, "w") as out:
        json.dump(results, out, indent=2)

    print(f"\n✅ Analysis complete. Results saved to: {output_file}\n")

    # ------------------- PRINT RESULTS -------------------

    print("\n📊 Complexity Distribution:")
    for level, count in complexity_counter.items():
        print(f"  • {level.title()}: {count}")

    print("\n🧠 Raspberry Pi Model Mentions:")
    for model, count in pi_model_counter.items():
        print(f"  • {model}: {count}")

    print("\n🌍 Context Mentions:")
    for context, count in context_counter.items():
        print(f"  • {context}: {count}")

    print("\n🔌 Category Matches:")
    for cat, subcats in category_counter.items():
        print(f"\n  📁 {cat} ({sum(subcats.values())})")
        for sub, count in subcats.most_common():
            print(f"    - {sub}: {count}")

    print("\n📦 Sensor Presence in Tags: ", sensor_presence)
    print("⚙️  Actuator Presence in Tags:", actuator_presence)

# ------------------- CLI -------------------

if __name__ == "__main__":
    json_path = input("Enter the path to the JSON file: ").strip()
    output_path = input("Enter the output filename (press Enter to use default 'analysis_report.json'): ").strip()

    if not output_path:
        output_path = "analysis_report.json"

    analyze_examples(json_path, output_path)