import httpx
from config import OPENWEATHER_API_BASE_URL, OPENWEATHER_API_KEY


def get_current_temperature(city):
    """Получение текущей температуры для указанного города
    через OpenWeatherMap API."""
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric'
    }
    response = httpx.get(OPENWEATHER_API_BASE_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        return data['main']['temp']
    elif response.status_code == 401:
        raise ValueError(
            "Invalid API key. Please see "
            "https://openweathermap.org/faq#error401 for more info."
        )
    else:
        raise Exception(
            f"Error fetching data: {data.get('message', 'Unknown error')}"
        )


async def get_current_temperature_async(city):
    """Асинхронное получение текущей температуры для указанного города
    через OpenWeatherMap API."""
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric'
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(OPENWEATHER_API_BASE_URL, params=params)
        data = response.json()

        if response.status_code == 200:
            return data['main']['temp']
        elif response.status_code == 401:
            raise ValueError(
                "Invalid API key. Please see "
                "https://openweathermap.org/faq#error401 for more info."
            )
        else:
            raise Exception(
                f"Error fetching data: {data.get('message', 'Unknown error')}"
            )
