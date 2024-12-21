import aiohttp
import time
import pandas as pd
from dataclasses import dataclass
from typing import Optional
import streamlit as st
from src.config import OPENWEATHER_API_BASE_URL, CACHE_TTL_SECONDS
from src.services.analysis_service import TemperatureAnalysis
from src.core.logger import logger


@dataclass
class WeatherInfo:
    temperature: float
    is_anomaly: bool
    error: Optional[str] = None


class WeatherService:
    """Сервис для получения текущей погоды через API."""

    def __init__(self):
        if 'weather_cache' not in st.session_state:
            st.session_state.weather_cache = {}
            st.session_state.weather_cache_time = {}

    async def get_current_temperature(
        self,
        city: str,
        city_analysis: TemperatureAnalysis,
        api_key: str
    ) -> WeatherInfo:
        """Асинхронное получение текущей температуры с кэшированием."""
        cache_key = f"{city}:{api_key}"
        current_time = time.time()

        if cache_key in st.session_state.weather_cache:
            cache_age = current_time - \
                st.session_state.weather_cache_time[cache_key]
            if cache_age < CACHE_TTL_SECONDS:
                logger.info(
                    f"Cache hit для {city}. Возраст кэша: {cache_age:.1f} сек."
                )
                return st.session_state.weather_cache[cache_key]
            logger.info(
                f"Cache expired для {city}. Возраст кэша: {cache_age:.1f} сек."
            )
        else:
            logger.info(f"Cache miss для {city}")

        result = await self._fetch_temperature(city, city_analysis, api_key)

        st.session_state.weather_cache[cache_key] = result
        st.session_state.weather_cache_time[cache_key] = current_time
        logger.info(f"Обновлен кэш для {city}")

        return result

    @staticmethod
    def is_temperature_anomaly(
        temperature: float,
        seasonal_stats: pd.DataFrame,
        current_season: str
    ) -> bool:
        """Проверка на аномалию температуры."""
        mean = seasonal_stats.loc[current_season, ('temperature', 'mean')]
        std = seasonal_stats.loc[current_season, ('temperature', 'std')]
        return (temperature > mean + 2 * std) or (temperature < mean - 2 * std)

    @staticmethod
    async def _fetch_temperature(
        city: str,
        city_analysis: TemperatureAnalysis,
        api_key: str
    ) -> WeatherInfo:
        """Асинхронное получение текущей температуры."""
        logger.info(f"Запрос текущей температуры для города {city}")
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }

        try:
            async with aiohttp.ClientSession() as session:
                logger.debug(
                    f"Отправка запроса к OpenWeatherMap API для {city}"
                )
                async with session.get(
                    OPENWEATHER_API_BASE_URL,
                    params=params
                ) as response:
                    data = await response.json()

                    if response.status == 200:
                        logger.success(f"200: получены данные для {city}")
                        is_anomaly = WeatherService.is_temperature_anomaly(
                            data['main']['temp'],
                            city_analysis.seasonal_stats,
                            city_analysis.data['season'].iloc[-1]
                        )
                        return WeatherInfo(
                            temperature=data['main']['temp'],
                            is_anomaly=is_anomaly
                        )

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
            logger.error(f"Неожиданная ошибка при запросе для {city}")
            return WeatherInfo(
                temperature=0,
                is_anomaly=False,
                error=f"Неожиданная ошибка: {str(e)}"
            )
