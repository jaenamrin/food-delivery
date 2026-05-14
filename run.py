from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from models import db, User
from routes import main_bp
from commands import seed_cli

app = Flask(__name__)
app.config.from_object(Config)

# --------------------------
# Инициализация базы данных
# --------------------------
db.init_app(app)
migrate = Migrate(app, db)

# --------------------------
# Инициализация системы логина
# --------------------------
login_manager = LoginManager(app)
login_manager.login_view = 'main.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --------------------------
# Регистрация блюпринта
# --------------------------
app.register_blueprint(main_bp)

# --------------------------
# Команды Flask CLI
# --------------------------
app.cli.add_command(seed_cli)

# --------------------------
# Запуск приложения
# --------------------------
if __name__ == '__main__':
    app.run(debug=True)

