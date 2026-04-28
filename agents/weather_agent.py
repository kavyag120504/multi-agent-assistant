import requests
from dotenv import load_dotenv
import os

load_dotenv()

def get_weather(user_message):
    # Extract city name using simple parsing
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    # Ask Groq to extract city name from message
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage
    
    llm = get_llm()
    messages = [
        SystemMessage(content="""
        Extract only the city name from the user message.
        Respond with just the city name, nothing else.
        Example: "What is the weather in Delhi?" -> Delhi
        """),
        HumanMessage(content=user_message)
    ]
    
    city = llm.invoke(messages).content.strip()
    
    # Call OpenWeatherMap API
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"  # celsius
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if response.status_code == 200:
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        
        return f"""Weather in {city}:
🌡️ Temperature: {temp}°C
🤔 Feels like: {feels_like}°C
💧 Humidity: {humidity}%
🌤️ Condition: {weather.capitalize()}"""
    else:
        return f"Sorry, I couldn't find weather data for {city}."