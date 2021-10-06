'''
 This file 

'''
import logging
import urllib.parse
import requests
import datetime
import argparse
import json
import jwt
import pytz

import time
import math


class API(object):

    def __init__(self, clientid=None, clientsecret=None,username=None, password=None,timezone=None):
        assert clientid is not None
        assert clientsecret is not None

        self.clientid = clientid
        self.clientsecret = clientsecret
        self.username = username
        self.password = password
        self.timezone = timezone


        self.session = requests.Session()

    def unparse(self, obj):
        return obj

    def parse(self, string):
        return string

    def buildRequestHeader(self):
        header = {"Authorization": "Bearer " + self.access_token}
        return header

    def device_list(self):
        devices = []
        headers = {"Authorization": "Bearer " + self.access_token}
        resp = requests.request('GET', 'https://api.flumetech.com/users/' + str(self.user_id) + '/devices', headers=headers) 
        dataJSON = json.loads(resp.text)
        logging.debug("Executed device search")
    
        if dataJSON["http_code"] == 200:
            for bridge in dataJSON["data"]:
                logging.debug("JSON Data from device")
                logging.debug(dataJSON["data"])
                if bridge["type"] == 2:
                    devices.append(bridge["id"])
        return devices

    def device_query(self, device_id, all=False, refresh=False):
        result = []
        
        # remove timezone , need to make sure tomezone on FLUME is correct

        if self.timezone :
            now = datetime.datetime.now(pytz.timezone(self.timezone))
        else :
            now = datetime.datetime.now()

        current_min= now.strftime('%Y-%m-%d %H:%M:00')
        previous_min = (now - datetime.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:00')
        current_month =  now.strftime('%Y-%m-01 00:00:00')

        payload = '{"queries":[{"request_id":"perminute","bucket":"MIN","since_datetime":"' + previous_min + '","until_datetime":"' + current_min + '","group_multiplier":"1","operation":"SUM","sort_direction":"ASC","units":"GALLONS"}, {"request_id":"currentmonth","bucket":"MON","since_datetime":"' + current_month + '", "operation":"SUM"}]}'
        logging.debug(payload)
        headers = {"Authorization": "Bearer " + self.access_token}
        headers["content-type"] = "application/json"
        resp = requests.request("POST", "https://api.flumetech.com/users/" + str(self.user_id)  + "/devices/" + str(device_id)  + "/query", data=payload, headers=headers)
        data = json.loads(resp.text)
        logging.debug(data)
        if data["http_code"]==200:
            result.append(data["data"][0]["perminute"][0]["value"])
            result.append(data["data"][0]["currentmonth"][0]["value"])
            return result
        else:
            return None

    def credentials(self): 
        # get the credential
        url = "https://api.flumetech.com/oauth/token"
        payload = '{"grant_type":"password","client_id":"' + self.clientid + '","client_secret":"' + self.clientsecret + '","username":"' + self.username + '","password":"' + self.password + '"}'
        headers = {'content-type': 'application/json'}

        logging.debug("Post to server: " + payload)
        resp = requests.request("POST", url, data=payload, headers=headers)
        logging.debug("response from server: " + resp.text)
        dataJSON = json.loads(resp.text)

        if dataJSON["http_code"] == 200:
            logging.debug("Got 200 response from auth token request")
            self.access_token = dataJSON["data"][0]["access_token"]
            self.refresh_token = dataJSON["data"][0]["refresh_token"]
        else:
            quit("Failed to get credential")
        return

    def userid(self): 
        decoded = jwt.decode(self.access_token, options={"verify_signature": False})
        self.user_id = decoded["user_id"]
        logging.debug(decoded)

        return
