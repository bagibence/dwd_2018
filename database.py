import pony.orm as porm
#import database
import datetime
import station_names
import getpass
import pandas as pd

from pony.orm.core import ObjectNotFound, TransactionIntegrityError


conn_url = 'postgresql://localhost:5432'
db = porm.Database()

class Station(db.Entity):
    stations_id   = porm.PrimaryKey(int, auto=False)
    von_datum     = porm.Optional(datetime.date)
    bis_datum     = porm.Optional(datetime.date)
    stationshoehe = porm.Optional(int)
    geobreite     = porm.Optional(float)
    geolaenge     = porm.Optional(float)
    stationsname  = porm.Required(str)
    bundesland    = porm.Optional(str)
    measurements  = porm.Set('DailyMeasurement')


    def in_city(self, cityname):
        return self.stationsname.lower().startswith(cityname.lower())


    @property
    def active(self):
        """Station was active in the last 4 weeks"""
        return self.bis_datum > (datetime.datetime.now().date() - datetime.timedelta(weeks = 4))


class DailyMeasurement(db.Entity):
    mess_datum  = porm.Required(datetime.date)
    stations_id = porm.Required(int)
    station     = porm.Optional(Station)
    qn_3        = porm.Optional(int)  # quality level of next columns
    fx          = porm.Optional(float)
    fm          = porm.Optional(float)
    qn_4        = porm.Optional(int)
    rsk         = porm.Optional(float)
    rskf        = porm.Optional(float)
    sdk         = porm.Optional(float)
    shk_tag     = porm.Optional(float)
    nm          = porm.Optional(float)
    vpm         = porm.Optional(float)
    pm          = porm.Optional(float)
    tmk         = porm.Optional(float)
    upm         = porm.Optional(float)
    txk         = porm.Optional(float)
    tnk         = porm.Optional(float)
    tgk         = porm.Optional(float)

    porm.PrimaryKey(mess_datum, stations_id)

    #import math
    #def before_insert(self):
    #    for x in self._columns_:
    #        if isinstance(getattr(self, x), float):
    #            if math.isnan((getattr(self, x))):
    #                setattr(self, x, None)
    #    self.station = Station[self.stations_id]

    #def after_insert(self):
    #    self.station = Station[self.stations_id]

    #def after_update(self):
    #    self.station = Station[self.stations_id]

class DailyPrediction(db.Entity):
    id                 = porm.PrimaryKey(int, auto=True)
    website            = porm.Required(str)
    city               = porm.Required(str)
    date_of_acquisition = porm.Required(datetime.date)
    date_for_which_weather_is_predicted = porm.Required(datetime.date)
    temperature_max    = porm.Required(float)
    temperature_min    = porm.Required(float)
    wind_speed         = porm.Optional(float, nullable=True)
    humidity           = porm.Optional(float, nullable=True)
    precipitation_per  = porm.Optional(float, nullable=True)
    precipitation_l    = porm.Optional(float, nullable=True)
    wind_direction     = porm.Optional(str, 3, nullable=True)
    condition          = porm.Optional(str, nullable=True)
    snow               = porm.Optional(float, nullable=True)
    UVI                = porm.Optional(int, unsigned=True)


class HourlyPrediction(db.Entity):
    id                  = porm.PrimaryKey(int, auto=True)
    website             = porm.Required(str)
    city                = porm.Required(str)
    date_of_acquisition = porm.Required(datetime.datetime)
    date_for_which_weather_is_predicted = porm.Required(datetime.datetime)
    temperature         = porm.Required(float)
    wind_speed          = porm.Optional(float)
    humidity            = porm.Optional(float)
    precipitation_per   = porm.Optional(float)
    precipitation_l     = porm.Optional(float)
    wind_direction      = porm.Optional(str, 3)
    condition           = porm.Optional(str)
    snow                = porm.Optional(float)
    UVI                 = porm.Optional(int, unsigned=True)


class DailyPeriodPrediction(db.Entity):
    id                  = porm.PrimaryKey(int, auto=True)
    website             = porm.Required(str)
    city                = porm.Required(str)
    date_of_acquisition = porm.Required(datetime.datetime)
    date_for_which_weather_is_predicted = porm.Required(str)
    temperature         = porm.Required(float)
    wind_speed          = porm.Optional(float)
    precipitation_per   = porm.Optional(float)
    precipitation_l     = porm.Optional(float)
    wind_direction      = porm.Optional(str, 3)
    condition           = porm.Optional(str)


@porm.db_session
def set_station_trigger(db):
    trigger_text = '''
    create or replace function set_station()
    returns trigger as '
    begin
        new.station := new.stations_id;
        return new;
    end;
    ' language plpgsql;

    drop trigger if exists set_station on dailymeasurement;
    create trigger set_station
    before insert
    on dailymeasurement
    for each row
    execute procedure set_station();
    '''

    db.execute(trigger_text)


def set_up_connection(db, db_name, user='', password=None, host='127.0.0.1', create_tables=False):
    '''
    Sets up a connection with the database server.
    Set create_tables to True if the tables don't exist.
    '''
    if password is None:
        password = getpass.getpass(prompt='postgres user password: ')
    db.bind(provider='postgres', user=user, password=password, host=host, database=db_name)
    db.generate_mapping(create_tables = create_tables)
    global conn_url
    conn_url = 'postgresql://{}:{}@{}:5432/{}'.format(user, password, host, db_name)
    if create_tables:
        set_station_trigger(db)


@porm.db_session
def _insert_without_pandas(df, table_name):
    table_obj = db.entities[table_name]
    pk = table_obj._pk_columns_

    if df.index.name is None:
        df_q = df.set_index(pk)
    else:
        df_q = df.copy()

    for i in df_q.index:
        try:
            table_obj[i]
        except ObjectNotFound:
            try:
                table_obj(**{**dict(zip(pk, i)),
                             **df_q.loc[i].to_dict()})
            except TypeError:
                table_obj(**{**{pk : i},
                             **df_q.loc[i].to_dict()})


@porm.db_session
def _insert_with_pandas(df, table_name, auto_id=False, overwrite=False):
    indices_to_keep = []
    rows_to_delete = []
    table_obj = db.entities[table_name]

    if df.index.name is None and not auto_id:
        df_q = df.set_index(table_obj._pk_columns_)
    else:
        df_q = df.copy()

    try:
        df_q.to_sql(table_name.lower(), conn_url, if_exists='append', index=not auto_id)
    except:
        for i in df_q.index:
            try:
                row = table_obj[i]

                if overwrite:
                    rows_to_delete.append(row)
                    indices_to_keep.append(i)

            except ObjectNotFound:
                indices_to_keep.append(i)

            except:
                print(i)

        if overwrite:
            table_obj.select(lambda x: x in rows_to_delete).delete(bulk = True)
            porm.commit()

        print('starting insert')
        df_to_insert = df_q.loc[indices_to_keep]
        df_to_insert.to_sql(table_name.lower(), conn_url, if_exists='append', index=not auto_id)


@porm.db_session
def insert_into_table(df, table_name, use_pandas=True, auto_id=False, overwrite=False):
    if use_pandas:
        _insert_with_pandas(df, table_name, auto_id, overwrite)
    else:
        _insert_without_pandas(df, table_name)


@porm.db_session
def query_to_dataframe(query):
    try:
        return pd.read_sql_query(query.get_sql(), conn_url)
    except:
        return pd.DataFrame([o.to_dict() for o in query]).reindex(columns = query.first()._columns_)
    
    
@porm.db_session
def update_station_dates(verbose=True):
    df = station_names.get_stations_dataframe()
    
    indices_to_keep = []
    table_obj = db.entities['Station']

    if df.index.name is None:
        df_q = df.set_index(table_obj._pk_columns_)
    else:
        df_q = df.copy()

    
    if verbose: print('updating dates')

    for i in df_q.index:
        try:
            row = table_obj[i]
            
            row.von_datum = df_q.loc[i].von_datum.date()
            row.bis_datum = df_q.loc[i].bis_datum.date()
            
        except ObjectNotFound:
            indices_to_keep.append(i)

        except:
            print(i)

    if verbose: print('inserting new stations...')

    df_to_insert = df_q.loc[indices_to_keep]
    df_to_insert.to_sql('station', conn_url, if_exists='append', index=True)

    if verbose: print('inserted {} new stations'.format(len(indices_to_keep)))
