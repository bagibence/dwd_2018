from datetime import date
from pony.orm import *


db = Database()


class Station(db.Entity):
    stations_id = PrimaryKey(int, auto=True)
    von_datum = Optional(date)
    bis_datum = Optional(date)
    stationshoehe = Optional(int)
    geoBreite = Optional(float)
    geoLaenge = Optional(float)
    stationsname = Required(str)
    bundesland = Optional(str)
    measurements = Set('Hourly_Measurement')


class Hourly_Measurement(db.Entity):
    mess_datum = Required(str)
    stations_id = Required(Station)
    air_temp = Optional(float)  # quality level of next columns
    wind_speed = Optional(float)
    humidity = Optional(float)
    precipation_bin = Optional(int)
    precipation_mm = Optional(float)
    wind_direction = Optional(float)
    cloudiness_cover = Optional(float)
    cloud_type_L1 = Optional(float)
    cloud_height_L1 = Optional(float)
    cloud_cover_L1 = Optional(float)
    cloud_type_L2 = Optional(float)
    cloud_height_L2 = Optional(float)
    cloud_cover_L2 = Optional(float)
    sun_duration = Optional(float)
    visibility = Optional(float)
    sum_longwave = Optional(float)
    sum_diffuse_solar = Optional(float)
    sum_solar_duration = Optional(float)
    zenith_angle = Optional(float)
    PrimaryKey(mess_datum, stations_id)



db.generate_mapping()
