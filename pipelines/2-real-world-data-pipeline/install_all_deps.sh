#!/bin/bash

set -e

echo "🔧 Starting setup for all required libraries..."

sudo apt update
sudo apt upgrade -y

echo "📦 Installing essential build tools..."
sudo apt install -y build-essential cmake git scons wget curl pkg-config \
                    python3-dev python3-pip python-dev-is-python3 \
                    libjson-c-dev libpcre3-dev libaio-dev libjpeg-dev \
                    imagemagick fswebcam scons swig

echo "📦 Installing GPIO libraries..."
sudo apt install -y libgpiod-dev libraspberrypi-dev \
                    libmmal-dev libmmal-core-dev libmmal-util-dev

echo "📦 Installing I2C/SPI tools..."
sudo apt install -y i2c-tools libi2c-dev libspi-dev linux-headers-$(uname -r)

echo "📦 Installing camera and image libs..."
sudo apt install -y libcamera-dev libv4l-dev libopencv-dev \
                    libavcodec-dev libgstreamer1.0-dev libsdl2-dev

echo "📦 Installing config, JSON, and INI parsers..."
sudo apt install -y libconfig-dev libcjson-dev libjansson-dev \
                    libinih-dev libiniparser-dev

echo "📦 Installing messaging and networking libs..."
sudo apt install -y libmosquitto-dev libpaho-mqtt-dev \
                    libzmq3-dev libnanomsg-dev librabbitmq-dev \
                    libcoap3-dev libevent-dev libcurl4-openssl-dev \
                    libmicrohttpd-dev libatomic-ops-dev libsystemd-dev \
                    libturbojpeg0-dev libfftw3-dev liblwip-dev \
                    libmraa-dev

echo "📦 Fixing MQTT header path..."
sudo mkdir -p /usr/include/paho-mqtt
sudo ln -sf /usr/include/MQTTClient.h /usr/include/paho-mqtt/MQTTClient.h

echo "📦 Cloning and installing WiringPi (legacy)..."
git clone https://github.com/WiringPi/WiringPi.git || true
cd WiringPi && ./build && cd ..

echo "📦 Cloning and installing pigpio..."
git clone https://github.com/joan2937/pigpio.git || true
cd pigpio && make && sudo make install && cd ..

echo "📦 Cloning and installing rpi_ws281x..."
git clone https://github.com/jgarff/rpi_ws281x.git || true
cd rpi_ws281x && scons && sudo scons install && cd ..

echo "📦 Installing mongoose (header-only)..."
git clone https://github.com/cesanta/mongoose.git || true
cd mongoose && sudo cp mongoose.h /usr/local/include/ && cd ..

echo "📦 Installing libcoap from source..."
git clone https://github.com/obgm/libcoap.git || true
cd libcoap
mkdir -p build && cd build
cmake .. && make && sudo make install
cd ../..

echo "✅ All dependencies installed successfully!"
