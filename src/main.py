import asyncio
import pandas as pd
import utils
from config import DATA_DIR
from weather_api import get_current_temperature, get_current_temperature_async


async def get_temperature_info(city, seasonal_stats, season):
    """Получение информации о температуре с проверкой на аномальность."""
    try:
        current_temp = get_current_temperature(city)
        is_anomaly = utils.is_temperature_anomaly(
            current_temp,
            seasonal_stats,
            season
        )
        return {
            'temperature': current_temp,
            'is_anomaly': is_anomaly,
            'error': None
        }
    except Exception as e:
        return {'error': str(e)}


async def get_temperature_info_async(city, seasonal_stats, season):
    """Асинхронный запрос температуры и проверка аномальности."""
    try:
        current_temp = await get_current_temperature_async(city)
        is_anomaly = utils.is_temperature_anomaly(
            current_temp,
            seasonal_stats,
            season
        )
        return {
            'temperature': current_temp,
            'is_anomaly': is_anomaly,
            'error': None
        }
    except Exception as e:
        return {'error': str(e)}


def print_temperature_info(city, temp_info, method=""):
    """Вывод информации о температуре."""
    if temp_info.get('error'):
        print(
            f"Ошибка при получении температуры{method}: {temp_info['error']}"
        )
        return

    status = "аномальная" if temp_info['is_anomaly'] else "нормальная"
    print(
        f"Текущая температура в {city}{method}: {temp_info['temperature']}°C "
        f"({status} для текущего сезона)"
    )


def main():
    # Загружаем данные
    data_path = DATA_DIR / 'temperature_data.csv'
    df = pd.read_csv(data_path)

    # Запускаем анализ
    results, execution_time = utils.run_parallel_analysis(df)
    print(f"\nВремя параллельного выполнения: {execution_time:.2f} секунд")

    # Получаем результаты для первого города
    # first_city = list(results.keys())[0]
    first_city = "Moscow"
    city_results = results[first_city]

    # Выводим статистику
    print(f"\nСтатистика по сезонам для города {first_city}:")
    print(city_results['seasonal_stats'])
    print(f"\nОбщее количество аномалий: "
          f"{city_results['data']['is_anomaly'].sum()}")

    # Получаем и выводим текущую температуру
    current_season = city_results['data']['season'].iloc[-1]

    # Синхронный запрос
    temp_info = asyncio.run(get_temperature_info(
        first_city,
        city_results['seasonal_stats'],
        current_season
    ))
    print_temperature_info(first_city, temp_info)

    # Асинхронный запрос
    temp_info_async = asyncio.run(get_temperature_info_async(
        first_city,
        city_results['seasonal_stats'],
        current_season
    ))
    print_temperature_info(first_city, temp_info_async, " (асинхронно)")


if __name__ == "__main__":
    main()
