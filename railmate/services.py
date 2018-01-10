# calls to the NS API go here
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET

class NS:
    def station_list(self):
        API = 'http://webservices.ns.nl/ns-api-stations-v2?'
        username = 'g.buntinx@student.tue.nl'
        password = 'EyccWJlIkL27BLh3On8zrRMiie_Z3r-WQAjDaZMBA93sD15cEAWT7A'
        data = requests.get(API, auth=HTTPBasicAuth(username, password))        # response is in XML format
        root = ET.fromstring(data.content)  # obtain XML format and store in variable to parse

        station_list = []

        for station in root:
            code = station.find('Code').text
            station_name = station.find('Namen/Lang').text

            station_list.append({'code':code, 'name':station_name})
        return station_list

