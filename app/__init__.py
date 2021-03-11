from flask import Flask, render_template, flash, redirect, request, session, logging, url_for
#from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
#import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.extensions import db
from datetime import date, time, timedelta
import requests
import numpy as np
import pygrib
import ast
from twilio.rest import Client

account_sid = "AC5bd76816a3697162c33d569895121fd3"
auth_token  = "26db581fcd3880d977769dc92d194868"
client = Client(account_sid, auth_token)

# App creation and DB registration functions

def create_app():
    app = Flask(__name__)
    register_extensions(app)
    return app

def register_extensions(app):
    db.init_app(app)

#app.config['SECRET_KEY'] = '!9m@sgfsk4%32'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/James/Desktop/surftext/test.db'
#db = SQLAlchemy()

#scheduler = BackgroundScheduler()
#scheduler.add_job(func=get_surf_data, trigger="interval", seconds=60)
#scheduler.add_job(func=send_texts, trigger="interval", seconds=60)
#scheduler.start()
# Shut down the scheduler when exiting the app
#atexit.register(lambda: scheduler.shutdown())



# DB models/tables below

class User(db.Model):

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    phone = db.Column(db.String(11), nullable=False, unique=True)
    password = db.Column(db.String(256), unique=True)
    location1 = db.Column(db.String(100), nullable=False)
    loc1_lat = db.Column(db.Float, nullable=False)
    loc1_lon = db.Column(db.Float, nullable=False)
    location2 = db.Column(db.String(100), nullable=False)
    loc2_lat = db.Column(db.Float, nullable=False)
    loc2_lon = db.Column(db.Float, nullable=False)
    location3 = db.Column(db.String(100), nullable=False)
    loc3_lat = db.Column(db.Float, nullable=False)
    loc3_lon = db.Column(db.Float, nullable=False)
    notif_time = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<User %r' % self.id

class Locations(db.Model):

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    #update_time = db.Column(db.String(10), nullable=False)
    location_name = db.Column(db.String(256), nullable=False, unique=True)
    loc_lat = db.Column(db.Float, nullable=False)
    loc_lon = db.Column(db.Float, nullable=False)
    surf_data = db.Column(db.String) # consider better storage types for this large field
    tolerance = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return '<Locations %r' % self.id



#App functions for retrieving/updating surf data, sending texts, etc. below

def get_surf_data():
    # Master function that will be set to run at scheduled times to check if new data is available in the server, 
    # ...then calls the update_surf_data function to update data if new file is available on server.
    today = date.today().strftime("%Y%m%d")
    request_day = requests.get(f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{today}")
    request_00 = requests.get(f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{today}/00/wave/gridded/")
    request_06 = requests.get(f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{today}/06/wave/gridded/") 
    request_12 = requests.get(f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{today}/12/wave/gridded/")
    request_18 = requests.get(f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{today}/18/wave/gridded/")
    if request_day.ok:
        if request_00.ok and request_06 is False and request_12 is False and request_18 is False:
            update_surf_data(today, hour='00')
        elif request_06.ok and request_12 is False and request_18 is False:
            update_surf_data(today, hour='06')
        elif request_12.ok and request_18 is False:
            update_surf_data(today, hour='12')
        elif request_18.ok:
            update_surf_data(today, hour='18')
        else:
            return ("Error with requests")
    else:
        pass


def update_surf_data(today, hour):
    # Retrieves grib2 data from NOAA server, downloads + reads file for each forecast time (out to 384 files/hours).
    # For each spot (i.e. Doheny, San-O, etc.), updates Locations database with new forecast data.
    # Found a different, better data source with the Nearshore Wave Prediction System (NWPS), minor details will need to be changed below to implement new server.
    for a in range(0, 9, 3): #384 potential files 
        if len(str(a)) == 1:
            req = requests.get(f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{today}/{hour}/wave/gridded/gefs.wave.t00z.c00.global.0p25.f00{a}.grib2")
        elif len(str(a)) == 2: 
            req = requests.get(f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{today}/{hour}/wave/gridded/gefs.wave.t00z.c00.global.0p25.f0{a}.grib2")
        else:
            req = requests.get(f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{today}/{hour}/wave/gridded/gefs.wave.t00z.c00.global.0p25.f{a}.grib2")
        with open('grib2data.grib2', 'wb') as f:
            f.write(req.content)
        gr = pygrib.open('grib2data.grib2')
        msg = gr[1:24]
        latlons = db.session.query(Locations).all()
        for spot in latlons:
            tolerence = spot.tolerance
            old_surf_data = eval(str(spot.surf_data))
            if old_surf_data is None:
                first_surf_data = {a : {}}
                update_surf_data = first_surf_data[a]
                for i in range(1, 3):
                    data, lats, lons = msg[i].data(lat1=spot.loc_lat - tolerence,lat2=spot.loc_lat + tolerence,lon1=spot.loc_lon - tolerence,lon2=spot.loc_lon + tolerence)
                    update_surf_data[i] = data.mean() 
                spot.surf_data = str(first_surf_data)
            else:
                old_surf_data.update({a : {}})
                newer_surf_data = old_surf_data[a]
                for i in range(1, 3): 
                    data, lats, lons = msg[i].data(lat1=spot.loc_lat - tolerence,lat2=spot.loc_lat + tolerence,lon1=spot.loc_lon - tolerence,lon2=spot.loc_lon + tolerence)
                    newer_surf_data[i] = data.mean()
                spot.surf_data = str(old_surf_data)



def tide_data():
    # Still need to find tide data, might be included in the new NWPS server that is to be implemented above!
    pass


def send_texts():
    # Scheduled function (to run every 1 min or so) to check if a user has an update scheduled within the minute.
    # If so, then send the user a text with surf forecast data for their respective surf spots
    current_time = datetime.now()  
    users = db.session.query(User).filter(datetime.strptime(User.notif_time, "%I:%M %p") <= current_time + timedelta(minutes=10) & datetime.strptime(User.notif_time, "%I:%M %p") >= current_time).all()
    for user in users:
        fcst_hour = get_best_rept(user.notif_time)
        locations = db.session.query(Locations).filter_by(loc_lat==user.loc1_lat & loc_lon==user.loc1_lon | loc_lat==user.loc2_lat & loc_lon==user.loc2_lon | loc_lat==user.loc3_lat & loc_lon==user.loc3_lon).all()
        message = client.messages.create(to=f"{user.phone}", from_= "+18189753652", body= f"Hello James! {user.location1} {locations[0].surf_data}")



def get_best_rept(notification_time):
    # Fun function to get the best forecast time (for ex., if a user wants a text report at 5:00am, then...
    # ... this will send them the data that is closest to 5:00am. The next report time is 6:00am, so the...
    # ...only available time is 00 (midnight) and the forecast for 6 hours in the future is closest since the forecast...
    # ...is in 3 hour intervals.)
    in_time = datetime.strptime(notification_time, "%I:%M %p")
    out_time = datetime.strftime(in_time, "%H:%M")[0]
    rept_times = [0, 6, 12, 18]
    lengths = np.array([0, 3, 6, 9])
    if len(notification_time) == 5:
        out_time = int(notification_time[:2])
    else:
        out_time = int(notification_time[0])
        rept_times = [0, 6, 12, 18]
        lengths = np.array([0, 3, 6, 9])
    if out_time <= 7:
        rept = rept_times[0]
        out_time = out_time - rept
        return lengths[np.abs(lengths - out_time).argmin()]
    elif out_time > 7 and out_time <=13:
        rept = rept_times[1]
        out_time = out_time - rept
        return lengths[np.abs(lengths - out_time).argmin()]
    elif out_time > 13 and out_time <= 19:
        rept = rept_times[2]
        out_time = out_time - rept
        return lengths[np.abs(lengths - out_time).argmin()]
    else:
        rept = rept_times[3]
        out_time = out_time - rept
        return lengths[np.abs(lengths - out_time).argmin()]

# Below are the app url routes and associated stps for login, register, logout, etc.
# They are commented out becasue they cause problems when trying to test the backend functions above in test_app.py

'''@app.route('/')
def home():

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    # Creating Login form object
    form = LoginForm(request.form)
    # verifying that method is post and form is valid
    if request.method == 'POST' and form.validate:
        # checking that user is exist or not by email
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            # if user exist in database than we will compare our database hased password and password come from login form 
            if check_password_hash(user.password, form.password.data):
                # if password is matched, allow user to access and save email and username inside the session
                flash('You have successfully logged in.', "success")
                session['logged_in'] = True
                session['email'] = user.email 
                session['username'] = user.username
                # After successful login, redirecting to home page
                return redirect(url_for('home'))
            else:
                # if password is in correct , redirect to login page
                flash('Username or Password Incorrect', "Danger")
                return redirect(url_for('login'))
    # rendering login page
    return render_template('login.html', form = form)

@app.route('/register/', methods = ['GET', 'POST'])
def register():
    # Creating RegistrationForm class object
    form = RegisterForm(request.form)
    # Cheking that method is post and form is valid or not.
    if request.method == 'POST' and form.validate():
        # if all is fine, generate hashed password
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        # create new user model object
        new_user = User(
            name = form.name.data, 
            username = form.username.data, 
            email = form.email.data, 
            password = hashed_password )
        # saving user object into data base with hashed password
        db.session.add(new_user)
        db.session.commit()
        flash('You have successfully registered', 'success')
        # if registration successful, then redirecting to login Api
        return redirect(url_for('login'))
    else:
        # if method is Get, than render registration form
        return render_template('register.html', form = form)

@app.route('/logout/')
def logout():
    # Removing data from session by setting logged_flag to False.
    session['logged_in'] = False
    # redirecting to home page
    return redirect(url_for('home'))

@app.route('/newpass/')
def new_pass():


@app.route('/dashboard/<id>')
def subscription():
    return render_template('dashboard.html')'''
         

if __name__=='__main__':
    app = create_app()
    app.run()
 