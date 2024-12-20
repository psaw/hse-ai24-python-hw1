import streamlit as st
import asyncio
import time
from src.services.analysis_service import AnalysisService
from src.services.weather_service import WeatherService
from src.utils import load_csv_async
from src.config import (
    DEFAULT_CITY,
    PLOT_FIGSIZE,
    TEMPERATURE_COLORS,
    OPENWEATHER_API_KEY
)


st.cache_data.clear()


async def main():
    st.title("Анализ температурных данных")

    # Загрузка данных
    uploaded_file = st.file_uploader("Загрузите файл с историческими данными", type=['csv'])

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
        analysis = await AnalysisService.analyze_city_temperature(df, selected_city)

        # Добавляем timestamp к ключу, чтобы сбросить кэш при перезапуске
        # cache_key = f"api_key_{int(time.time())}"
        # Получить от пользователя API ключ
        api_key = st.text_input(
            "Введите API ключ OpenWeatherMap",
            value=OPENWEATHER_API_KEY,
            # key=cache_key,
            type="password"  # Скрываем ключ звездочками
        )

        if api_key:
            # Получение текущей температуры
            weather = await WeatherService.get_current_temperature(selected_city, analysis, api_key)

            # Отображение результатов
            st.write(display_results(analysis, weather))


def display_results(analysis, weather_info):
    # Здесь код для отображения графиков и статистики

    # для начала просто выведем анализ аналогично тому, как это делается в main.py

    print(f"Анализ для города {analysis.city}:")
    print(analysis.seasonal_stats)
    print(f"\nОбщее количество аномалий: {analysis.anomalies_count}")

    if weather_info.error:
        print(f"Ошибка при получении температуры: {weather_info.error}")
        return

    status = "аномальная" if weather_info.is_anomaly else "нормальная"
    print(
        f"Текущая температура в {analysis.city}: {weather_info.temperature}°C "
        f"({status} для текущего сезона)"
    )


if __name__ == "__main__":
    asyncio.run(main())
