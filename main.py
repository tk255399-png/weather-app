from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

API_KEY = "4f594785e32a434abe2171541261607"
BASE_URL = "http://api.weatherapi.com/v1/current.json"

search_history = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is the vital missing piece! It serves the index.html page at the root link
@app.get("/", response_class=HTMLResponse)
def read_root():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>Frontend index.html file not found in directory.</h3>"

@app.get("/api/weather")
def get_weather(city: str):
    if not city:
        raise HTTPException(status_code=400, detail="City name is required")
    
    params = {"key": API_KEY, "q": city, "aqi": "no"}
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 400:
        raise HTTPException(status_code=404, detail="City not found. Please check spelling.")
    elif response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch data from weather service")
        
    data = response.json()
    
    weather_profile = {
        "city": data["location"]["name"],
        "country": data["location"]["country"],
        "temp": data["current"]["temp_c"],
        "condition": data["current"]["condition"]["text"],
        "icon": data["current"]["condition"]["icon"],
        "humidity": data["current"]["humidity"]
    }
    
    history_entry = f"{weather_profile['city']}, {weather_profile['country']}"
    if history_entry not in search_history:
        search_history.insert(0, history_entry)
        if len(search_history) > 5:
            search_history.pop()
            
    return weather_profile

@app.get("/api/history")
def get_history():
    return {"history": search_history}
