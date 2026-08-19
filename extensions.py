# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Объект базы данных. Через него мы будем делать запросы и создавать таблицы.
db = SQLAlchemy()

# Объект для управления входом в систему.
login_manager = LoginManager()