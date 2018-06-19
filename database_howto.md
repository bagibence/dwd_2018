# Running Jupyter notebook on the server and connecting to it

1. Fire up the VPN and login to the server
2. Start a notebook server: `jupyter notebook --no-browser --ip=0.0.0.0`
3. See which port it started on and copy the token if you get one. Typically `8888`
3. Open a browser and go to: `http://pcp2018.bccn-berlin.pri:8888` (replace `8888` with the port your server is running on)
4. Enter your password or paste the token the jupyter notebook server gave you

---


# Using the database module

First of all login to the server

### Import the database module and set up a connection to the database

```python
import database as db
db.set_up_connection(db.db, database_name, user=your_database_user)
```

typically `database_name` would be `db_weather`, user is your database user (e.g. `bence` or `webscrapers`)

### Writing queries

The tables we have are in the database.py.
<br>
They are `station, dailymeasurement, hourlymeasurement, dailyprediction, hourlyprediction, dailyperiodprediction`.

Two ways of selecting from tables:

```python
# select stations whose name contains Berlin
query1 = db.porm.select(s for m in db.Station if 'Berlin' in s.stationsname)
query2 = db.Station.select(lambda s: 'Berlin' in s.stationsname)
```

These give you pony queries. You can loop through them to access the objects (Station objects in this case) or turn them into a list by `query1[:]`.

Normally you should be able to put these results into a pandas DataFrame by

```python
pd.read_sql_query(query1.get_sql(), db.conn_url)
```
