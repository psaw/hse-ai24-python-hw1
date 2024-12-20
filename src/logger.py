import sys
from loguru import logger
from src.config import LOG_LEVEL

# Удаляем стандартный обработчик
logger.remove()

# Добавляем свой обработчик с форматированием
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
           "<level>{message}</level>",
    level=LOG_LEVEL,
    colorize=True
)

# Добавляем файловый обработчик для записи логов
logger.add(
    "logs/app.log",
    rotation="1 day",
    retention="7 days",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
           "<level>{message}</level>",
    level=LOG_LEVEL,
    encoding="utf-8"
)
