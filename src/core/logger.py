import sys
from loguru import logger
from src.core.logging_config import (
    LOG_LEVEL, LOG_DIR, LOG_FORMAT,
    LOG_RETENTION_DAYS, LOG_ROTATION_SIZE
)

# Удаляем стандартный обработчик
logger.remove()

# Консольный вывод
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    colorize=True
)

# Основной файл логов
logger.add(
    LOG_DIR / "app.log",
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    rotation=LOG_ROTATION_SIZE,
    retention=LOG_RETENTION_DAYS,
    compression="zip",
    encoding="utf-8"
)

# Отдельный файл для ошибок
logger.add(
    LOG_DIR / "errors.log",
    format=LOG_FORMAT,
    level="ERROR",
    rotation="1 week",
    retention=LOG_RETENTION_DAYS,
    compression="zip",
    encoding="utf-8",
    backtrace=True,
    diagnose=True
)

# # Отдельный файл для API запросов
# logger.add(
#     LOG_DIR / "api.log",
#     format=LOG_FORMAT,
#     level=LOG_LEVEL,
#     rotation="1 day",
#     retention=LOG_RETENTION_DAYS,
#     compression="zip",
#     encoding="utf-8",
#     filter=lambda record: "api" in record["extra"]
# )
