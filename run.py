from oebb_checker.requestor import Requestor
from datetime import datetime

requestor = Requestor()
station_src = requestor.stations('Wien Hbf')   
station_dst = requestor.stations('Krakow')  
doi = '2023-08-09'
lines = requestor.connections(station_src.pop(0), station_dst.pop(0), date=datetime.strptime(doi, '%Y-%m-%d'))
print(doi)
for line in lines:
    print(line)