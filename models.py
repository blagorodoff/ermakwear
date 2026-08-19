# models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager


# ---------- Пользователь (администратор) ----------
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Метод для установки пароля (хеширует строку)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Метод для проверки пароля
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# Функция, которая по id пользователя возвращает объект User (для Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------- Коллекция (например, "Божий промысел") ----------
class Collection(db.Model):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255))       # подпись/лейбл (например, "Православие")
    sort_order = db.Column(db.Integer, default=0) # порядок отображения
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связь с товарами (одна коллекция имеет много товаров)
    products = db.relationship('Product', backref='collection', lazy='dynamic')

    def __repr__(self):
        return f'<Collection {self.title}>'


# ---------- Категория (тип товара: Футболка, Худи, Шорты) ----------
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    products = db.relationship('Product', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


# ---------- Товар ----------
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связь с изображениями товара (несколько фото)
    images = db.relationship('ProductImage', backref='product', lazy='dynamic',
                             cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Product {self.title}>'


# ---------- Изображение товара ----------
class ProductImage(db.Model):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # имя файла в /static/uploads/
    is_primary = db.Column(db.Boolean, default=False)     # главное фото (показывается на карточке)
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<ProductImage {self.filename} for product {self.product_id}>'


# ---------- Изображение галереи (отдельная галерея, если понадобится) ----------
class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<GalleryImage {self.filename}>'