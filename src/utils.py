from typing import Dict, Tuple, Optional
import pandas as pd
from multiprocessing import Pool
import time
import aiofiles
import asyncio
from io import StringIO
from pathlib import Path
from src.config import DATA_DIR


def validate_and_prepare_dataframe(df: pd.DataFrame) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """Проверка и подготовка DataFrame.
    
    Args:
        df: DataFrame для проверки
        
    Returns:
        Tuple[bool, str, Optional[pd.DataFrame]]: 
            - bool: успешна ли валидация
            - str: сообщение об ошибке или успехе
            - Optional[pd.DataFrame]: подготовленный DataFrame или None
    """
    required_columns = {'city', 'timestamp', 'temperature', 'season'}
    
    # Проверка наличия необходимых колонок
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        return False, f"Отсутствуют обязательные колонки: {missing}", None
    
    try:
        # Создаем копию для преобразований
        prepared_df = df.copy()
        
        # Конвертация timestamp
        prepared_df['timestamp'] = pd.to_datetime(prepared_df['timestamp'])
        
        # Проверка типов данных
        if not pd.api.types.is_numeric_dtype(prepared_df['temperature']):
            return False, "Колонка 'temperature' должна содержать числовые значения", None
            
        # Проверка сезонов
        valid_seasons = {'winter', 'spring', 'summer', 'autumn'}
        if not set(prepared_df['season'].unique()).issubset(valid_seasons):
            return False, f"Недопустимые значения в колонке 'season'. Допустимые значения: {valid_seasons}", None
        
        return True, "Данные успешно загружены и подготовлены", prepared_df
        
    except Exception as e:
        return False, f"Ошибка при подготовке данных: {str(e)}", None


async def load_csv_async(file) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """Асинхронная загрузка CSV файла.
    
    Args:
        file: Файловый объект (UploadedFile из Streamlit или путь к файлу)
        
    Returns:
        Tuple[bool, str, Optional[pd.DataFrame]]:
            - bool: успешна ли загрузка
            - str: сообщение об ошибке или успехе
            - Optional[pd.DataFrame]: загруженный DataFrame или None
    """
    try:
        if isinstance(file, (str, Path)):
            async with aiofiles.open(file, mode='r') as f:
                content = await f.read()
        else:
            # Для загруженного через Streamlit файла
            content = file.getvalue().decode('utf-8')
            
        df = pd.read_csv(StringIO(content))
        return validate_and_prepare_dataframe(df)
        
    except Exception as e:
        return False, f"Ошибка при загрузке файла: {str(e)}", None


def analyze_data(df: pd.DataFrame) -> Tuple[bool, str, Optional[Dict]]:
    """Анализ данных из DataFrame.
    
    Args:
        df: Подготовленный DataFrame
        
    Returns:
        Tuple[bool, str, Optional[Dict]]:
            - bool: успешен ли анализ
            - str: сообщение об ошибке или успехе
            - Optional[Dict]: результаты анализа или None
    """
    try:
        start_time = time.time()
        results = run_parallel_analysis(df)
        execution_time = time.time() - start_time
        
        return True, f"Анализ выполнен за {execution_time:.2f} секунд", results
        
    except Exception as e:
        return False, f"Ошибка при анализе данных: {str(e)}", None


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
    """Запуск пара��лельного анализа для всех городов"""
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
