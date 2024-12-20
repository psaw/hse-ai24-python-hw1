import pandas as pd
from multiprocessing import Pool
import time


def analyze_temperature_data(df, city):
    """Анализ температурных данных для конкретного города"""
    city_data = df[df['city'] == city].copy()

    city_data['rolling_mean'] = \
        city_data['temperature'].rolling(window=30, center=True).mean()

    seasonal_stats = city_data.groupby('season').agg({
        'temperature': ['mean', 'std']
    }).round(2)

    for season in city_data['season'].unique():
        season_data = seasonal_stats.loc[season]
        mean = season_data[('temperature', 'mean')]
        std = season_data[('temperature', 'std')]

        season_mask = city_data['season'] == season
        city_data.loc[season_mask, 'is_anomaly'] = (
            (city_data.loc[season_mask, 'temperature'] > mean + 2*std) |
            (city_data.loc[season_mask, 'temperature'] < mean - 2*std)
        )

    return {
        'city': city,
        'seasonal_stats': seasonal_stats,
        'data': city_data
    }


def process_city(df_dict, city):
    """Функция для обработки одного города"""
    df = pd.DataFrame(df_dict)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return analyze_temperature_data(df, city)


def run_parallel_analysis(df):
    """Запуск параллельного анализа для всех городов"""
    # Подготовка данных
    df_dict = df.to_dict('list')
    cities = df['city'].unique()

    start_time = time.time()

    with Pool() as pool:
        results = pool.starmap(
            process_city, [(df_dict, city) for city in cities]
        )
    parallel_results = {result['city']: result for result in results}

    execution_time = time.time() - start_time
    return parallel_results, execution_time


def is_temperature_anomaly(temperature, seasonal_stats, season):
    """Проверяет, является ли температура аномальной для данного сезона.

    Args:
        temperature: Текущая температура
        seasonal_stats: Статистика по сезонам (DataFrame с mean и std)
        season: Текущий сезон

    Returns:
        bool: True если температура аномальная, False если нормальная
    """
    mean = seasonal_stats.loc[season, ('temperature', 'mean')]
    std = seasonal_stats.loc[season, ('temperature', 'std')]

    return (temperature > mean + 2*std) or (temperature < mean - 2*std)
