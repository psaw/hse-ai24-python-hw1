import aiohttp
import pandas as pd
from dataclasses import dataclass
from typing import Optional
from src.config import OPENWEATHER_API_BASE_URL
from src.services.analysis_service import TemperatureAnalysis
from src.core.logger import logger


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
        logger.info(f"Запрос текущей температуры для города {city}")
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }

        try:
            async with aiohttp.ClientSession() as session:
                logger.debug(f"Отправка запроса к OpenWeatherMap API для {city}")
                async with session.get(OPENWEATHER_API_BASE_URL, params=params) as response:
                    data = await response.json()

                    if response.status == 200:
                        logger.success(f"200: получены данные для {city}")
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
                    else:
                        error_message = data.get('message', 'Неизвестная ошибка')
                        if response.status == 401:
                            logger.error(
                                f"401: Неверный API ключ при запросе для {city}"
                            )
                            error_message = "Invalid API key"
                        elif response.status == 404:
                            logger.error(f"404: Город {city} не найден")
                            error_message = f"Город {city} не найден"
                        else:
                            logger.error(f"Ошибка API: {error_message}")

                        return WeatherInfo(
                            temperature=0,
                            is_anomaly=False,
                            error=error_message
                        )

        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети при запросе для {city}: {str(e)}")
            return WeatherInfo(
                temperature=0,
                is_anomaly=False,
                error=f"Ошибка сети: {str(e)}"
            )
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при запросе для {city}")
            return WeatherInfo(
                temperature=0,
                is_anomaly=False,
                error=f"Неожиданная ошибка: {str(e)}"
            )
