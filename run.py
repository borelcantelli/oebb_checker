from oebb_checker.requestor import Requestor
from datetime import datetime
from constants import get_access_token

__ACCESS_TOKEN__ = None

if __name__ == '__main__':
    __ACCESS_TOKEN__ = get_access_token()
    requestor = Requestor(access_token=__ACCESS_TOKEN__)
    station_src = requestor.stations('Wien Hbf')   
    station_dst = requestor.stations('Krakow Glowny')  
    doi = ['2023-09-13 08:00:00', '2023-09-14 08:00:00', '2023-09-15 08:00:00']
    for date in doi:
        print(date)
        lines = requestor.connections(station_src[0], station_dst[0], date=datetime.strptime(date, '%Y-%m-%d %H:%M:%S'))
        scroll = requestor.connections(station_src[0], station_dst[0], date=datetime.strptime(date, '%Y-%m-%d %H:%M:%S'))
        for line in lines:
            print(line)