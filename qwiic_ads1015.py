#-------------------------------------------------------------------------------
# qwiic_ads1015.py
#
# Python library for the SparkFun Qwiic ADS1015, available here:
# https://www.sparkfun.com/products/15334
#-------------------------------------------------------------------------------
# Written by SparkFun Electronics, November 2024
#
# This python library supports the SparkFun Electroncis Qwiic ecosystem
#
# More information on Qwiic is at https://www.sparkfun.com/qwiic
#
# Do you like this library? Help support SparkFun. Buy a board!
#===============================================================================
# Copyright (c) 2024 SparkFun Electronics
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#===============================================================================

"""
qwiic_ads1015
============
Python module for the [SparkFun Qwiic ADS1015](https://www.sparkfun.com/products/15334)
This is a port of the existing [Arduino Library](https://github.com/sparkfun/SparkFun_ADS1015_Arduino_Library)
This package can be used with the overall [SparkFun Qwiic Python Package](https://github.com/sparkfun/Qwiic_Py)
New to Qwiic? Take a look at the entire [SparkFun Qwiic ecosystem](https://www.sparkfun.com/qwiic).
"""

# The Qwiic_I2C_Py platform driver is designed to work on almost any Python
# platform, check it out here: https://github.com/sparkfun/Qwiic_I2C_Py
import qwiic_i2c
import time

# Define the device name and I2C addresses. These are set in the class defintion
# as class variables, making them avilable without having to create a class
# instance. This allows higher level logic to rapidly create a index of Qwiic
# devices at runtine
_DEFAULT_NAME = "Qwiic ADS1015"

# Some devices have multiple available addresses - this is a list of these
# addresses. NOTE: The first address in this list is considered the default I2C
# address for the device.
_AVAILABLE_I2C_ADDRESS = [0x48, 0x49, 0x4A, 0x4B]

# Define the class that encapsulates the device being created. All information
# associated with this device is encapsulated by this class. The device class
# should be the only value exported from this module.
class QwiicADS1015(object):
    # Set default name and I2C address(es)
    device_name         = _DEFAULT_NAME
    available_addresses = _AVAILABLE_I2C_ADDRESS

    # Register addresses
    ADS1015_DELAY = 1

    # TODO: potentially we could delete some of the below constants to save space if we don't think we'll use them in 

    # Pointer Register
    kPointerConvert = 0x00
    kPointerConfig = 0x01
    kPointerLowThresh = 0x02
    kPointerHiThresh = 0x03

    # Config Register

    # Operational status or single-shot conversion start
    # This bit determines the operational status of the device. OS can only be written
    # when in power-down state and has no effect when a conversion is ongoing.

    kConfigOsNo = 0x0000
    kConfigOsSingle = 0x8000  # 1 : Start a single conversion (when in power-down state)
    kConfigOsNotReady = 0x0000  # 0 : Device is currently performing a conversion
    kConfigOsReady = 0x8000  # 1 : Device is not currently performing a conversion

    kConfigModeCont = 0x0000
    kConfigModeSingle = 0x0100

    kConfigMuxSingle0 = 0x4000
    kConfigMuxSingle1 = 0x5000
    kConfigMuxSingle2 = 0x6000
    kConfigMuxSingle3 = 0x7000
    kConfigMuxDiffP0N1 = 0x0000
    kConfigMuxDiffP0N3 = 0x1000
    kConfigMuxDiffP1N3 = 0x2000
    kConfigMuxDiffP2N3 = 0x3000

    kConfigRateMask = 0x00E0
    kConfigRate128Hz = 0x0000
    kConfigRate250Hz = 0x0020
    kConfigRate490Hz = 0x0040
    kConfigRate920Hz = 0x0060
    kConfigRate1600Hz = 0x0080
    kConfigRate2400Hz = 0x00A0
    kConfigRate3300Hz = 0x00C0

    kConfigPgaMask = 0x0E00
    kConfigPgaTwoThirds = 0x0000  # +/- 6.144v
    kConfigPga1 = 0x0200  # +/- 4.096v
    kConfigPga2 = 0x0400  # +/- 2.048v
    kConfigPga4 = 0x0600  # +/- 1.024v
    kConfigPga8 = 0x0800  # +/- 0.512v
    kConfigPga16 = 0x0A00  # +/- 0.256v

    kConfigCmodeTrad = 0x0000  # Traditional comparator with hysteresis (default)
    kConfigCmodeWindow = 0x0010  # Window comparator
    kConfigCpolActvLow = 0x0000  # ALERT/RDY pin is low when active (default)
    kConfigCpolActvHi = 0x0008  # ALERT/RDY pin is high when active
    kConfigClatNonLat = 0x0000  # Non-latching comparator (default)
    kConfigClatLatch = 0x0004  # Latching comparator
    kConfigCque1Conv = 0x0000  # Assert ALERT/RDY after one conversion
    kConfigCque2Conv = 0x0001  # Assert ALERT/RDY after two conversions
    kConfigCque4Conv = 0x0002  # Assert ALERT/RDY after four conversions
    kConfigCqueNone = 0x0003  # Disable the comparator and put ALERT/RDY in high state (default)

    def __init__(self, address=None, i2c_driver=None):
        """
        Constructor

        :param address: The I2C address to use for the device
            If not provided, the default address is used
        :type address: int, optional
        :param i2c_driver: An existing i2c driver object
            If not provided, a driver object is created
        :type i2c_driver: I2CDriver, optional
        """

        # Use address if provided, otherwise pick the default
        if address in self.available_addresses:
            self.address = address
        else:
            self.address = self.available_addresses[0]

        # Load the I2C driver if one isn't provided
        if i2c_driver is None:
            self._i2c = qwiic_i2c.getI2CDriver()
            if self._i2c is None:
                print("Unable to load I2C driver for this platform.")
                return
        else:
            self._i2c = i2c_driver

        self._sampleRate = self.kConfigRate1600Hz
        self._gain = self.kConfigPga2
        self._useConversionReady = False # Default to disabled, allowing continous mode to be used
        self._mode = self.kConfigModeCont # Default to continuous mode
        self._multiplierToVolts = 1.0

        # Array is structured as calibrationValues[finger][lo/hi]
        self._calibrationValues = [[0,0],[0,0]]

    def is_connected(self):
        """
        Determines if this device is connected

        :return: `True` if connected, otherwise `False`
        :rtype: bool
        """
        # Check if connected by seeing if an ACK is received
        # TODO: If the device has a product ID register, that should be
        # checked in addition to the ACK
        return self._i2c.isDeviceConnected(self.address)

    connected = property(is_connected)

    def begin(self):
        """
        Initializes this device with default parameters

        :return: Returns `True` if successful, otherwise `False`
        :rtype: bool
        """
        # Confirm device is connected before doing anything
        if not self.is_connected():
            return False

        return True


    def get_single_ended(self, channel):
        """
        Returns the decimal value of sensor channel single-ended input
        :param channel: The channel to read
        :type channel: int

        :return: The decimal value of the sensor channel
        :rtype: int
        """
        if channel > 3:
            return 0

        config = self.kConfigOsSingle | self.kConfigCqueNone | self._sampleRate

        config |= self._gain

        if self._useConversionReady:
            config |= self.kConfigModeSingle
        else:
            config |= self._mode

        if channel == 0:
            config |= self.kConfigMuxSingle0
        elif channel == 1:
            config |= self.kConfigMuxSingle1
        elif channel == 2:
            config |= self.kConfigMuxSingle2
        elif channel == 3:
            config |= self.kConfigMuxSingle3

        self._i2c.writeWord(self.address, self.kPointerConfig, config)

        if self._useConversionReady:
            while not self.available():
                pass
            else:
                self.conversion_delay()

        result = self._i2c.readWord(self.address, self.kPointerConvert)
        return result >> 4
    
    def get_single_ended_signed(self, channel):
        """
        Returns the signed value of sensor channel single-ended input
        :param channel: The channel to read
        :type channel: int

        :return: The signed value of the sensor channel
        :rtype: int
        """
        value = self.get_single_ended(channel)
        if value > 32767:
            value -= 32767

        return value
    
    def get_single_ended_millivolts(self, channel):
        """
        Returns the millivolt value of sensor channel single-ended input
        :param channel: The channel to read
        :type channel: int

        :return: The millivolt value of the sensor channel
        :rtype: float
        """
        return self.get_single_ended(channel) * self.get_multiplier()
    
    def get_differential(self, config_mux_diff=kConfigMuxDiffP0N1):
        """
        Returns the signed decimal value of sensor differential input
        Note, there are 4 possible differential pin setups:
        kConfigMuxDiffP0N1
        kConfigMuxDiffP0N3
        kConfigMuxDiffP1N3
        kConfigMuxDiffP2N3

        :param config_mux_dif: The differential pin set up from the list above
        :type config_mux_dif: int

        :return: The signed value of the sensor differential input channel
        :rtype: int
        """
        if config_mux_diff not in [
            self.kConfigMuxDiffP0N1,
            self.kConfigMuxDiffP0N3,
            self.kConfigMuxDiffP1N3,
            self.kConfigMuxDiffP2N3,
        ]:
            return 0  # received invalid argument

        config = self.kConfigOsSingle | self.kConfigCqueNone | self._sampleRate
        config |= self._gain

        if self._useConversionReady:
            config |= self.kConfigModeSingle
        else:
            config |= self._mode
        
        config |= config_mux_diff

        self._i2c.writeWord(self.address, self.kPointerConfig, config)

        if self._useConversionReady:
            while not self.available():
                pass
        else:
            self.conversion_delay()

        result = self._i2c.readWord(self.address, self.kPointerConvert) >> 4

        if result > 32767:
            result -= 65536
        
        return result

    def get_differential_millivolts(self, config_mux_diff=kConfigMuxDiffP0N1):
        """
        Returns the millivolt value of sensor differential input
        Note, there are 4 possible differential pin setups:
        kConfigMuxDiffP0N1
        kConfigMuxDiffP0N3
        kConfigMuxDiffP1N3
        kConfigMuxDiffP2N3

        :param config_mux_dif: The differential pin set up from the list above
        :type config_mux_dif: int

        :return: The millivolt value of the sensor differential input channel
        :rtype: float
        """
        value = self.get_differential(config_mux_diff)
        return value * self.get_multiplier()
    
    def mapf(self, val, in_min, in_max, out_min, out_max):
        """
            Maps a value from one range to another
            :param val: The value to map
            :type val: float
            :param in_min: The minimum value of the input range
            :type in_min: float
            :param in_max: The maximum value of the input range
            :type in_max: float
            :param out_min: The minimum value of the output range
            :type out_min: float
            :param out_max: The maximum value of the output range
            :type out_max: float
            :return: The mapped value
            :rtype: float
        """
        return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def get_scaled_analog_data(self, channel):
        """
        Returns a value between 0 and 1 based on how bent the finger is. This function will not work with an uncalibrated sensor
        :param channel: The channel to read
        :type channel: int
        :return: The scaled value of the sensor
        :rtype: float
        """
        if channel > 3:
            return 0
        
        data = self.mapf(self.get_single_ended(channel), self._calibrationValues[channel][0], self._calibrationValues[channel][1], 0, 1)

        if data > 1:
            return 1
        elif data < 0:
            return 0
        else:
            return data

    def calibrate(self):
        """
        Perform calibration on the sensor. This function will set the calibration values for each finger
        """
        for finger in range(2):
            value = self.get_single_ended(finger)
            if (value > self._calibrationValues[finger][1] or self._calibrationValues[finger][1] == 0) and value < 1085:
                self._calibrationValues[finger][1] = value
            elif (value < self._calibrationValues[finger][0] or self._calibrationValues[finger][0] == 0):
                self._calibrationValues[finger][0] = value
    
    def get_calibration(self, channel, hiLo):
        """
        Returns the calibration value for the specified channel and hiLo
        :param channel: The channel to read
        :type channel: int
        :param hiLo: The hiLo to read
        :type hiLo: int
        :return: The calibration value
        :rtype: int
        """
        return self._calibrationValues[channel][hiLo]
    
    def set_calibration(self, channel, hiLo, value):
        """
        Sets the calibration value for the specified channel and hiLo
        :param channel: The channel to read
        :type channel: int
        :param hiLo: The hiLo to read
        :type hiLo: int
        :param value: The value to set
        :type value: int
        """
        self._calibrationValues[channel][hiLo] = value
    
    def reset_calibration(self):
        """
        Resets the calibration values to 0
        """
        self._calibrationValues = [[0,0],[0,0]]
    
    def set_mode(self, mode):
        """
        Sets the mode of the device. Continuous mode 0 is favored
        :param mode: The mode to set
        :type mode: int
        """
        mode &= self.kConfigModeSingle
        self._mode = mode

    def get_mode(self):
        """
        Returns the mode of the device. get_mode will return 0 for continuous and ADS1015_CONFIG_MODE_SINGLE for single shot
        :return: The mode of the device
        :rtype: int
        """
        return self._mode

    def set_gain(self, gain):
        """
        Sets the gain of the device. 
        Valid values are: 
            kConfigPgaTwoThirds,
            kConfigPga1,
            kConfigPga2,
            kConfigPga4,
            kConfigPga8,
            kConfigPga16

        :param gain: The gain to set
        :type gain: int
        """
        gain &= self.kConfigPgaMask
        self._gain = gain
        self.update_multiplier_to_volts() # each new gain setting changes how we convert to volts
    
    def get_gain(self):
        """
        Returns the gain of the device
            Will return a differnet hex value of each gain setting:
            0x0E00: +/- 0.256V
            0X0000: +/- 6.144V
            0X0200: +/- 4.096V
            0X0400: +/- 2.048V
            0X0600: +/- 1.024V
            0X0800: +/- 0.512V
            0X0A00: +/- 0.256V

        :return: The gain of the device
        :rtype: int
        """
        return self._gain
    
    def update_multiplier_to_volts(self):
        """
        Updates the multiplier to convert to volts
        """
        if self._gain == self.kConfigPgaTwoThirds:
            self._multiplierToVolts = 3.0
        elif self._gain == self.kConfigPga1:
            self._multiplierToVolts = 2.0
        elif self._gain == self.kConfigPga2:
            self._multiplierToVolts = 1.0
        elif self._gain == self.kConfigPga4:
            self._multiplierToVolts = 0.5
        elif self._gain == self.kConfigPga8:
            self._multiplierToVolts = 0.25
        elif self._gain == self.kConfigPga16:
            self._multiplierToVolts = 0.125
        else:
            self._multiplierToVolts = 1.0

    def get_multiplier(self):
        """
        Returns the multiplier to convert to volts
        :return: The multiplier to convert to volts
        :rtype: float
        """
        return self._multiplierToVolts

    def set_sample_rate(self, rate):
        """
        Sets the sample rate of the device
        :param rate: The sample rate to set
        :type rate: int
        """
        rate &= self.kConfigRateMask
        self._sampleRate = rate
    
    def get_sample_rate(self):
        """
        Will return a different hex value for each sample rate
        Possible Values:
            0x0000: 128 Hz
            0X0020: 250 Hz
            0X0040: 490 Hz
            0X0060: 920 Hz
            0X0080: 1600 Hz
            0X00A0: 2400 Hz
            0X00C0: 3300 Hz

        :return: The sample rate of the device
        :rtype: int
        """
        return self._sampleRate
    
    def available(self):
        """
        Checks to see if the Operational Status (OS) flag is set in the status register
        :return: True if the OS flag is set, otherwise False
        :rtype: bool
        """
        value = self._i2c.readWord(self.address, self.kPointerConfig)
        return (value & self.kConfigOsReady > 0)
    
    def set_comparator_single_ended(self, channel, threshold):
        """
        Sets up the comparator to operate in basic mode, causing the
            ALERT/RDY pin to assert (go from high to low) when the ADC
            value exceeds the specified threshold.

            This will also set the ADC in continuous conversion mode.

        Note, this function was adapted from the Adafruit Industries
        located here:
        https://github.com/adafruit/Adafruit_ADS1X15

        :param channel: The channel to read
        :type channel: int
        :param threshold: The threshold value to compare
        :type threshold: int
        """
        if channel > 3:
            return 0

        config = (
            self.kConfigModeCont |
            self._sampleRate |
            self.kConfigCque1Conv |   # Comparator enabled and asserts on 1 match
            self.kConfigClatLatch |   # Latching mode
            self.kConfigCpolActvLow | # Alert/Rdy active low (default val)
            self.kConfigCmodeTrad    # Traditional comparator (default val)
        )

        config |= self._gain

        if channel == 0:
            config |= self.kConfigMuxSingle0
        elif channel == 1:
            config |= self.kConfigMuxSingle1
        elif channel == 2:
            config |= self.kConfigMuxSingle2
        elif channel == 3:
            config |= self.kConfigMuxSingle3

        # Set the high threshold register
        # Shift 12-bit results left 4 bits for the ADS1015
        
        self._i2c.writeWord(self.address, self.kPointerHiThresh, threshold << 4)

        # Write config register to the ADC
        self._i2c.writeWord(self.address, self.kPointerConfig, config)
    
    def get_last_conversion_results(self):
        """
            In order to clear the comparator, we need to read the
            conversion results.  This function reads the last conversion
            results without changing the config value.

            Note, this function was adapted from the Adafruit Industries
            located here:
            https://github.com/adafruit/Adafruit_ADS1X15

            :return: The last conversion result
            :rtype: int
        """

        # Read the conversion results
        # Shift 12-bit results right 4 bits for the ADS1015,
        # making sure we keep the sign bit intact
        result = self._i2c.readWord(self.address, self.kPointerConvert) >> 4

        # Convert to signed 
        if result > 32767:
            result -= 65536
        
        return result

    def conversion_delay(self):
        """
        Delay for experimentally-determined delay times based on sample rate.
        These were determined experimentally by using Example7
        """
        if self._sampleRate >= self.kConfigRate3300Hz:
            time.sleep(0.000400) # > 303 us + 10% + 25 us power-up
        elif self._sampleRate >= self.kConfigRate2400Hz:
            time.sleep(0.000500) # > (417us + 10% + 25us power-up)
        elif self._sampleRate >= self.kConfigRate1600Hz:
            time.sleep(0.001000) # > (625us + 10% + 25us power-up)
        elif self._sampleRate >= self.kConfigRate920Hz:
            time.sleep(0.002000)
        elif self._sampleRate >= self.kConfigRate490Hz:
            time.sleep(0.004000)
        elif self._sampleRate >= self.kConfigRate250Hz:
            time.sleep(0.008000)
        else:
            time.sleep(0.016000) # 128Hz
    
    def use_conversion_ready(self, enable):
        """
        Enables or disables the use of useConversionReady

        When useConversionReady is enabled:
        The Config Register OS bit is read to determine when the conversion is complete - instead of using conversionDelay.
        Single-shot mode is always selected. _mode is ignored.

        :param enable: True to enable, False to disable
        :type enable: bool
        """
        self._useConversionReady = enable
