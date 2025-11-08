from prometheus_client import start_http_server, Gauge, Info
import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Exporter info
exporter_info = Info('custom_exporter', 'Custom API Exporter Information')

# List of cities to monitor (we can add more later)
CITIES = [
    {'name': 'Astana', 'country': 'Kazakhstan', 'lat': 51.1694, 'lon': 71.4491},
    {'name': 'Almaty', 'country': 'Kazakhstan', 'lat': 43.2220, 'lon': 76.8512}
]

# Weather Metrics
weather_temperature = Gauge('weather_temperature_celsius', 'Current temperature in Celsius', ['city', 'country'])
weather_windspeed = Gauge('weather_windspeed_kmh', 'Current wind speed in km/h', ['city', 'country'])
weather_humidity = Gauge('weather_humidity_percent', 'Current relative humidity', ['city', 'country'])
weather_pressure = Gauge('weather_pressure_hpa', 'Current atmospheric pressure', ['city', 'country'])
weather_feels_like = Gauge('weather_apparent_temperature_celsius', 'Apparent temperature (feels like)', ['city', 'country'])
weather_precipitation = Gauge('weather_precipitation_mm', 'Current precipitation', ['city', 'country'])
weather_cloud_cover = Gauge('weather_cloud_cover_percent', 'Cloud cover percentage', ['city', 'country'])
weather_visibility = Gauge('weather_visibility_meters', 'Visibility in meters', ['city', 'country'])
weather_uv_index = Gauge('weather_uv_index', 'UV index', ['city', 'country'])
weather_wind_direction = Gauge('weather_wind_direction_degrees', 'Wind direction in degrees', ['city', 'country'])

# API status & response time
weather_api_status = Gauge('weather_api_status', 'Weather API status (1=up, 0=down)', ['city', 'country'])
weather_api_response_time = Gauge('weather_api_response_time_seconds', 'API response time in seconds', ['city', 'country'])


def fetch_weather(city):
    """
    Fetch weather data for a given city from Open-Meteo API
    """
    try:
        start_time = time.time()
        
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': city['lat'],
            'longitude': city['lon'],
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,'
                       'precipitation,pressure_msl,cloud_cover,wind_speed_10m,wind_direction_10m',
            'timezone': 'Asia/Almaty'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        response_time = time.time() - start_time

        data = response.json()
        current = data.get('current', {})

        labels = {'city': city['name'], 'country': city['country']}

        # Update metrics
        weather_temperature.labels(**labels).set(current.get('temperature_2m', 0))
        weather_windspeed.labels(**labels).set(current.get('wind_speed_10m', 0))
        weather_humidity.labels(**labels).set(current.get('relative_humidity_2m', 0))
        weather_pressure.labels(**labels).set(current.get('pressure_msl', 0))
        weather_feels_like.labels(**labels).set(current.get('apparent_temperature', 0))
        weather_precipitation.labels(**labels).set(current.get('precipitation', 0))
        weather_cloud_cover.labels(**labels).set(current.get('cloud_cover', 0))
        weather_wind_direction.labels(**labels).set(current.get('wind_direction_10m', 0))
        weather_visibility.labels(**labels).set(10000)  # Default visibility
        weather_uv_index.labels(**labels).set(0)        # Default UV index

        # API status & response time
        weather_api_status.labels(**labels).set(1)
        weather_api_response_time.labels(**labels).set(response_time)

        logger.info(f"Fetched weather for {city['name']}: {current.get('temperature_2m', 0)}°C")
        return True

    except Exception as e:
        labels = {'city': city['name'], 'country': city['country']}
        weather_api_status.labels(**labels).set(0)
        weather_api_response_time.labels(**labels).set(0)
        logger.error(f"Failed to fetch weather for {city['name']}: {e}")
        return False


if __name__ == '__main__':
    # Set exporter info
    exporter_info.info({
        'version': '1.1',
        'author': 'Student',
        'sources': 'open-meteo',
        'description': 'Weather metrics from Open-Meteo API for multiple cities'
    })

    # Start HTTP server
    start_http_server(8000)
    logger.info("Custom exporter started on port 8000")
    logger.info("Metrics available at http://localhost:8000/metrics")

    # Infinite loop to collect metrics
    while True:
        for city in CITIES:
            fetch_weather(city)
        time.sleep(20)