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


'''
class Device(object):

    _PAIRS = (
            ("clientsecret", "Client_Secret"),
            ("clientid", "Client_ID"),
            ("username", "Username"),
            ("password", "Password")

#    @classmethod
    def from_xml(cls, x):
        kwargs = {}
        for attr, tag_name in cls._PAIRS:
            tag = x.find(tag_name)
            if tag is not None:
                kwargs[attr] = tag.text
        return cls(**kwargs)

    def __init__(self, clientid=None, clientsecret=None,
        username=None, password=None):

        self.clientid = clientid
        self.clientsecret = clientsecret
        self.username = username
        self.password = password

class Component(object):

    _PAIRS = (
            ("clientid", "ClientID"),
            ("clientsecret", "ClientSecret"))

    @classmethod
    def from_xml(cls, x):
        kwargs = {}
        for attr, tag_name in cls._PAIRS:
            tag = x.find(tag_name)
            if tag is not None:
                kwargs[attr] = tag.text
        variables = []
        vars_tag = x.find("Variables")
        if vars_tag:
            for var_tag in vars_tag.findall("Variable"):
                variables.append(Variable.from_xml(var_tag))
        kwargs["variables"] = variables
        return cls(**kwargs)

    def __init__(self, clientid=None, clientsecret=None,
        username=None, password=None):

        self.clientid = clientid
        self.clientsecret = clientsecret
        self.username = username
        self.password = password

'''


class Variable(object):

    _PAIRS = (
            ("name", "Name"),
            ("value", "Value"),
            ("units", "Units"),
            ("description", "Description"))

    @classmethod
    def from_xml(cls, x):
        # This happens in device_details
        text = x.text.strip()
        if text:
            return text
        kwargs = {}
        for attr, tag_name in cls._PAIRS:
            tag = x.find(tag_name)
            if tag is not None:
                kwargs[attr] = tag.text
        return cls(**kwargs)

    def __init__(self, name=None, value=None, units=None, description=None):
        self.name = name
        self.value = value
        self.units = units
        self.description = description


class DeviceComponents(object):

    def __init__(self, device, components):
        self.device = device
        self.components = components


class API(object):

    def __init__(self, clientid=None, clientsecret=None,username=None, password=None, tokenfile=None):
        assert clientid is not None
        assert clientsecret is not None

        self.clientid = clientid
        self.clientsecret = clientsecret
        self.username = username
        self.password = password
        self.tokenfile = tokenfile

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

        now = datetime.datetime.now(pytz.timezone('US/Pacific'))
        current_min= now.strftime('%Y-%m-%d %H:%M:00')
        previous_min = (now - datetime.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:00')
        current_month =  now.strftime('%Y-%m-01 00:00:00')

        payload = '{"queries":[{"request_id":"perminute","bucket":"MIN","since_datetime":"' + previous_min + '","until_datetime":"' + current_min + '","group_multiplier":"1","operation":"SUM","sort_direction":"ASC","units":"GALLONS"}, {"request_id":"currentmonth","bucket":"MON","since_datetime":"' + current_month + '", "operation":"SUM"}]}'
        logging.debug(payload)
        #headers = buildRequestHeader(self);
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

            if self.tokenfile:
                outline = {}
                outline["access_token"] = self.access_token
                outline["refresh_token"] = self.refresh_token
                f = open(self.tokenfile, "w")
                f.write(json.dumps(outline))
                f.close()
        else:
            quit("failed to obtain creds")    

        return

    def userid(self): 
        decoded = jwt.decode(self.access_token, options={"verify_signature": False})
        self.user_id = decoded["user_id"]
        logging.debug(decoded)

        return

