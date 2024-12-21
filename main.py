import asyncio
import pandas as pd

from src.config import DATA_DIR, DEFAULT_CITY, OPENWEATHER_API_KEY
from src.services.analysis_service import AnalysisService
from src.services.weather_service import WeatherService
from src.core.logger import logger


async def print_temperature_info(
    city: str,
    analysis: AnalysisService,
    weather_info: WeatherService
) -> None:
    """Вывод информации о температуре."""
    if weather_info.error:
        logger.error(f"Ошибка при получении температуры: {weather_info.error}")
        return

    status = "аномальная" if weather_info.is_anomaly else "нормальная"
    logger.info(
        f"Текущая температура в {city}: {weather_info.temperature}°C "
        f"({status} для текущего сезона)"
    )


async def print_city_analysis(city: str, analysis: AnalysisService) -> None:
    """Вывод анализа температуры для города."""
    logger.info(f"Анализ для города {city}:")
    logger.info(f"Сезонная статистика:\n{analysis.seasonal_stats}")
    logger.info(f"Общее количество аномалий: {analysis.anomalies_count}")


async def main():
    """Основная логика приложения."""
    # Загружаем данные
    data_path = DATA_DIR / 'temperature_data.csv'
    logger.info(f"Загрузка данных из {data_path}")
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Анализ температурных данных для всех городов
    analyses = await AnalysisService.analyze_all_cities_temperature(df)

    # Работаем с выбранным городом
    city = DEFAULT_CITY
    city_analysis = analyses[city]

    # Выводим статистику
    await print_city_analysis(city, city_analysis)

    # Получаем текущую температуру
    weather_service = WeatherService()
    current_weather = await weather_service.get_current_temperature(
        city,
        city_analysis,
        OPENWEATHER_API_KEY
    )

    await print_temperature_info(city, city_analysis, current_weather)


if __name__ == "__main__":
    asyncio.run(main())
