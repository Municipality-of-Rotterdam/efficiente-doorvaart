from flask import Flask
import requests

app = Flask(__name__)


def get_weather_data():
    api_url = "https://api.openweathermap.org/data/2.5/weather?q=Rotterdam&units=metric&appid=68fa16e98d023e91c68ce1d4632a129b"

    try:
        response = requests.get(api_url)
        response.raise_for_status() 

        return response.json()
        
    except requests.exceptions.RequestException as e:
        print("Error bij het ophalen van het weer:", e)
        return None

if __name__ == '__main__':
    app.run(debug=True, port=5001)