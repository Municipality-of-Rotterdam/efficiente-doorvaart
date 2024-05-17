from flask import Flask, render_template, request
import sys, os, datetime, requests, psycopg2, json
from functools import partial
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'commonground123'

# ============================ Functions ============================

def databasegeschiedenis():
    try:
        connection = psycopg2.connect(database="postgres", 
                                    user="postgres",
                                    password="12345",
                                    host="localhost",
                                    port="5432")
        print("Database connected successfully")
        
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM public.vertrekgeschiedenis ORDER BY id DESC LIMIT 5")
        data = cursor.fetchall()
        return data
        
    except psycopg2.Error as e:
        print("Error:", e)
        
    finally:
        cursor.close()
        connection.close()
        
        
def connecttodb():
    try:
        connection = psycopg2.connect(database="postgres", 
                                    user="postgres",
                                    password="12345",
                                    host="localhost",
                                    port="5432")
        print("Database connected successfully")
        
        return connection
        
    except psycopg2.Error as e:
        print("Error:", e)

def insert_into_database(latitude, longitude, speed, speed_unit):
    try:
        connection = connecttodb()
        cursor = connection.cursor()
        
        if speed_unit == 'kilometer':
            speed = float(speed) / 1.852  
        
        knopen = True if speed_unit == 'knots' else False
        
        cursor.execute("INSERT INTO public.vertrekgeschiedenis (latitude, longitude, snelheid, knopen) VALUES (%s, %s, %s, %s)", (latitude, longitude, speed, knopen))
        connection.commit()
        print("Data inserted into database successfully")
    except psycopg2.Error as e:
        print("Error inserting data into database:", e)
    finally:
        if connection:
            cursor.close()
            connection.close()
            
def fetch_data_from_database():
    try:
        connection = connecttodb()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM public.vertrekgeschiedenis ORDER BY id DESC LIMIT 5")
        data = cursor.fetchall()
        return data
    except psycopg2.Error as e:
        print("Error fetching data from database:", e)
    finally:
        if connection:
            cursor.close()
            connection.close()

dbconnect = connecttodb()
geschiedenis = databasegeschiedenis()

def get_current_time():
    now = datetime.datetime.now().hour
    if now >= 1 and now <= 7:
        return "Momenteel geen file op de weg."
    elif now >= 8 and now <= 9:
        return "File op de weg door mensen die naar werk gaan."
    elif now >= 10 and now <= 11:
        return "Momenteel geen file op de weg."
    elif now >= 12 and now <= 13:
        return "Beetje file op de weg door mensen die naar lunch gaan."
    elif now >= 14 and now <= 15:
        return "Momenteel geen file op de weg."
    elif now >= 16 and now <= 17:
        return "File op de weg door mensen die naar huis gaan."
    elif now >= 18 and now <= 19:
        return "Beetje file op de weg door mensen die gaan avondeten."
    elif now >= 20 and now <= 24:
        return "Momenteel geen file op de weg."
    else:
        return "Error: Kon geen info ophalen."
    
def get_weather_data():
    api_url = "https://api.openweathermap.org/data/2.5/weather?q=Rotterdam&units=metric&appid=68fa16e98d023e91c68ce1d4632a129b"
    try:
        response = requests.get(api_url)
        response.raise_for_status() 

        return response.json()
        
    except requests.exceptions.RequestException as e:
        print("Error bij het ophalen van het weer:", e)
        return None
    
class MyForm(FlaskForm):
    action = SelectField('Action', choices=[('get', 'GET'), ('post', 'POST'), ('put', 'PUT'), ('patch', 'PATCH'), ('delete', 'DELETE')], validators=[DataRequired()])
    option = SelectField('Option', choices=[('objects', 'Objects'), ('objecttypes', 'Objecttypes')], validators=[DataRequired()])
    authorization = StringField('Authorization Token', validators=[DataRequired()])
    uuid = StringField('Uuid', validators=[DataRequired()])

# ============================ Routes ============================

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

def adviesBerekening(arrival_time):
    advice = ""
    if arrival_time.hour >= 1 and arrival_time.hour <= 7:
        advice = "Het is rustig op de weg. Je kunt vertrekken!"
    elif arrival_time.hour >= 8 and arrival_time.hour <= 9:
        advice = "Het is beter om nog even te wachten met vertrekken. Tussen 10:00 en 11:00 is het rustiger op de weg."
    elif arrival_time.hour >= 10 and arrival_time.hour <= 11:
        advice = "Het is rustig op de weg. Je kunt vertrekken!"
    elif arrival_time.hour >= 12 and arrival_time.hour <= 13:
        advice = "Het is beter om nog even te wachten met vertrekken. Tussen 14:00 en 15:00 is het rustiger op de weg."
    elif arrival_time.hour >= 14 and arrival_time.hour <= 15:
        advice = "Het is rustig op de weg. Je kunt vertrekken!"
    elif arrival_time.hour >= 16 and arrival_time.hour <= 17:
        advice = "Het is beter om nog even te wachten met vertrekken. Tussen 18:00 en 19:00 is het rustiger op de weg."
    elif arrival_time.hour >= 18 and arrival_time.hour <= 19:
        advice = "Het is rustig op de weg. Je kunt vertrekken!"
    elif arrival_time.hour >= 20 and arrival_time.hour <= 24:
        advice = "Het is rustig op de weg. Je kunt vertrekken!"
    
    return advice

@app.route('/home', methods=['GET', 'POST'])
def index():
    distance = None
    travel_time = None
    time = datetime.datetime.now()
    formatted_time = time.strftime("%H:%M:%S")
    current_situation = get_current_time()
    advice = ""
    arrival_time = None
    
    if request.method == 'POST':
        user_latitude = float(request.form['latitude'])
        user_longitude = float(request.form['longitude'])
        user_speed = float(request.form['speed'])
        speed_unit = request.form['speed_unit']
        
        insert_into_database(user_latitude, user_longitude, user_speed, speed_unit)

        specific_location = (51.9090, 4.4871)
        user_location = (user_latitude, user_longitude)
        distance = geodesic(user_location, specific_location).km

        if user_speed > 0:
            user_speed = float(request.form['speed'])
            speed_unit = request.form['speed_unit']
            
            if speed_unit == 'knots':
                user_speed *= 1.852  
            else:
                user_speed = user_speed
            
            travel_time_hours = int(distance / user_speed)
            travel_time_minutes = int((distance / user_speed * 60) % 60)
            travel_time_seconds = int((distance / user_speed * 3600) % 60)
            travel_time = f"{travel_time_hours}h {travel_time_minutes}m {travel_time_seconds}s"
            
            arrival_time = time + datetime.timedelta(hours=travel_time_hours, minutes=travel_time_minutes, seconds=travel_time_seconds)
            advice = adviesBerekening(arrival_time)

    return render_template('index.html', geschiedenis=geschiedenis, distance=distance, formatted_time=formatted_time, current_situation=current_situation, travel_time=travel_time, arrival_time=arrival_time.strftime("%H:%M") if arrival_time else None, advice=advice)

@app.route('/hetweer')
def hetweer():
    weather_data = get_weather_data()
    if weather_data:
        return render_template('hetweer.html', weather_data=weather_data, utcfromtimestamp=datetime.datetime.utcfromtimestamp)
    else:
        return "Error: Unable to fetch weather data"

@app.route('/api' , methods=['GET', 'POST'])
def api():
    form = MyForm()
    response = None
    usersinput = None
    if form.validate_on_submit():
        action = form.action.data
        option = form.option.data
        authorization = form.authorization.data
        uuid = form.uuid.data

        print(f'Action: {action}, Option: {option}, Authorization Token: {authorization}, Uuid: {uuid}')
    
    
        usersinput = "Gelukt!"
        # response = "..."
    return render_template('apipage.html', form=form, response=response, usersinput=usersinput)
        


if __name__ == '__main__':
    app.run(debug=True)