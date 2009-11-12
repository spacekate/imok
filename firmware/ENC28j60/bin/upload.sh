#!/bin/sh

BIN_DIR=`pwd`
EXECUTABLE_NAME=imok_enc28j60

avr-objcopy -O ihex -R .eeprom ${EXECUTABLE_NAME}/${EXECUTABLE_NAME} ${EXECUTABLE_NAME}/${EXECUTABLE_NAME}.hex
cd /home/hamish/dev/arduino/from_src/arduino-read-only/build/linux/work && ./hamishUpload ${BIN_DIR}/${EXECUTABLE_NAME} ${EXECUTABLE_NAME} && cd -

# avr-objcopy -O ihex -R .eeprom blinkLED/blinkLED blinkLED/blinkLED.hex
# cd /home/hamish/dev/arduino/from_src/arduino-read-only/build/linux/work && ./hamishUpload /home/hamish/Archive/hardware/make/ArduinoProjects/bin/blinkLED blinkLED && cd -
