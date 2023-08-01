# modified from https://github.com/HerrHofrat/oebb/blob/master/oebb/oebb.py 
import requests
import json
from datetime import datetime
from time import time
import os
import logging

from oebb_checker.oebb import Station, Line
from oebb_checker.constants import USER_ID


_LOGGER = logging.getLogger(__name__)
p_request = requests.Session()

class Requestor:
    def __init__(self, cookie_keep_time=2300, auto_auth=True, access_token=None):
        self.session_keep_time = min(cookie_keep_time, 2300)
        self.session_expires = 0
        self.headers = {'Channel': 'inet', 'User-Agent' : 'Mozilla/5.0'}
        self.auto_auth = auto_auth
        self.access_token = access_token

    def stations(self, name=''):
        r = self._make_request('https://shop.oebbtickets.at/api/hafas/v1/stations',
                               params={'count': 15,
                                       'name': str(name)})
        if r.status_code == 200:
            return [Station(station) for station in json.loads(r.text)]
        else:
            raise requests.ConnectionError(f'Endpoint returned error {r.status_code}')

    def connections(self, origin, destination, date=datetime.now(), count=5, opt=None):
           
        # if origin['name'] == "":
        #      origin['name'] = origin['meta']
        # if destination['name'] == "":
        #      destination['name'] = destination['meta']

        default = {'sortType': 'DEPARTURE',
                   'datetimeDeparture': date.strftime("%Y-%m-%dT%H:%M:00.000"),
                   'entrypointId': 'timetable',
                   'filter': {'regionaltrains': False,
                              'direct': False,
                              'changeTime': False,
                              'wheelchair': False,
                              'bikes': False,
                              'trains': False,
                              'motorail': False,
                              'connections': []},
                   'passengers': [
                       {
                           'type': 'ADULT',
                           'id': 1658937617,
                           'me': False,
                           'remembered': False,
                           'challengedFlags': {
                               'hasHandicappedPass': False,
                               'hasAssistanceDog': False,
                               'hasWheelchair': False,
                               'hasAttendant': False
                           },
                           'relations': [],
                           'cards': [],
                           'isBirthdateChangeable': True,
                           'isBirthdateDeletable': True,
                           'isDeletable': True,
                           'isNameChangeable': True,
                           'isSelected': True,
                           'markedForDeath': False,
                           'nameChangeable': True,
                           'passengerDeletable': True,
                           'birthdateChangeable': True,
                           'birthdateDeletable': True,
                       }
                   ],
                   'count': count,
                   'debugFilter': {'noAggregationFilter': False,
                                   'noEqclassFilter': False,
                                   'noNrtpathFilter': False,
                                   'noPaymentFilter': False,
                                   'useTripartFilter': False,
                                   'noVbxFilter': False,
                                   'noCategoriesFilter': False},
                   'from': origin.station_dict,
                   'to': destination.station_dict,
                   'timeout': {}}
        if type(opt) == dict:
            default.update(opt)
        r = self._make_request('https://shop.oebbtickets.at/api/hafas/v4/timetable',
                               data=default)


        if r.status_code == 200:
            lines = json.loads(r.text)['connections']
            return [Line(line, line['sections'], self.access_token) for line in lines]
        else:
            raise requests.ConnectionError(f'Endpoint returned error {r.status_code}')

    def next_connections(self, connection, opt=None):
        default = {'connectionId': connection['id'],
                   'direction': 'after',
                   'count': 5,
                   'filter': {'regionaltrains': False,
                              'direct': False,
                              'changeTime': False,
                              'wheelchair': False,
                              'bikes': False,
                              'trains': False,
                              'motorail': False,
                              'droppedConnections': False}
                   }
        if type(opt) == dict:
            default.update(opt)
        r = self._make_request('https://shop.oebbtickets.at/api/hafas/v1/timetableScroll',
                               data=default)
        r = json.loads(r.text)
        return r['connections']

    def prices(self, connections):
        params = {'connectionIds[]': []}
        for connection in connections:
            params['connectionIds[]'].append(connection['id'])
        params['sortType'] = 'DEPARTING'
        params['bestPriceId'] = 'undefined'
        r = self._make_request('https://shop.oebbtickets.at/api/offer/v1/prices',
                               params=params)
        r = json.loads(r.text)
        return r['offers'][0]['price']

    def _make_request(self, url, data=None, params=None):
        if self.auto_auth and (int(time()) > self.session_expires):
            self.auth()
        if data is None:
            r = p_request.get(url, headers=self.headers, params=params)
        else:
            r = p_request.post(url, headers=self.headers, json=data)
        return r

    def auth(self):
        r = p_request.get('https://shop.oebbtickets.at/api/domain/v3/init',
                         headers=self.headers,
                         params={'userId': USER_ID})
        r = json.loads(r.text)
        self.headers.update({'AccessToken': self.access_token,
                             'SessionId': r['sessionId'],
                             'x-ts-supportid': r['supportId']})
        self.session_expires = int(time()) + self.session_keep_time

    @staticmethod
    def _generate_uid():
        s = os.urandom(7)
        return 'anonym-' + s[:4].hex() + '-' + s[4:6].hex() + '-' + s[6:].hex()

    @staticmethod
    def station_name(station):
        return station['name'] if station['name'] else station['meta']

    @staticmethod
    def get_datetime(text):
        return datetime.strptime(text[:-4], '%Y-%m-%dT%H:%M:%S')
    
    
    