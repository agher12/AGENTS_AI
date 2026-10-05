from urllib import response

from flask import session
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
import requests
import os


load_dotenv()

DB_URI = os.getenv("SUPBASE_DB_URI")

pool = ConnectionPool(
    conninfo=DB_URI,
    open=True,
    max_size=10,
    kwargs={
        "autocommit": True,
        "prepare_threshold": None,  # ← clave: deshabilita prepared statements
    }
)

checkpointer = PostgresSaver(pool)
checkpointer.setup()

def get_weather(city: str):
    """Get weather information for a given city Return the temperature_fahrenheit value in fahrenheit for locations such as US"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    temperature_celsius = data['main']['temp']
    temperature_farenheit = temperature_celsius * 1.8 + 32
    return data, {'temperature_farenheit': temperature_farenheit}

def get_location():
    """Get location information, use this when the user ask about weather"""
    from flask import session
    lat = session['user_location']['lat']
    lon = session['user_location']['lon']
    print("lat lon from get location", lat, lon)

    response = requests.get(
        f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json',
        headers={'User-Agent': 'WeatherAssistant/1.0'},
        timeout=5
    )
    data = response.json()
    print(data)
    address = data.get('address', {})
    city = address.get('city') or address.get('town') or address.get('village', 'Unknown')
    country = address.get('country', '')


    return f"{city}, {country}"

#Initialize the Google Generative AI model 
llm = ChatGoogleGenerativeAI(
    model = "gemini-3.1-flash-lite",
    #temperature = 0.2,
)

system_prompt = """
You are a helpful weather asistant.
YOUR WORKFLOW:
1. If the user asks about weather WITHOUT specifying a location, you MUST:
   - First call get_location() to find their location
   - Then call get_weather(city) with that location
   
2. If the user provides a city, call get_weather(city) directly.

3. If the user´s location is in US, only mention the temperature in Fahrenheit.
Otherwise, only mention the temperature in Celsius.
"""


agent = create_agent(
    model=llm,
    tools = [get_weather, get_location],
    system_prompt = system_prompt,
    checkpointer=checkpointer
)


