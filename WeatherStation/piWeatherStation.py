#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Connect to Oregon Scientific BLE Weather Station
# Copyright (c) 2016 Arnaud Balmelle
#
# This script will connect to Oregon Scientific BLE Weather Station
# and retrieve the temperature of the base and sensors attached to it.
# If no mac-address is passed as argument, it will scan for an Oregon Scientific BLE Weather Station.
#
# Supported Oregon Scientific Weather Station: EMR211 and RAR218HG (and probably BAR218HG)
#
# Usage: python bleWeatherStation.py [mac-address]
#
# Dependencies:
# - Bluetooth 4.1 and bluez installed
# - bluepy library (https://github.com/IanHarvey/bluepy)
#
# License: Released under an MIT license: http://opensource.org/licenses/MIT
# https://www.instructables.com/id/Connect-Raspberry-Pi-to-Oregon-Scientific-BLE-Weat/
#
# Run with python 2.7 NOT python 3.7

import os
import sys
import logging
import time
from subprocess import check_output
from bluepy.btle import * 
from math import log

# uncomment the following line to get debug information
# logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.DEBUG)

WEATHERSTATION_NAME = "" # IDTW213R for RAR218HG
WEATHERSTATION_MAC = ""

class WeatherStation:
	def __init__(self, mac):
		self._data = {}
		try:
			self.p = Peripheral(mac, ADDR_TYPE_RANDOM)
			self.p.setDelegate(NotificationDelegate())
			logging.debug('WeatherStation connected !')
		except BTLEException:
			self.p = 0
			logging.debug('Connection to WeatherStation failed !')
			raise
			
	def _enableNotification(self):
		try:
			# Enable all notification or indication
			self.p.writeCharacteristic(0x000c, "\x02\x00")
			self.p.writeCharacteristic(0x000f, "\x02\x00")
			self.p.writeCharacteristic(0x0012, "\x02\x00")
			self.p.writeCharacteristic(0x0015, "\x01\x00")
			self.p.writeCharacteristic(0x0018, "\x02\x00")
			self.p.writeCharacteristic(0x001b, "\x02\x00")
			self.p.writeCharacteristic(0x001e, "\x02\x00")
			self.p.writeCharacteristic(0x0021, "\x02\x00")
			self.p.writeCharacteristic(0x0032, "\x01\x00")
			logging.debug('Notifications enabled')
		
		except BTLEException as err:
			print(err)
			self.p.disconnect()
	
	def monitorWeatherStation(self):
		try:
			# Enable notification
			self._enableNotification()
			# Wait for notifications
			while self.p.waitForNotifications(1.0):
				# handleNotification() was called
				continue
			logging.debug('Notification timeout')
		except:
			return None
		
		regs = self.p.delegate.getData()
		if regs is not None:
			# expand INDOOR_AND_CH1_TO_3_TH_DATA_TYPE0
			self._data['index0_temperature'] = ''.join(regs['data_type0'][4:6] + regs['data_type0'][2:4])
			self._data['index1_temperature'] = ''.join(regs['data_type0'][8:10] + regs['data_type0'][6:8])
			self._data['index2_temperature'] = ''.join(regs['data_type0'][12:14] + regs['data_type0'][10:12])
			self._data['index3_temperature'] = ''.join(regs['data_type0'][16:18] + regs['data_type0'][14:16])
			self._data['index0_humidity'] = regs['data_type0'][18:20]
			self._data['index1_humidity'] = regs['data_type0'][20:22]
			self._data['index2_humidity'] = regs['data_type0'][22:24]
			self._data['index3_humidity'] = regs['data_type0'][24:26]
			self._data['temperature_trend'] = regs['data_type0'][26:28]
			self._data['humidity_trend'] = regs['data_type0'][28:30]
			self._data['index0_humidity_max'] = regs['data_type0'][30:32]
			self._data['index0_humidity_min'] = regs['data_type0'][32:34]
			self._data['index1_humidity_max'] = regs['data_type0'][34:36]
			self._data['index1_humidity_min'] = regs['data_type0'][36:38]
			self._data['index2_humidity_max'] = regs['data_type0'][38:40]
			# expand INDOOR_AND_CH1_TO_3_TH_DATA_TYPE1
			self._data['index2_humidity_min'] = regs['data_type1'][2:4]
			self._data['index3_humidity_max'] = regs['data_type1'][4:6]
			self._data['index3_humidity_min'] = regs['data_type1'][6:8]
			self._data['index0_temperature_max'] = ''.join(regs['data_type1'][10:12] + regs['data_type1'][8:10])
			self._data['index0_temperature_min'] = ''.join(regs['data_type1'][14:16] + regs['data_type1'][12:14])
			self._data['index1_temperature_max'] = ''.join(regs['data_type1'][18:20] + regs['data_type1'][16:18])
			self._data['index1_temperature_min'] = ''.join(regs['data_type1'][22:24] + regs['data_type1'][20:22])
			self._data['index2_temperature_max'] = ''.join(regs['data_type1'][26:28] + regs['data_type1'][24:26])
			self._data['index2_temperature_min'] = ''.join(regs['data_type1'][30:32] + regs['data_type1'][28:30])
			self._data['index3_temperature_max'] = ''.join(regs['data_type1'][34:36] + regs['data_type1'][32:34])
			self._data['index3_temperature_min'] = ''.join(regs['data_type1'][38:40] + regs['data_type1'][36:38])
			return True
		else:
			return None
			
	def getValue(self, indexstr):
		val = int(self._data[indexstr], 16)
		if val >= 0x8000:
			val = ((val + 0x8000) & 0xFFFF) - 0x8000
		return val
	
	def getIndoorTemp(self):
		
		if 'index0_temperature' in self._data:
			temp = self.getValue('index0_temperature') / 10.0
			max = self.getValue('index0_temperature_max') / 10.0
			min = self.getValue('index0_temperature_min') / 10.0
			logging.debug('Indoor temp : %.1f°C, max : %.1f°C, min : %.1f°C', temp, max, min)
			return temp, max, min
		else:
			return None
	
	def getOutdoorTemp(self):
		if 'index1_temperature' in self._data:
			temp = self.getValue('index1_temperature') / 10.0
			max = self.getValue('index1_temperature_max') / 10.0
			min = self.getValue('index1_temperature_min') / 10.0
			logging.debug('Outdoor temp : %.1f°C, max : %.1f°C, min : %.1f°C', temp, max, min)
			return temp, max, min
		else:
			return None

	def getOutdoorTemp2(self):
		if 'index2_temperature' in self._data:
			temp = self.getValue('index2_temperature') / 10.0
			max = self.getValue('index2_temperature_max') / 10.0
			min = self.getValue('index2_temperature_min') / 10.0
			logging.debug('Outdoor temp : %.1f°C, max : %.1f°C, min : %.1f°C', temp, max, min)
			return temp, max, min
		else:
			return None

	def getAverageOutdoorTemp(self):
		if 'index1_temperature' in self._data and 'index2_temperature' in self._data:
			temp1 = self.getValue('index1_temperature') / 10.0
			temp2 = self.getValue('index2_temperature') / 10.0
			avg_temp = (temp1+temp2) / 2.0
			logging.debug('Average Outdoor temp : %.1f°C', avg_temp)
			return avg_temp
		else:
			return None

	def getIndoorHumidity(self):
		if 'index0_humidity' in self._data:
			humidity = self.getValue('index0_humidity')
			max = self.getValue('index0_humidity_max')
			min = self.getValue('index0_humidity_min')
			logging.debug(
				'Indoor humidity : %.1f°C, max : %.1f°C, min : %.1f°C', humidity, max, min)
			return humidity, max, min
		else:
			return None
			
	def getOutdoorHumidity(self):
		if 'index1_humidity' in self._data:
			humidity = self.getValue('index1_humidity')
			max = self.getValue('index1_humidity_max')
			min = self.getValue('index1_humidity_min')
			logging.debug(
				'Outdoor humidity : %.1f°C, max : %.1f°C, min : %.1f°C', humidity, max, min)
			return humidity, max, min
		else:
			return None

	def getDewPoint(self, t_air_c, rel_humidity):
	    """Compute the dew point in degrees Celsius
	    :param t_air_c: current ambient temperature in degrees Celsius
	    :type t_air_c: float
	    :param rel_humidity: relative humidity in %
	    :type rel_humidity: float
	    :return: the dew point in degrees Celsius
	    :rtype: float
	    """
	    A = 17.27
	    B = 237.7
	    alpha = ((A * t_air_c) / (B + t_air_c)) + log(rel_humidity/100.0)
	    x = (B * alpha) / (A - alpha)
	    return round(x,2)

	def getFrostPoint(self, t_air_c, dew_point_c):
	    """Compute the frost point in degrees Celsius
	    :param t_air_c: current ambient temperature in degrees Celsius
	    :type t_air_c: float
	    :param dew_point_c: current dew point in degrees Celsius
	    :type dew_point_c: float
	    :return: the frost point in degrees Celsius
	    :rtype: float
	    """
	    dew_point_k = 273.15 + dew_point_c
	    t_air_k = 273.15 + t_air_c
	    frost_point_k = dew_point_k - t_air_k + 2671.02 / ((2954.61 / t_air_k) + 2.193665 * log(t_air_k) - 13.3448)
	    x = frost_point_k - 273.15
	    return round(x,2)

	def getWeather(self):
		pass


	def disconnect(self):
		self.p.disconnect()
		
class NotificationDelegate(DefaultDelegate):
	def __init__(self):
		DefaultDelegate.__init__(self)
		self._indoorAndOutdoorTemp_type0 = None
		self._indoorAndOutdoorTemp_type1 = None
		
	def handleNotification(self, cHandle, data):
		formatedData = binascii.b2a_hex(data)
		if cHandle == 0x0017:
			# indoorAndOutdoorTemp indication received
			if formatedData[0] == '8':
				# Type1 data packet received
				self._indoorAndOutdoorTemp_type1 = formatedData
				logging.debug('indoorAndOutdoorTemp_type1 = %s', formatedData)
			else:
				# Type0 data packet received
				self._indoorAndOutdoorTemp_type0 = formatedData
				logging.debug('indoorAndOutdoorTemp_type0 = %s', formatedData)
		else:
			# skip other indications/notifications
			logging.debug('handle %x = %s', cHandle, formatedData)
	
	def getData(self):
			if self._indoorAndOutdoorTemp_type0 is not None:
				# return sensors data
				return {'data_type0':self._indoorAndOutdoorTemp_type0, 'data_type1':self._indoorAndOutdoorTemp_type1}
			else:
				return None

class ScanDelegate(DefaultDelegate):
	def __init__(self):
		DefaultDelegate.__init__(self)
		
	def handleDiscovery(self, dev, isNewDev, isNewData):
		global weatherStationMacAddr
		if dev.getValueText(9) == WEATHERSTATION_NAME:
			# Weather Station in range, saving Mac address for future connection
			logging.info('WeatherStation found')
			weatherStationMacAddr = dev.addr

if __name__=="__main__":

	# weatherStationMacAddr = WEATHERSTATION_MAC

	weatherStationMacAddr = None
	if len(sys.argv) < 2:
		# No MAC address passed as argument
		try:
			# Scanning to see if Weather Station in range
			scanner = Scanner().withDelegate(ScanDelegate())
			devices = scanner.scan(2.0)
		except BTLEException as err:
			print(err)
			print('Scanning required root privilege, so do not forget to run the script with sudo.')
	else:
		# Weather Station MAC address passed as argument, will attempt to connect with this address
		weatherStationMacAddr = sys.argv[1]
	if weatherStationMacAddr is None:
		logging.info('No WeatherStation in range !')
	else:

		try:
			# Attempting to connect to device with MAC address "weatherStationMacAddr"
			weatherStation = WeatherStation(weatherStationMacAddr)
			
			if weatherStation.monitorWeatherStation() is not None:

				# WeatherStation data received
				indoor, max_indoor, min_indoor                               = weatherStation.getIndoorTemp()
				outdoor, max_outdoor, min_outdoor                            = weatherStation.getOutdoorTemp()
				outdoor2, max_outdoor2, min_outdoor2                         = weatherStation.getOutdoorTemp2()
				indoor_humidity, max_indoor_humidity, min_indoor_humidity    = weatherStation.getIndoorHumidity()
				outdoor_humidity, max_outdoor_humidity, min_outdoor_humidity = weatherStation.getOutdoorHumidity()
				avg_outdoor_temp                                             = weatherStation.getAverageOutdoorTemp()
				dewpoint                                                     = weatherStation.getDewPoint(float(outdoor), float(outdoor_humidity))
				# frostpoint                                                   = weatherStation.getFrostPoint(float(outdoor), dewpoint)

				if len(sys.argv) > 1: 

					if sys.argv[1] == "shortcut":
						print("Ci sono {} gradi dentro casa con un'umidità del {}%. Fuori fa {} gradi con un'umidità del {}%."
							.format(indoor, indoor_humidity, outdoor2, outdoor, outdoor_humidity))

					elif sys.argv[1] == "shortcut_stats":
						print("La temperatura minima dentro casa è stata di {} gradi, mentre la massima {} gradi. Fuori la minima è stata di {} gradi e la massima di {} gradi."
							.format(int(min_indoor), int(max_indoor), int((min_outdoor+min_outdoor2)/2), int((max_outdoor+max_outdoor2)/2) ))

					elif sys.argv[1] == "battery": 
						cmd = "sudo gatttool -b {} -t random --char-read --handle=0x0031".format(WEATHERSTATION_MAC)
						output = check_output(cmd, shell=True)
						n = int(''.join(filter(str.isdigit, output)))
						print("Battery charge: {}%".format(n))
				else:
					print('***INDOOR***')
					print('Indoor temp : {}°C, max : {}°C, min : {}°C'.format(indoor, max_indoor, min_indoor))
					print('Indoor humidity : {}%, max : {}%, min : {}%'.format(indoor_humidity, max_indoor_humidity, min_indoor_humidity))

					print('\n***OUTDOOR***')
					print('Outdoor temp : {}°C, max : {}°C, min : {}°C'.format(outdoor, max_outdoor, min_outdoor))
					print('Outdoor temp 2 : {}°C, max : {}°C, min : {}°C'.format(outdoor2, max_outdoor2, min_outdoor2))
					print('Average outdoor temperature: {}°C'.format(avg_outdoor_temp))
					print('Outdoor humidity : {}%, max : {}%, min : {}%'.format(outdoor_humidity, max_outdoor_humidity, min_outdoor_humidity))
					print('Dew point: {}°C'.format(dewpoint))

			else:
				logging.error('No data received from WeatherStation')
			
			weatherStation.disconnect()
	
		except KeyboardInterrupt:
			logging.info('Program stopped by user')
