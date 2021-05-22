
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>" 
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    # Calculate the date one year from the last date in data set.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()

    # dictionary with the date as the key and the precipitation as the value 
    precip = {date: prcp for date, prcp in results}
    
    session.close()
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    # Design a query to show how many stations available in this dataset
    results = session.query(Station.station).all()

    stations = list(np.ravel(results))

    return jsonify(stations)



@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of the most active station for the last year of data.
    #Return a JSON list of temperature observations (TOBS) for the previous year.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs).\
                filter(Measurement.date >= prev_year).\
                filter (Measurement.station == 'USC00519281').all()

    tobs = list(np.ravel(results))

    return jsonify(tobs)



@app.route("/api/v1.0/<start>")
def start(start):
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    min_temp = session.query(func.min(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

    max_temp = session.query(func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

    avg_temp = session.query(func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    
    temps = list(np.ravel([low_temp, high_temp, avg_temp]))

    return jsonify(temps)

#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def startend(start=None, end=None):
    min_temp = session.query(func.min(Measurement.tobs)).\
                filter(Measurement.date >= start).all().\
                filter(Measurement.date <= end).all()

    max_temp = session.query(func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all().\
                filter(Measurement.date <= end).all()

    avg_temp = session.query(func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start).all().\
                filter(Measurement.date <= end).all()

    temps = list(np.ravel([low_temp, high_temp, avg_temp]))

    return jsonify(temps)
    session.close()


if __name__ == '__main__':
    app.run(debug=True)