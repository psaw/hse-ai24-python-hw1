"""Сервис для визуализации температурных данных."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from src.config import PLOT_FIGSIZE, PLOT_DPI, TEMPERATURE_COLORS


class VisualizationService:
    """Сервис для создания визуализаций температурных данных."""

    @staticmethod
    def setup_style():
        """Настройка стиля графиков."""
        plt.style.use('seaborn-v0_8-dark-palette')
        sns.set_palette("husl")

    @staticmethod
    def plot_temperature_time_series(
        data: pd.DataFrame,
        city: str,
        ax: plt.Axes = None
    ) -> plt.Figure:
        """Создание графика временного ряда температур с аномалиями.

        Args:
            data: DataFrame с температурными данными
            city: Название города
            ax: Объект осей для отрисовки. Если None, создается новая фигура

        Returns:
            plt.Figure: Объект с построенным графиком
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=PLOT_FIGSIZE, dpi=PLOT_DPI)
        else:
            fig = ax.figure

        # Основной ряд температур
        ax.plot(
            data['timestamp'],
            data['temperature'],
            color=TEMPERATURE_COLORS['normal'],
            alpha=0.5,
            label='Температура'
        )

        # Скользящее среднее
        ax.plot(
            data['timestamp'],
            data['rolling_mean'],
            color=TEMPERATURE_COLORS['rolling'],
            label='Скользящее среднее (30 дней)'
        )

        # Аномалии
        anomalies = data[data['is_anomaly']]
        ax.scatter(
            anomalies['timestamp'],
            anomalies['temperature'],
            color=TEMPERATURE_COLORS['anomaly'],
            label='Аномалии'
        )

        ax.set_title(f'Временной ряд температур для города {city}')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Температура (°C)')
        ax.legend()

        return fig

    @staticmethod
    def plot_seasonal_boxplot(
        data: pd.DataFrame,
        city: str,
        ax: plt.Axes = None
    ) -> plt.Figure:
        """Создание box plot распределения температур по сезонам.

        Args:
            data: DataFrame с температурными данными
            city: Название города
            ax: Объект осей для отрисовки. Если None, создается новая фигура

        Returns:
            plt.Figure: Объект с построенным графиком
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=PLOT_FIGSIZE, dpi=PLOT_DPI)
        else:
            fig = ax.figure

        sns.boxplot(
            data=data,
            x='season',
            y='temperature',
            ax=ax
        )

        ax.set_title(f'Распределение температур по сезонам для города {city}')
        ax.set_ylabel('Температура (°C)')

        return fig

    @staticmethod
    def plot_temperature_distribution(
        data: pd.DataFrame,
        city: str,
        ax: plt.Axes = None
    ) -> plt.Figure:
        """Создание гистограммы распределения температур.

        Args:
            data: DataFrame с температурными данными
            city: Название города
            ax: Объект осей для отрисовки. Если None, создается новая фигура

        Returns:
            plt.Figure: Объект с построенным графиком
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=PLOT_FIGSIZE, dpi=PLOT_DPI)
        else:
            fig = ax.figure

        sns.histplot(
            data=data,
            x='temperature',
            hue='season',
            multiple="stack",
            ax=ax
        )

        ax.set_title(f'Распределение температур для города {city}')
        ax.set_xlabel('Температура (°C)')
        ax.set_ylabel('Количество дней')

        return fig

    @staticmethod
    def plot_anomalies_heatmap(
        data: pd.DataFrame,
        city: str,
        ax: plt.Axes = None
    ) -> plt.Figure:
        """Создание тепловой карты аномалий по месяцам и годам.

        Args:
            data: DataFrame с температурными данными
            city: Название города
            ax: Объект осей для отрисовки. Если None, создается новая фигура

        Returns:
            plt.Figure: Объект с построенным графиком
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=PLOT_FIGSIZE, dpi=PLOT_DPI)
        else:
            fig = ax.figure

        # Подготовка данных для тепловой карты
        data = data.copy()
        data['year'] = data['timestamp'].dt.year
        data['month'] = data['timestamp'].dt.month

        anomalies_pivot = data.pivot_table(
            values='is_anomaly',
            index='year',
            columns='month',
            aggfunc='sum'
        ).astype(int)

        sns.heatmap(
            anomalies_pivot,
            ax=ax,
            cmap='YlOrRd'
        )

        ax.set_title(f'Количество аномалий по месяцам для города {city}')
        ax.set_xlabel('Месяц')
        ax.set_ylabel('Год')

        return fig
