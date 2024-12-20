import aiohttp
import pandas as pd
from dataclasses import dataclass
from typing import Optional
from src.config import OPENWEATHER_API_KEY, OPENWEATHER_API_BASE_URL
from src.services.analysis_service import TemperatureAnalysis

@dataclass
class WeatherInfo:
    temperature: float
    is_anomaly: bool
    error: Optional[str] = None

class WeatherService:
    @staticmethod
    def is_temperature_anomaly(temperature: float, 
                               seasonal_stats: pd.DataFrame,
                               current_season: str) -> bool:
        """Проверка на аномалию температуры"""
        mean = seasonal_stats.loc[current_season, ('temperature', 'mean')]
        std = seasonal_stats.loc[current_season, ('temperature', 'std')]

        return (temperature > mean + 2*std) or (temperature < mean - 2*std)

    @staticmethod
    async def get_current_temperature(city: str, 
                                      city_analysis: TemperatureAnalysis, 
                                      api_key: str) -> WeatherInfo:
        """Асинхронное получение текущей температуры"""
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(OPENWEATHER_API_BASE_URL, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        is_anomaly = WeatherService.is_temperature_anomaly(
                            data['main']['temp'],
                            city_analysis.seasonal_stats,
                            city_analysis.data['season'].iloc[-1]
                        )
                        return WeatherInfo(
                            temperature=data['main']['temp'],
                            is_anomaly=is_anomaly
                        )
                    elif response.status == 401:
                        return WeatherInfo(
                            temperature=0,
                            is_anomaly=False,
                            error="Invalid API key"
                        )
                    else:
                        data = await response.json()
                        return WeatherInfo(
                            temperature=0,
                            is_anomaly=False,
                            error=f"Error: {data.get('message', 'Unknown error')}"
                        )
        except Exception as e:
            return WeatherInfo(
                temperature=0,
                is_anomaly=False,
                error=f"Request error: {str(e)}"
            )
