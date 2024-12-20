import os
from pathlib import Path
from typing import Final
from dotenv import load_dotenv
from src.core.logger import logger
from src.core.logging_config import PROJECT_ROOT

# Загружаем переменные из .env
load_dotenv()
logger.info("Загружена конфигурация из .env")

# Пути
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"

# API настройки
OPENWEATHER_API_KEY: Final[str] = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_API_BASE_URL: Final[str] = \
    "http://api.openweathermap.org/data/2.5/weather"

# Анализ данных
ROLLING_WINDOW: Final[int] = 30
ANOMALY_THRESHOLD: Final[float] = 2.0
DEFAULT_CITY: Final[str] = "Moscow"

# Визуализация
PLOT_FIGSIZE: Final[tuple] = (20, 15)
PLOT_DPI: Final[int] = 100
TEMPERATURE_COLORS: Final[dict] = {
    'normal': '#1f77b4',
    'anomaly': '#d62728',
    'rolling': '#ff7f0e'
}

# Кэширование
CACHE_TTL: Final[int] = 300  # секунды
