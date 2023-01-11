# Dependencies 
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

##############################################
# Setup Database
engine = create_engine("sqlite:///D:\SurfsUp\Resources\hawaii.sqlite")

# reflect existing db and tables
Base = automap_base()
Base.prepare(autoload_with = engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement
################################################
session = Session(engine)

# Find the last date in the database
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

# Calculate the date 1 year previous from the last data point in db
prev_yr = dt.date(2017,8,23) - dt.timedelta(days=365)

session.close()
#################################################

# Create app
app = Flask(__name__)

# Flask routes
@app.route("/")
def homepage():
    print("List all available api routes.")
    return(
        f"Available Routes for Hawaii Weather Data:<br/><br>"
        f"--Precipitation Data for Previous Year: <a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation<a><br/>"
        f"--List of Stations: <a href=\"/api/v1.0/stations\">/api/v1.0/stations<a><br/>"
        f"--Temperature Observations for Most- Active Station (Previous Year): <a href=\"/api/v1.0/tobs\">/api/v1.0/tobs<a><br/>"
        f"--Min, Max, and Avg Temperatures for Start Date: /api/v1.0/trip/yyyy-mm-dd/yyyy-mm-dd<br>"
        f"--Min, Max, and Avg Tempratures for given start and end date: <a href=\"/api/v1.0/min_max_avg/&lt;start date&gt;/&lt;end date&gt;<br/>"        
    )

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Return dictionary for date and precipitation info")

# Create session
    session = Session(engine)

# Query prcp and date values (last 12 months)

    data = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date).all()

# Convert the query results to a dictionary using date as the key and prcp as the value ---
    prcp_date = [] 

    for date, prcp in prcp:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_date.append(prcp_dict)
       
    session.close()

# Return the JSON representation of your dictionary.
    return jsonify(prcp_dict)

### Station Route
@app.route("/api/v1.0/stations")
def stations():
    print("Return a list of all stations")
# Create session
    session = Session(engine)

    stations = {}

    # Query all stations
    results = session.query(Station.station, Station.name).all()
    for stations, name in results:
        stations[stations] = name

    session.close()
 
    return jsonify(stations)

### Tobs Route
@app.route("/api/v1.0/tobs")
def tobs():
    print("Return a list of temperature observations for the previous year")
    # Create session
    session = Session(engine)

    # Last date in dataset and date from 1 yr prior to last date
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    prev_yr = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Query for dates and temp
    all_tobs = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= prev_yr).\
                order_by(Measurement.date).all()
    date_list = []

    for date, tobs in all_tobs:
        tobs_dict = {}
        tobs_dict[date] = tobs
        date_list.append(tobs_dict)
    # Close Session
    session.close()

    return jsonify(date_list)

### Start/ End Route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_range(start, end=None):
    print("Return a list of the minimum, maximum, and the average temperatures for a specified start or start-end range")

    #Create session
    session = Session(engine)

# Calculate tmin, tmax, tavg for all dates greater than or equal to the start date.
# Calculate tmin, tmax, tavg for dates from start date to end date
    start_date = str(start)

    if end == None:
        end_date = session.query(func.max(Measurement.date)).\
                    scalar()
    else:
        end_date = str(end)

    ranges = session.query(func.min(Measurement.tobs).label('min_temp'),
                           func.max(Measurement.tobs).label('max_temp'),
                           func.avg(Measurement.tobs).label('avg_temp')).\
                filter(Measurement.date.between(start_date,end_date)).\
                first()
    session.close()
    dp = list(np.ravel(ranges))
    return jsonify(dp)

# Run app
if __name__ == '__main__':
    app.run(debug=True)