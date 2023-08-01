import datetime as dt

class Station:
    def __init__(self, station_info) -> None:
        necessary_keys = ['number', 'longitude', 'latitude', 'name', 'meta']
        assert all(key in station_info.keys() for key in necessary_keys), "missing one of ['number', 'longitude', 'latitude', 'name', 'meta'] in station info"
        self.name = station_info['name'] if station_info['name'] else station_info['meta']
        self.number = station_info['number']
        self.long = station_info['longitude'] / 1e6
        self.lat = station_info['latitude'] /1e6
        self.meta = station_info['meta']
        self.station_dict = station_info

    def get_coords(self, cardinal=False) -> tuple:
        if cardinal:
            return (f'{self.lat} N', f'{self.long} E')
        else:
            return (self.lat, self.long)
        
    def __str__(self) -> str:
        return self.name if self.name else self.meta
    
    def __repr__(self) -> str:
        return self.name if self.name else self.meta

class Section:
    def __init__(self, src_name, dst_name, duration, departure_time, arrival_time, train_id, train_direction) -> None:
        from oebb_checker.requestor import Requestor
        self.requestor = Requestor()
        self.src_station = src_name
        self.dst_station = dst_name
        self.duration = duration
        self.departure = dt.datetime.fromisoformat(departure_time)
        self.arrival = dt.datetime.fromisoformat(arrival_time)
        self.train_id = train_id
        self.train_direction = train_direction
    
    def _pretty_time(self, time):
        return dt.date.strftime(time, '%T')
    
    def _format_duration(self, time):
        hours = time / 3600000
        return hours

    def __str__(self):
        return f'{self.src_station} ({self._pretty_time(self.departure)}) --({self.train_id} {self.duration}hrs)-> {self.dst_station} ({self._pretty_time(self.arrival)})'
    
    def __repr__(self):
        return f'{self.src_station} ({self._pretty_time(self.departure)}) --({self.train_id} {self.duration}hrs)-> {self.dst_station} ({self._pretty_time(self.arrival)})'

class Line:
    def __init__(self, line_info, section_list):
        self.sections = []
        for section in section_list:
            s = Section(src_name=section['from']['name'], dst_name=section['to']['name'], duration = self._format_duration(section['duration']), 
                        departure_time=section['from']['departure'], arrival_time=section['to']['arrival'],
                        train_id=section['category']['name'] + section['category']['number'], train_direction=section['category']['direction'])
            self.sections.append(s)
        
        self.id = line_info['id']
        self.num_switches = line_info['switches']
        self.duration = round(self._format_duration(line_info['duration']), 2)
        self.line_info = line_info
        self.price = self._get_price()

    def _format_duration(self, time):
        hours = float(time) / 3600000
        return hours
    
    def _get_price(self):
        from oebb_checker.requestor import Requestor
        r = Requestor()
        offer = r.prices([self.line_info])
        return offer
    
    def __str__(self):
        return f"Euro: {self.price}, connections: {self.num_switches}: {', '.join([str(section) for section in self.sections])}"
    
    def __repr__(self):
        return f"{self.price}, connections: {self.num_switches}: {', '.join([str(section) for section in self.sections])}"