# Анализ температурных данных

Веб-приложение для анализа исторических температурных данных и мониторинга текущей температуры через OpenWeatherMap API.

## Возможности

- Загрузка и анализ исторических температурных данных
- Выявление температурных аномалий
- Визуализация температурных трендов
- Мониторинг текущей температуры через OpenWeatherMap API
- Сравнение текущей температуры с историческими данными

## Структура проекта
```sh
├── LICENSE                             # лицензия  
├── README.md                           # описание проекта  
├── requirements.txt                    # зависимости  
├── streamlit_app.py                    # веб-приложение  
├── main.py                             # консольное приложение  
├── homework1.md                        # описание задания  
├── data                                # данные  
│   └── temperature_data.csv            # пример данных (для веб-приложения)
├── logs                                # логи  (будет создан)
│   ├── app.log                         # логи веб-приложения  
│   └── errors.log                      # логи ошибок  
├── notebooks                           # ноутбуки  
│   ├── data_analysis.ipynb             # анализ данных  
│   └── ИИ_ДЗ_1_(ОБЯЗАТЕЛЬНОЕ).ipynb    # исходное задание  
├── src                                 # исходный код  
│   ├── config.py                       # конфигурация  
│   ├── core                            # базовые компоненты  
│   │   ├── logger.py                   # инициализация логгера  
│   │   └── logging_config.py           # базовые настройки логирования  
│   ├── services                        # сервисы  
│   │   ├── analysis_service.py         # анализ температурных данных  
│   │   ├── visualization_service.py    # визуализация данных  
│   │   └── weather_service.py          # работа с OpenWeatherMap API  
│   └── utils.py                        # вспомогательные функции  
```
## Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/psaw/hse-ai24-python-hw1.git temperature-analysis
cd temperature-analysis
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/MacOS
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` в корневой директории и добавьте API ключ:
```
OPENWEATHER_API_KEY=ваш_ключ_api
```

## Использование

### Веб-приложение

Запустите Streamlit приложение:
```bash
streamlit run streamlit_app.py
```

Приложение будет доступно по адресу: http://localhost:8501

### Консольное приложение

Для анализа данных через командную строку:
```bash
python main.py
```

## Основные компоненты

### AnalysisService
Сервис для анализа температурных данных:
- Вычисление скользящего среднего
- Расчет сезонной статистики
- Определение аномалий

### WeatherService
Сервис для работы с OpenWeatherMap API:
- Получение текущей температуры
- Кэширование результатов
- Определение аномальности текущей температуры

### VisualizationService
Сервис для визуализации данных:
- Временные ряды температур
- Сезонные графики
- Тепловые карты аномалий

## Требования

- Python 3.12
- streamlit
- pandas
- matplotlib
- seaborn
- aiohttp
- aiofiles
- python-dotenv
- loguru

## Лицензия

MIT License

