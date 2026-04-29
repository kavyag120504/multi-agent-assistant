import requests
from dotenv import load_dotenv
import os

load_dotenv()

# ── Friendly error messages ──────────────────────────────────────────────────
_OWM_ERRORS = {
    401: "❌ Invalid OpenWeatherMap API key. Please check your `.env` file.",
    404: "❌ City **{city}** not found. Try a different spelling or include the country (e.g. *Paris, FR*).",
    429: "⚠️ Weather API rate limit reached. Please wait a moment and try again.",
}

def get_weather(user_message, context: str = ""):
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage

    api_key = os.getenv("OPENWEATHER_API_KEY")

    # ── Validate API key present ─────────────────────────────────────────────
    if not api_key:
        return "❌ `OPENWEATHER_API_KEY` is missing from your `.env` file. Please add it and restart."

    llm = get_llm()

    # ── Build context hint for LLM ───────────────────────────────────────────
    context_hint = f"\nConversation so far:\n{context}\n" if context else ""

    # ── Step 1: Detect intent (current / forecast / both) ───────────────────
    try:
        intent_messages = [
            SystemMessage(content=f"""
            Classify the weather request into one of:
            - current       (e.g. "what's the weather in Delhi?")
            - forecast      (e.g. "weather forecast for Mumbai", "next 5 days weather")
            - both          (e.g. "weather and forecast for Chennai")
            {context_hint}
            Respond with just the single word: current, forecast, or both.
            """),
            HumanMessage(content=user_message)
        ]
        weather_intent = llm.invoke(intent_messages).content.strip().lower()
        if weather_intent not in ("current", "forecast", "both"):
            weather_intent = "current"

        # ── Step 2: Extract city (uses context to resolve "there", "same city") ──
        city_messages = [
            SystemMessage(content=f"""
            Extract only the city name from the user message.
            Respond with just the city name, nothing else.
            If no city is mentioned but the conversation history mentions one, use that city.
            If still unknown, respond with: UNKNOWN
            {context_hint}
            Example: "What is the weather in Delhi?" -> Delhi
            Example: "What about tomorrow?" (with Delhi in history) -> Delhi
            """),
            HumanMessage(content=user_message)
        ]
        city = llm.invoke(city_messages).content.strip()

    except Exception as e:
        return f"⚠️ I had trouble understanding your request. Please try again.\n_Error: {str(e)}_"

    # ── Validate city was extracted ──────────────────────────────────────────
    if not city or city.upper() == "UNKNOWN":
        return "❓ I couldn't find a city name in your message. Try: *\"What's the weather in Mumbai?\"*"

    output_parts = []

    # ── Step 3: Current weather ──────────────────────────────────────────────
    if weather_intent in ("current", "both"):
        try:
            url    = "http://api.openweathermap.org/data/2.5/weather"
            params = {"q": city, "appid": api_key, "units": "metric"}
            resp   = requests.get(url, params=params, timeout=10)
            data   = resp.json()

            if resp.status_code == 200:
                weather    = data["weather"][0]["description"]
                temp       = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity   = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]
                visibility = data.get("visibility", 0) // 1000
                pressure   = data["main"]["pressure"]

                output_parts.append(
                    f"**Current Weather in {city}:**\n"
                    f"🌡️ Temperature: {temp}°C  (feels like {feels_like}°C)\n"
                    f"🌤️ Condition: {weather.capitalize()}\n"
                    f"💧 Humidity: {humidity}%\n"
                    f"💨 Wind Speed: {wind_speed} m/s\n"
                    f"👁️ Visibility: {visibility} km\n"
                    f"🔵 Pressure: {pressure} hPa"
                )
            else:
                msg = _OWM_ERRORS.get(resp.status_code,
                      f"❌ Weather service returned an error (code {resp.status_code}). Please try again.")
                return msg.format(city=city)

        except requests.exceptions.ConnectionError:
            return "🌐 No internet connection. Please check your network and try again."
        except requests.exceptions.Timeout:
            return "⏱️ Weather service timed out. Please try again in a moment."
        except Exception as e:
            return f"❌ Unexpected error fetching weather: {str(e)}"

    # ── Step 4: 5-day forecast ───────────────────────────────────────────────
    if weather_intent in ("forecast", "both"):
        try:
            url    = "http://api.openweathermap.org/data/2.5/forecast"
            params = {"q": city, "appid": api_key, "units": "metric", "cnt": 40}
            resp   = requests.get(url, params=params, timeout=10)
            data   = resp.json()

            if resp.status_code == 200:
                daily = {}
                for item in data["list"]:
                    date = item["dt_txt"].split(" ")[0]
                    hour = item["dt_txt"].split(" ")[1]
                    if date not in daily or hour == "12:00:00":
                        daily[date] = item

                forecast_lines = [f"\n**5-Day Forecast for {city}:**"]
                for date, item in list(daily.items())[:5]:
                    desc  = item["weather"][0]["description"].capitalize()
                    t_min = item["main"]["temp_min"]
                    t_max = item["main"]["temp_max"]
                    rain  = item.get("rain", {}).get("3h", 0)
                    forecast_lines.append(
                        f"📅 {date}  |  {desc}  |  🌡️ {t_min}°C – {t_max}°C"
                        + (f"  |  🌧️ Rain: {rain} mm" if rain else "")
                    )
                output_parts.append("\n".join(forecast_lines))
            else:
                output_parts.append(f"⚠️ Forecast data unavailable for **{city}**.")

        except requests.exceptions.ConnectionError:
            output_parts.append("🌐 Could not fetch forecast — no internet connection.")
        except requests.exceptions.Timeout:
            output_parts.append("⏱️ Forecast request timed out.")
        except Exception as e:
            output_parts.append(f"⚠️ Forecast error: {str(e)}")

    return "\n\n".join(output_parts) if output_parts else "❌ Could not retrieve weather data. Please try again."
