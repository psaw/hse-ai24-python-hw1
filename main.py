import asyncio
import pandas as pd
from pathlib import Path
from typing import Dict, Optional

from src.config import DATA_DIR, DEFAULT_CITY, OPENWEATHER_API_KEY
from src.services.analysis_service import AnalysisService
from src.services.weather_service import WeatherService
# from src.utils import is_temperature_anomaly

async def print_temperature_info(city: str, analysis: AnalysisService, weather_info: WeatherService) -> None:
    """Вывод информации о температуре."""
    if weather_info.error:
        print(f"Ошибка при получении температуры: {weather_info.error}")
        return

    status = "аномальная" if weather_info.is_anomaly else "нормальная"
    print(
        f"Текущая температура в {city}: {weather_info.temperature}°C "
        f"({status} для текущего сезона)"
    )


async def print_city_analysis(city: str, analysis: AnalysisService) -> None:
    print(f"Анализ для города {city}:")
    print(analysis.seasonal_stats)
    print(f"\nОбщее количество аномалий: {analysis.anomalies_count}")


async def main():
    # Загружаем данные
    data_path = DATA_DIR / 'temperature_data.csv'
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Получаем список городов
    cities = df['city'].unique()
    
    # Анализируем данные для каждого города
    analyses = {}
    for city in cities:
        analysis = await AnalysisService.analyze_city_temperature(df, city)
        analyses[city] = analysis

    # Работаем с выбранным городом (по умолчанию Moscow)
    city = DEFAULT_CITY
    city_analysis = analyses[city]

    # Выводим статистику
    await print_city_analysis(city, city_analysis)

    # Получаем текущую температуру
    weather_service = WeatherService()
    
    # Асинхронный запрос текущей температуры
    current_weather = await weather_service.get_current_temperature(city, city_analysis, OPENWEATHER_API_KEY)

    # # Проверка на аномалию
    # is_anomaly = is_temperature_anomaly(
    #     current_weather.temperature,
    #     city_analysis.seasonal_stats,
    #     city_analysis.data['season'].iloc[-1]
    # )
    # current_weather.is_anomaly = is_anomaly
    await print_temperature_info(city, city_analysis, current_weather)


if __name__ == "__main__":
    asyncio.run(main())
