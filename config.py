import os

class Config:
    # Путь к базе данных SQLite
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'food.db')

    # Отключаем лишние предупреждения SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Секретный ключ для сессий и CSRF-защиты
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey123'

    # Можно добавить опционально: уровень отладки
    DEBUG = True
