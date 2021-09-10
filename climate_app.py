# Import dependencies
from flask import Flask, request, redirect, jsonify
import numpy as np 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


# SET UP FLASK APP
app = Flask(__name__)


# SET UP DATABASE & DB REFERENCES
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station


# CREATE FLASK ROUTES
################################################################
@app.route("/")
# Home page.
# Lists all routes that are available...
def home():
    homepageHTML = (
        f"<h1>Welcome to the Hawaii Climate Analysis API!</h1>"
        f"<h2>Available API Endpoints:</h2><br/>"

        f"<h3>🌧 PRECIPITATION:</h3>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/><br/><br/><br/>"

        f"<h3>📡 STATIONS:</h3>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/><br/><br/><br/>"
        
        f"<h3>🌡 TEMPERATURE OBSERVATIONS:</h3>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/><br/><br/><br/>"

        f"<h3>📆 SPECIFIED START DATE:</h3>"
        f"/api/v1.0/temp/YYYY-MM-DD<br/><br/><br/><br/>"

        f"<h3>📆 SPECIFIED START DATE & END DATE:</h3>"
        f"/api/v1.0/temp/YYYY-MM-DD/YYYY-MM-DD"
    )
    return homepageHTML


################################################################
@app.route("/api/v1.0/precipitation") 
# Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary.
def precipitation():
    # Connect to database
    session = Session(engine)

    query_results = session.query(Measurement.date, Measurement.prcp).all() 
    query_dict = {}
    for datestr,prcp in query_results:
        query_dict[datestr] = prcp

    # Disconnect from database
    session.close()
    return jsonify(query_dict)


################################################################
@app.route("/api/v1.0/stations")
# Return a JSON list of stations from the dataset.
def stations():
    # Connect to database
    session = Session(engine)

    # YOUR JOB: DEFINE THE stations_as_list VARIABLE
    station_list = session.query(Station.station).order_by(Station.station).all()

    stations_as_list = []
    for station in station_list:
        stations_as_list.append(station[0])
    # Disconnect from database
    session.close()
    return jsonify(stations_as_list)


################################################################
@app.route("/api/v1.0/tobs")
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
def tobs():
    # Connect to database
    session = Session(engine)

    # YOUR JOB: DEFINE THE tobs_data VARIABLE
    top_station_id = 'USC00519281'
    session.query(func.min(Measurement.tobs),
    func.max(Measurement.tobs),
    func.avg(Measurement.tobs)).filter(Measurement.station ==top_station_id).all()
    temp_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    temp_recent_year = int(temp_recent_date[0:4])
    temp_recent_month = int(temp_recent_date[5:7])
    temp_recent_day = int(temp_recent_date[8:])
    year_of_temp_data = dt.date(temp_recent_year,temp_recent_month,temp_recent_day) - dt.timedelta(days=365)
    temp_query_results = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.station == top_station_id, Measurement.date >= year_of_temp_data).all()
    temp_query_results
    tobs_data = []
    for obs in temp_query_results:
        tobs_data.append(obs[2])
    # Disconnect from database
    session.close()
    return jsonify(tobs_data)


################################################################
@app.route("/api/v1.0/temp/<start>")
def start_date(start='YYYY-MM-DD'):
    
    # Connect to database
    session = Session(engine)

    print(start)

    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    temps_filtered_by_date = []
    for TMIN, TAVG, TMAX in result:
        temps_filtered_by_date_dict = {}
        temps_filtered_by_date_dict['TMIN'] = TMIN
        temps_filtered_by_date_dict['TAVG'] = TAVG
        temps_filtered_by_date_dict['TMAX'] = TMAX
        temps_filtered_by_date.append(temps_filtered_by_date_dict)


    # Disconnect from database
    session.close()
    return jsonify(temps_filtered_by_date)

@app.route("/api/v1.0/temp/<start>/<end>")
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
def start_and_end_date(start='YYYY-MM-DD', end='YYYY-MM-DD'):
    
    # Connect to database
    session = Session(engine)

    print(start,end)

    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temps_filtered_by_date_list = []
    for TMIN, TAVG, TMAX in result:
        temps_filtered_by_date_dict = {}
        temps_filtered_by_date_dict['TMIN'] = TMIN
        temps_filtered_by_date_dict['TAVG'] = TAVG
        temps_filtered_by_date_dict['TMAX'] = TMAX
        temps_filtered_by_date_list.append(temps_filtered_by_date_dict)

    # Disconnect from database
    session.close()
    return jsonify(temps_filtered_by_date_list)

# Run the Flask app that was created at the top of this file --> app = Flask(__name__)
################################################################
if __name__ == '__main__':
    app.run(debug=True) # set to false if deploying to a live website server (such as Google Cloud, Heroku, or AWS Elastic Beanstaulk)