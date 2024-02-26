# Import the dependencies.



#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file

# Declare a Base using `automap_base()`

# Use the Base class to reflect the database tables


# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`


# Create a session


#################################################
# Flask Setup
#################################################




#################################################
# Flask Routes
#################################################
# Import necessary libraries
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

# Create Flask app
app = Flask(__name__)

# Create engine and reflect tables
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Define routes
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    # Convert query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in results}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    # Convert station results to a list
    station_list = [station[0] for station in results]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Query the most-active station
    most_active_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .first()[0]

    # Query temperature observations for the most-active station for the previous year
    one_year_ago = dt.date.today() - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= one_year_ago)\
        .all()

    session.close()

    # Convert query results to a list of dictionaries
    tobs_list = [{"Date": date, "Temperature": tobs} for date, tobs in results]

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end=None):
    session = Session(engine)

    # Define query to calculate TMIN, TAVG, and TMAX for the specified date range
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if end:
        results = session.query(*sel)\
            .filter(Measurement.date >= start)\
            .filter(Measurement.date <= end)\
            .all()
    else:
        results = session.query(*sel)\
            .filter(Measurement.date >= start)\
            .all()

    session.close()

    # Convert query results to a list of dictionaries
    temp_range_list = [{"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]} for result in results]

    return jsonify(temp_range_list)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
