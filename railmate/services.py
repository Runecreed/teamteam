# calls to the NS API go here
import datetime
import requests, sys
from django.core.exceptions import ValidationError
from django.db.models import Q
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
from xmljson import parker, Parker
import json
import collections, types

from railmate.models import Message
from railmate.signals import message_sent, message_read


class NS:
    _username = 'g.buntinx@student.tue.nl'
    _password = 'EyccWJlIkL27BLh3On8zrRMiie_Z3r-WQAjDaZMBA93sD15cEAWT7A'

    def station_list(self):
        station_list = []
        API = 'http://webservices.ns.nl/ns-api-stations-v2?'

        data = requests.get(API, auth=HTTPBasicAuth(self._username, self._password))  # response is in XML format
        if not data:
            return station_list

        root = ET.fromstring(data.content)  # obtain XML format and store in variable to parse
        for station in root:
            code = station.find('Code').text
            station_name = station.find('Namen/Lang').text

            station_list.append({'code': code, 'name': station_name})
        return station_list

    # NOTE: parameters should be a list of parameters
    def trip_list(self, parameters):
        API = "http://webservices.ns.nl/ns-api-treinplanner?"

        query = ''
        for key, value in parameters.items():
            query = query + key + '=' + value + '&'

        # query = "fromStation=" + source + "&toStation=" + destination  # It might be that SPACES need to converted to + in the query, but probably already taken care of
        data = requests.get(API + query,
                            auth=HTTPBasicAuth(self._username, self._password))  # response is in XML format

        # TODO: Properly handle the data, for now lets see what we get
        list = []
        jsonDataString = json.dumps(parker.data(ET.fromstring(
            data.content)))  # Parker parses all options into a list of tuples under 'Reismogelijkheid: [ ... , {'keys': 'values', .. }, {...} ]
        jsonData = json.loads(jsonDataString)
        try:  # Unpack data, gracefully exit if we have an error here (NS API can have various types of retrieval, list, tuple, dict,
            partialTrip = jsonData['ReisMogelijkheid'][0]['ReisDeel']  # get trip info (can be single element or a list)
            if type(partialTrip) is dict:
                partialTrip = [ partialTrip ]  # always use lists here even if single element for consistency

            for trip in partialTrip:
                for station in trip['ReisStop']:  # for all trips in the partial trip list (or single trip element
                    if station['Naam'] not in list:  # see if it's in the list already
                        list.append(station['Naam'])  # add it if not present (order matters)

        except Exception as e:  # data was not useful (empty trip, or issues with the API)
            jsonData = {"ReisMogelijkheid": 'none'}
            print(
                "Error occured looking for trip information, possibly no trip data for the source/destination combo --- message below")
            print(e)
            pass  # continue without data

        # example json Data: {"ReisMogelijkheid": [{"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "0:59", "VertrekVertraging": "+2 min", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-12T22:00:00+0100", "ActueleVertrekTijd": "2018-01-12T22:02:00+0100", "GeplandeAankomstTijd": "2018-01-12T23:01:00+0100", "ActueleAankomstTijd": "2018-01-12T23:01:00+0100", "Status": "VERTRAAGD", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2977, "Status": "VERTRAAGD", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-12T22:00:00+0100", "VertrekVertraging": "+2 min", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-12T22:17:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-12T22:31:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-12T22:47:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-12T23:01:00+0100", "Spoor": 1}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-12T22:30:00+0100", "ActueleVertrekTijd": "2018-01-12T22:30:00+0100", "GeplandeAankomstTijd": "2018-01-12T23:31:00+0100", "ActueleAankomstTijd": "2018-01-12T23:31:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2979, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-12T22:30:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-12T22:47:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-12T23:01:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-12T23:17:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-12T23:31:00+0100", "Spoor": 3}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-12T23:00:00+0100", "ActueleVertrekTijd": "2018-01-12T23:00:00+0100", "GeplandeAankomstTijd": "2018-01-13T00:01:00+0100", "ActueleAankomstTijd": "2018-01-13T00:01:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2981, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-12T23:00:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-12T23:17:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-12T23:31:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-12T23:47:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T00:01:00+0100", "Spoor": 1}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-12T23:30:00+0100", "ActueleVertrekTijd": "2018-01-12T23:30:00+0100", "GeplandeAankomstTijd": "2018-01-13T00:31:00+0100", "ActueleAankomstTijd": "2018-01-13T00:31:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2983, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-12T23:30:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-12T23:47:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-13T00:01:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-13T00:17:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T00:31:00+0100", "Spoor": 1}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "0:57", "VertrekVertraging": "+7 min", "AankomstVertraging": "+3 min", "Optimaal": true, "GeplandeVertrekTijd": "2018-01-13T00:00:00+0100", "ActueleVertrekTijd": "2018-01-13T00:07:00+0100", "GeplandeAankomstTijd": "2018-01-13T01:01:00+0100", "ActueleAankomstTijd": "2018-01-13T01:04:00+0100", "Status": "VERTRAAGD", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2985, "Status": "VERTRAAGD", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-13T00:00:00+0100", "VertrekVertraging": "+7 min", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-14T00:17:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-14T00:31:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-14T00:47:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T01:01:00+0100", "VertrekVertraging": "+3 min", "Spoor": "4b"}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-13T07:30:00+0100", "ActueleVertrekTijd": "2018-01-13T07:30:00+0100", "GeplandeAankomstTijd": "2018-01-13T08:31:00+0100", "ActueleAankomstTijd": "2018-01-13T08:31:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2919, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-13T07:30:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-13T07:47:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-13T08:01:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-13T08:17:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T08:31:00+0100", "Spoor": 1}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-13T08:00:00+0100", "ActueleVertrekTijd": "2018-01-13T08:00:00+0100", "GeplandeAankomstTijd": "2018-01-13T09:01:00+0100", "ActueleAankomstTijd": "2018-01-13T09:01:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 821, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-13T08:00:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-13T08:17:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-13T08:31:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-13T08:47:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T09:01:00+0100", "Spoor": 1}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-13T08:30:00+0100", "ActueleVertrekTijd": "2018-01-13T08:30:00+0100", "GeplandeAankomstTijd": "2018-01-13T09:31:00+0100", "ActueleAankomstTijd": "2018-01-13T09:31:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2923, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-13T08:30:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-13T08:47:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-13T09:01:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-13T09:17:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T09:31:00+0100", "Spoor": 1}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-13T09:00:00+0100", "ActueleVertrekTijd": "2018-01-13T09:00:00+0100", "GeplandeAankomstTijd": "2018-01-13T10:01:00+0100", "ActueleAankomstTijd": "2018-01-13T10:01:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2925, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-13T09:00:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-13T09:17:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-13T09:31:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-13T09:47:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T10:01:00+0100", "Spoor": 1}]}}, {"AantalOverstappen": 0, "GeplandeReisTijd": "1:01", "ActueleReisTijd": "1:01", "Optimaal": false, "GeplandeVertrekTijd": "2018-01-13T09:30:00+0100", "ActueleVertrekTijd": "2018-01-13T09:30:00+0100", "GeplandeAankomstTijd": "2018-01-13T10:31:00+0100", "ActueleAankomstTijd": "2018-01-13T10:31:00+0100", "Status": "VOLGENS-PLAN", "ReisDeel": {"Vervoerder": "NS", "VervoerType": "Intercity", "RitNummer": 2927, "Status": "VOLGENS-PLAN", "ReisStop": [{"Naam": "Eindhoven", "Tijd": "2018-01-13T09:30:00+0100", "Spoor": 1}, {"Naam": "Weert", "Tijd": "2018-01-13T09:47:00+0100"}, {"Naam": "Roermond", "Tijd": "2018-01-13T10:01:00+0100"}, {"Naam": "Sittard", "Tijd": "2018-01-13T10:17:00+0100"}, {"Naam": "Maastricht", "Tijd": "2018-01-13T10:31:00+0100", "Spoor": 1}]}}]}
        return {'trips': jsonData["ReisMogelijkheid"],
                'station_intermediate': list}  # returns a list of possible trips that go from source to destination, with a lot of info




class MessagingService(object):
    """
    A object to manage all messages and conversations
    """

    # Message creation

    def send_message(self, sender, recipient, message):
        """
        Send a new message
        :param sender: user
        :param recipient: user
        :param message: String
        :return: Message and status code
        """

        if sender == recipient:
            raise ValidationError("You can't send messages to yourself.")

        message = Message(sender=sender, recipient=recipient, content=str(message))
        message.save()

        message_sent.send(sender=message, from_user=message.sender, to=message.recipient)

        # The second value acts as a status value
        return message, 200

    # Message reading
    def get_unread_messages(self, user):
        """
        List of unread messages for a specific user
        :param user: user
        :return: messages
        """
        return Message.objects.all().filter(recipient=user, read_at=None)

    def read_message(self, message_id):
        """
        Read specific message
        :param message_id: Integer
        :return: Message Text
        """
        try:
            message = Message.objects.get(id=message_id)
            self.mark_as_read(message)
            return message.content
        except Message.DoesNotExist:
            return ""

    def read_message_formatted(self, message_id):
        """
        Read a message in the format <User>: <Message>
        :param message_id: Id
        :return: Formatted Message Text
        """
        try:
            message = Message.objects.get(id=message_id)
            self.mark_as_read(message)
            return message.sender.username + ": "+message.content
        except Message.DoesNotExist:
            return ""

    # Conversation management

    def get_conversations(self, user):
        """
        Lists all conversation-partners for a specific user
        :param user: User
        :return: Conversation list
        """
        all_conversations = Message.objects.all().filter(Q(sender=user) | Q(recipient=user))

        contacts = []
        for conversation in all_conversations:
            if conversation.sender != user:
                contacts.append(conversation.sender)
            elif conversation.recipient != user:
                contacts.append(conversation.recipient)

        # To abolish duplicates
        return list(set(contacts))

    def get_conversation(self, user1, user2, limit=None, reversed=False, mark_read=False):
        """
        List of messages between two users
        :param user1: User
        :param user2: User
        :param limit: int
        :param reversed: Boolean - Makes the newest message be at index 0
        :return: messages
        """
        users = [user1, user2]

        # Newest message first if it's reversed (index 0)
        if reversed:
            order = '-pk'
        else:
            order = 'pk'
        conversation = Message.objects.all().filter(sender__in=users, recipient__in=users).order_by(order)
        if limit:
            # Limit number of messages to the x newest
            conversation = conversation[:limit]

        if mark_read:
            for message in conversation:
                # Just to be sure, everything is read
                self.mark_as_read(message)

        return conversation

    # Helper methods
    def mark_as_read(self, message):
        """
        Marks a message as read, if it hasn't been read before
        :param message: Message
        """

        if message.read_at is None:
            message.read_at = datetime.datetime.now()
            message_read.send(sender=message, from_user=message.sender, to=message.recipient)
            message.save()