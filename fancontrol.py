#!/usr/bin/env python3

import subprocess
import time
import logging
from gpiozero import PWMOutputDevice
from logging.handlers import RotatingFileHandler

MIN_TEMP = 55  # celcius
MAX_TEMP = 75  # celcius
SLEEP_INTERVAL = 5  # seconds
GPIO_PIN = "GPIO18"  # pin number
LOG_PATH = "/var/log/fancontrol-output.log"
LOG_MAX_SIXE = 5000000 # in bytes
LOG_ROTATION_FILES = 2 # number of log files


def getTemp():
    try:
        output = subprocess.run(
            ['vcgencmd', 'measure_temp'], capture_output=True)
        temp_str = output.stdout.decode()
        return float(temp_str.split('=')[1].split('\'')[0])
    except (IndexError, ValueError):
        raise RuntimeError('Could not parse temperature output.')


def calcSpeed(temp, fromLow=MIN_TEMP, fromHigh=MAX_TEMP, toLow=0, toHigh=1):
    return toLow + (toHigh - toLow) * ((temp - fromLow) / (fromHigh - fromLow))


def createLoger(path):
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(path, maxBytes=LOG_MAX_SIXE, backupCount=LOG_ROTATION_FILES)
    formatter = logging.Formatter('%(asctime)-12s: %(levelname)-5s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


if __name__ == '__main__':
    fan = PWMOutputDevice(GPIO_PIN)
    logger = createLoger(LOG_PATH)
    try:
        while True:
            temp = getTemp()
            if temp > MIN_TEMP:
                speed = calcSpeed(temp)
                logger.info(f'TEMP: {temp}, SPEED: {speed}')
                fan.value = 1 if speed > 1 else speed
            else:
                fan.value = 0
            time.sleep(SLEEP_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Stop execution")
    except BaseException as err:
        logger.error(err)
    finally:
        fan.off()
