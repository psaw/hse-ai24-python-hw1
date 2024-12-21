import streamlit as st
import asyncio
from src.services.analysis_service import AnalysisService
from src.services.weather_service import WeatherService
from src.services.visualization_service import VisualizationService
from src.utils import load_csv_async
from src.config import (
    DEFAULT_CITY,
    OPENWEATHER_API_KEY
)
from src.core.logger import logger


st.cache_data.clear()


async def main():
    st.title("Анализ температурных данных")

    # Загрузка данных
    uploaded_file = st.file_uploader(
        "Загрузите файл с историческими данными",
        type=['csv']
    )

    if uploaded_file is not None:
        success, message, df = await load_csv_async(uploaded_file)
        if not success:
            st.error(message)
            st.stop()

        st.success(message)

        # Выбор города
        cities = df['city'].unique()
        selected_city = st.selectbox(
            "Выберите город",
            options=cities,
            index=list(cities).index(DEFAULT_CITY) if DEFAULT_CITY in cities else 0
        )

        st.subheader(f"Анализ данных для города {selected_city}")
        # Анализ данных
        analysis = await AnalysisService().analyze_city_temperature(
            df,
            selected_city
        )

        # Получить от пользователя API ключ
        api_key = st.text_input(
            "Введите API ключ OpenWeatherMap",
            value=OPENWEATHER_API_KEY,
            type="password"  # Скрываем ключ звездочками
        )
        if api_key:
            # Получение текущей температуры
            weather = await WeatherService().get_current_temperature(
                selected_city,
                analysis,
                api_key
            )
            if weather.error:
                st.error(f"Ошибка при получении температуры: {weather.error}")
                logger.error(f"Ошибка при получении температуры: {weather.error}")
                st.stop()
            else:
                # Отображение результатов
                display_results(analysis, weather)
                display_stats(analysis)


def display_results(analysis, weather_info):
    """Отображение текущей температуры и её статуса."""
    st.subheader("Текущая температура")
    if weather_info.error:
        st.error(f"Ошибка при получении температуры: {weather_info.error}")
        return

    # Создаем колонки для отображения
    col1, col2 = st.columns(2)

    with col1:
        # Температура и город
        st.metric(
            label=analysis.city,
            value=f"{weather_info.temperature}°C",
            delta="Аномальная" if weather_info.is_anomaly else "Нормальная",
            delta_color="inverse" if weather_info.is_anomaly else "normal"
        )

    with col2:
        # Информация о сезоне
        current_season = analysis.data['season'].iloc[-1]
        season_stats = analysis.seasonal_stats.loc[current_season]
        mean_temp = season_stats[('temperature', 'mean')]
        std_temp = season_stats[('temperature', 'std')]

        st.caption("Статистика текущего сезона:")
        st.info(
            f"""
            **{current_season.title()}**
            - Средняя температура: {mean_temp:.1f}°C
            - Стандартное отклонение: {std_temp:.1f}°C
            """
        )


def display_stats(analysis):
    """Отображение статистики и графиков анализа температур."""
    # Инициализация сервиса визуализации
    viz_service = VisualizationService()
    viz_service.setup_style()

    # Вывод статистики
    st.subheader("Статистика по сезонам")
    st.dataframe(analysis.seasonal_stats)

    st.write(f"Общее количество аномалий: {analysis.anomalies_count}")

    # Графики
    st.subheader("Визуализация данных")

    # Временной ряд
    st.write("#### Временной ряд температур")
    fig_time_series = viz_service.plot_temperature_time_series(
        analysis.data,
        analysis.city
    )
    st.pyplot(fig_time_series)

    # Box plot сезонов
    st.write("#### Распределение температур по сезонам")
    fig_boxplot = viz_service.plot_seasonal_boxplot(
        analysis.data,
        analysis.city
    )
    st.pyplot(fig_boxplot)

    # Гистограмма
    st.write("#### Распределение температур")
    fig_hist = viz_service.plot_temperature_distribution(
        analysis.data,
        analysis.city
    )
    st.pyplot(fig_hist)

    # Тепловая карта
    st.write("#### Карта аномалий")
    fig_heatmap = viz_service.plot_anomalies_heatmap(
        analysis.data,
        analysis.city
    )
    st.pyplot(fig_heatmap)


if __name__ == "__main__":
    asyncio.run(main())
