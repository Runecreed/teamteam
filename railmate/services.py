# calls to the NS API go here
import requests, sys
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
from xmljson import parker, Parker
import json
import collections, types

class NS:
    _username = 'g.buntinx@student.tue.nl'
    _password = 'EyccWJlIkL27BLh3On8zrRMiie_Z3r-WQAjDaZMBA93sD15cEAWT7A'

    def station_list(self):
        API = 'http://webservices.ns.nl/ns-api-stations-v2?'

        data = requests.get(API, auth=HTTPBasicAuth(self._username, self._password))  # response is in XML format
        root = ET.fromstring(data.content)  # obtain XML format and store in variable to parse

        station_list = []

        for station in root:
            code = station.find('Code').text
            station_name = station.find('Namen/Lang').text

            station_list.append({'code': code, 'name': station_name})
        return station_list

    # NOTE: parameters should be a list of 2 elements  :: source -- destination, IN THAT ORDER
    def trip_list(self, parameters):
        API = "http://webservices.ns.nl/ns-api-treinplanner?"

        source = parameters[0]
        destination = parameters[1]

        query = "fromStation=" + source + "&toStation=" + destination  # It might be that SPACES need to converted to + in the query, but probably already taken care of
        data = requests.get(API + query,
                            auth=HTTPBasicAuth(self._username, self._password))  # response is in XML format

        # TODO: Properly handle the data, for now lets see what we get
        list = []
        jsonDataString = json.dumps(parker.data(ET.fromstring(
            data.content)))  # Parker parses all options into a list of tuples under 'Reismogelijkheid: [ ... , {'keys': 'values', .. }, {...} ]
        jsonData = json.loads(jsonDataString)
        try:  # see if the data is useful
            partialTrip = jsonData['ReisMogelijkheid'][0]['ReisDeel']  # get trip info (can be single element or a list)

            if type(partialTrip) is dict: # trip does not have transfers, single element, unfold stations
                for station in partialTrip['ReisStop']:
                  if station['Naam'] not in list:  # see if it's in the list already
                    list.append(station['Naam'])  # add it if not present (order matters)
            else:  # this dataset has transfers, so partialTrip is a LIST rather than an element, so iterate it
                for trip in partialTrip:
                    for station in trip['ReisStop']:  # for all trips in the partial trip list (or single trip element
                        if station['Naam'] not in list:  # see if it's in the list already
                            list.append(station['Naam'])  # add it if not present (order matters)

        except Exception as e:  # data was not useful
            jsonData = {"ReisMogelijkheid": "No trips possible"}
            print(
                "Error occured looking for trip information, possibly no trip data for the source/destination combo --- message below")
            print(e)
            pass  # continue without data

        # example json Data: {"ReisMogelijkheid": [{"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "0:59", "VertrekVertraging": "+2 min", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-12T22:00:00+0100", "ActueleVertrekTijd": "2018-01-12T22:02:00+0100", "GeplandeAankomstTijd": "2018-01-12T23:01:00+0100", "ActueleAankomstTijd": "2018-01-12T23:01:00+0100", "Status": "VERTRAAGD", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2977, "Status": "VERTRAAGD", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-12T22:00:00+0100", "VertrekVertraging": "+2 min", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-12T22:17:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-12T22:31:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-12T22:47:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-12T23:01:00+0100", "Spoor": 1}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-12T22:30:00+0100", "ActueleVertrekTijd": "2018-01-12T22:30:00+0100", "GeplandeAankomstTijd": "2018-01-12T23:31:00+0100", "ActueleAankomstTijd": "2018-01-12T23:31:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2979, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-12T22:30:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-12T22:47:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-12T23:01:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-12T23:17:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-12T23:31:00+0100", "Spoor": 3}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-12T23:00:00+0100", "ActueleVertrekTijd": "2018-01-12T23:00:00+0100", "GeplandeAankomstTijd": "2018-01-13T00:01:00+0100", "ActueleAankomstTijd": "2018-01-13T00:01:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2981, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-12T23:00:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-12T23:17:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-12T23:31:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-12T23:47:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T00:01:00+0100", "Spoor": 1}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-12T23:30:00+0100", "ActueleVertrekTijd": "2018-01-12T23:30:00+0100", "GeplandeAankomstTijd": "2018-01-13T00:31:00+0100", "ActueleAankomstTijd": "2018-01-13T00:31:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2983, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-12T23:30:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-12T23:47:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-13T00:01:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-13T00:17:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T00:31:00+0100", "Spoor": 1}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "0:57", "VertrekVertraging": "+7 min", "AankomstVertraging": "+3 min", "Optimaal": true, "GeplandeVertrekTijd": "2018-01-13T00:00:00+0100", "ActueleVertrekTijd": "2018-01-13T00:07:00+0100", "GeplandeAankomstTijd": "2018-01-13T01:01:00+0100", "ActueleAankomstTijd": "2018-01-13T01:04:00+0100", "Status": "VERTRAAGD", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2985, "Status": "VERTRAAGD", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-13T00:00:00+0100", "VertrekVertraging": "+7 min", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-14T00:17:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-14T00:31:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-14T00:47:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T01:01:00+0100", "VertrekVertraging": "+3 min", "Spoor": "4b"}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-13T07:30:00+0100", "ActueleVertrekTijd": "2018-01-13T07:30:00+0100", "GeplandeAankomstTijd": "2018-01-13T08:31:00+0100", "ActueleAankomstTijd": "2018-01-13T08:31:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2919, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-13T07:30:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-13T07:47:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-13T08:01:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-13T08:17:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T08:31:00+0100", "Spoor": 1}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-13T08:00:00+0100", "ActueleVertrekTijd": "2018-01-13T08:00:00+0100", "GeplandeAankomstTijd": "2018-01-13T09:01:00+0100", "ActueleAankomstTijd": "2018-01-13T09:01:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 821, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-13T08:00:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-13T08:17:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-13T08:31:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-13T08:47:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T09:01:00+0100", "Spoor": 1}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-13T08:30:00+0100", "ActueleVertrekTijd": "2018-01-13T08:30:00+0100", "GeplandeAankomstTijd": "2018-01-13T09:31:00+0100", "ActueleAankomstTijd": "2018-01-13T09:31:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2923, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-13T08:30:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-13T08:47:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-13T09:01:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-13T09:17:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T09:31:00+0100", "Spoor": 1}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-13T09:00:00+0100", "ActueleVertrekTijd": "2018-01-13T09:00:00+0100", "GeplandeAankomstTijd": "2018-01-13T10:01:00+0100", "ActueleAankomstTijd": "2018-01-13T10:01:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2925, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-13T09:00:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-13T09:17:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-13T09:31:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-13T09:47:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T10:01:00+0100", "Spoor": 1}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-13T09:30:00+0100", "ActueleVertrekTijd": "2018-01-13T09:30:00+0100", "GeplandeAankomstTijd": "2018-01-13T10:31:00+0100", "ActueleAankomstTijd": "2018-01-13T10:31:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2927, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-13T09:30:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-13T09:47:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-13T10:01:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-13T10:17:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T10:31:00+0100", "Spoor": 1}]}}]}
        return {'trips': jsonData["ReisMogelijkheid"],
                'station_intermediate': list}  # returns a list of possible trips that go from source to destination, with a lot of info
