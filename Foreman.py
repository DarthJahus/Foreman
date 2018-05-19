#!/usr/bin/python
#coding=utf-8

import requests, json, socket
import time, os
from datetime import datetime
import urllib3; urllib3.disable_warnings()


# Constants
__version__ = 0.4
__debug = False
__request_timeout = 10                 # Timeout for HTTP requests
__sleep_success = 180                  # Time before rechecking the miner if the operation (get_data+send) is successful
__sleep_failure_min = 10               # Used as a base for retries AND as a retry time when server can't be reached
__sleep_failure_max = __sleep_success  # When miner check fails, the waited time will increase until it hits the the max
__max_tries = 3                        # Max retries before giving up on an operation


def load_file_json(file_name):
	with open(file_name, 'r') as _file:
		content = _file.read()
		content_dict = json.loads(content)
		_file.close()
		return content_dict


# Config
__config = load_file_json("config.json")

# Variables
clear_order = True


def contact_miner(command, ip, port, psw=None, timeout=10):
	__miner_commands = {
		"stats": "miner_getstat1",
		"restart": "miner_restart",
		"reboot": "miner_reboot"
	}
	try:
		assert command in __miner_commands
		#
		data = {"jsonrpc": "2.0", "id": 0, "method": __miner_commands[command]}
		if psw is not None: data["psw"] = psw.encode("ascii")
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(timeout)
		s.connect((ip, port))
		data = bytearray(str(data).replace('\'', '\"'), "ascii")
		s.sendall(data)
		res = s.recv(1024)
		s.close()
		if res == '':
			return {"success": False, "message": "No data received."}
		else:
			return {"success": True, "result": json.loads(res.decode("utf-8"))["result"]}
	except AssertionError:
		return {"success": False, "message": "Invalid command."}
	except socket.error:
		return {"success": False, "message": "Can't establish a connection."}


def handle_stats(stats):
	if not stats["success"]:
		return {"success": False, "message": "No stats available"}
	else:
		_result = stats["result"]
		print(_result)
		result_dict = {
			"version": _result[0],
			"uptime": _result[1],
			"primary_hash_total": int(_result[2].split(";")[0]),  # kH/s
			"primary_shares_total": int(_result[2].split(";")[1]),
			"primary_rejected_total": int(_result[2].split(";")[2]),
			"primary_hash_gpu": _result[3].split(";"),  # kH/s,
			"dual_hash_total": int(_result[4].split(';')[0]),  # kH/s
			"dual_shares_total": int(_result[4].split(';')[1]),
			"dual_rejected_total": int(_result[4].split(';')[2]),
			"dual_hash_gpu": _result[5].split(';'),  # kH/s, OFF if no DCR
			"gpu_temp": _result[6].split(';')[::2],
			"gpu_fan": _result[6].split(';')[1::2],
			"pool_current": _result[7].split(';'),  # array of [primary, dual]
			"primary_invalid_total": int(_result[8].split(';')[0]),
			"primary_pool_switches": int(_result[8].split(';')[1]),
			"dual_invalid_total": int(_result[8].split(';')[2]),
			"dual_pool_switches": int(_result[8].split(';')[3])
		}
		return {"success": True, "result": result_dict}


def try_send_data(data):
	global clear_order
	# build data
	_data = {
		"user": __config["user"]["id"],
		"key": __config["user"]["key"],
		"params": __config["params"], # these are optional
		"timestamp": time.time(),
		"clear_order": clear_order,
		"version": __version__,
		"data": data
	}
	# send data
	i = 0
	_req = None
	_message = "Unknown error"
	while i < __max_tries:
		try:
			_req = requests.post(
				url=__config["user"]["server"],
				data=json.dumps(_data),
				headers={"content-type": "application/json", "connection": "close"},
				timeout=__request_timeout,
				verify=False
			)
			if _req.status_code == 200:
				i = __max_tries
				print(">>> ORDER = '%s'" % _req.text)
				_order = _req.text
				if not (_order is None or _order == ""):
					if _order == "cleared":
						clear_order = False
					else:
						execute_order(_order)
			else:
				i += 1
				if i < __max_tries: time.sleep(int(__sleep_failure_min/__max_tries)+1)
		except requests.exceptions.Timeout:
			_message = "Connection timed out."
		except requests.ConnectionError:
			_message = "Can not establish a connection with remote server."
		except:
			print("Unhandled error.")
			_message = "Unhandled error."
	# Return status
	if _req is None:
		return {"success": False, "message": _message}
	else:
		if _req.status_code != 200:
			return {"success": False, "message": "Sorry, couldn't send the message. Error: %s" % _req.status_code}
		else:
			return {"success": True, "result": "Data sent correctly!"}


def try_get_data():
	_max_tries = __max_tries
	i = 0
	_data = {"success": False, "message": "Something went really, really wrong."}
	while i < _max_tries:
		if __debug: print("Loading...")
		_data = handle_stats(contact_miner("stats", __config["miner"]["ip"], __config["miner"]["port"], psw=__config["miner"]["pass"], timeout=__request_timeout))
		if __debug: print("+++ tried: %i" % (i + 1))
		if _data["success"]:
			i = _max_tries
		else:
			i += 1
			if i < _max_tries: time.sleep(int(__sleep_failure_min / _max_tries) + 1)
	return _data


def execute_order(order):
	global clear_order
	_res = try_execute_order(order)
	if _res["success"]:
		clear_order = True


def try_execute_order(order):
	_max_tries = __max_tries
	i = 0
	_res = {"success": False, "message": "Something went really, really wrong."}
	while i < _max_tries:
		if __debug: print("Trying to execute order '%s'..." % order)
		_method = "restart"
		_pass = None
		if order == "reboot": _method = "reboot"
		if "pass" in __config["miner"]: _pass = __config["miner"]["pass"]
		_res = contact_miner(
			_method,
			__config["miner"]["ip"],
			__config["miner"]["port"],
			psw=_pass,
			timeout=__request_timeout
		)
		if _res["success"]:
			i = _max_tries
		else:
			i += 1
			if i < _max_tries: time.sleep(int(__sleep_failure_max / _max_tries) + 1)
	return _res


def main():
	# Variables
	_sleep_failure = __sleep_failure_min
	_fails = 0
	# loop
	while True:
		# Retrieve data from miner
		_data = try_get_data()
		# Check if data is good
		if _data["success"]:
			if __debug: print(_data["result"])
			# Clean
			_fails = 0
			_sleep_failure = __sleep_failure_min
			# Send the data to server
			_req = try_send_data(_data)
			if __debug: print(_req)
			# If data is sent, wait __sleep_success, else, consider as failure and try as fast as possible
			if _req["success"]:
				# Assume server cleaned the orders as requested
				print(
					"\nUpdated on %s\nWaiting %i seconds..."
					% (datetime.fromtimestamp(time.time()).strftime("%Y-%m-%dT%H:%M:%S"), __sleep_success)
				)
				time.sleep(__sleep_success)
			else:
				print(
					"\nMiner was available at %s but the server is unreachable.\nTrying to send data in %i seconds..."
					% (datetime.fromtimestamp(time.time()).strftime("%Y-%m-%dT%H:%M:%S"), __sleep_failure_min)
				)
				time.sleep(__sleep_failure_min)
		else:
			_fails += 1
			print(_data["message"])
			print("\nWaiting %i seconds..." % _sleep_failure)
			time.sleep(_sleep_failure)
			if _sleep_failure < __sleep_failure_max: _sleep_failure += __sleep_failure_min


if __name__ == "__main__":
	main()
