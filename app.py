from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from models import db, User
from routes import main_bp
from commands import seed_cli
from flask_migrate import Migrate


# Создаем приложение
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/food_delivery.db'
app.config['SECRET_KEY'] = 'super_secret_key_123'  # обязательно для CSRF и сессий
app.config.from_object(Config)

# Инициализация базы
db.init_app(app)
migrate = Migrate(app, db)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Регистрируем команду seed
app.cli.add_command(seed_cli)
app.register_blueprint(main_bp)

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

