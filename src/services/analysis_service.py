from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd
from src.config import ROLLING_WINDOW, ANOMALY_THRESHOLD


@dataclass
class TemperatureAnalysis:
    city: str
    seasonal_stats: pd.DataFrame
    data: pd.DataFrame
    anomalies_count: int


class AnalysisService:
    @staticmethod
    async def analyze_city_temperature(
        df: pd.DataFrame,
        city: str
    ) -> TemperatureAnalysis:
        """Анализ температурных данных для конкретного города"""
        city_data = df[df['city'] == city].copy()
        
        # Вычисление скользящего среднего
        city_data['rolling_mean'] = city_data['temperature'].rolling(
            window=ROLLING_WINDOW,
            center=True
        ).mean()
        
        # Расчет сезонной статистики
        seasonal_stats = city_data.groupby('season').agg({
            'temperature': ['mean', 'std']
        }).round(2)
        
        # Определение аномалий
        city_data['is_anomaly'] = False
        for season in city_data['season'].unique():
            season_data = seasonal_stats.loc[season]
            mean = season_data[('temperature', 'mean')]
            std = season_data[('temperature', 'std')]
            
            season_mask = city_data['season'] == season
            city_data.loc[season_mask, 'is_anomaly'] = (
                (city_data.loc[season_mask, 'temperature'] > mean + ANOMALY_THRESHOLD*std) |
                (city_data.loc[season_mask, 'temperature'] < mean - ANOMALY_THRESHOLD*std)
            )
        
        return TemperatureAnalysis(
            city=city,
            seasonal_stats=seasonal_stats,
            data=city_data,
            anomalies_count=city_data['is_anomaly'].sum()
        ) 