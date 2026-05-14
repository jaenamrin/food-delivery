from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)  # + index
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)  # + index
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(30))
    address = db.Column(db.String(255))
    cashback_balance = db.Column(db.Float, default=0.0)

    # Связи
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)  # + index для поиска
    city = db.Column(db.String(100), index=True)  # + index
    delivery_time = db.Column(db.Integer, default=30)
    image = db.Column(db.String(200), default='images/default.png')
    menu_items = db.relationship('MenuItem', backref='restaurant', lazy=True, cascade='all, delete-orphan')


class MenuItem(db.Model):
    __tablename__ = 'menu_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)  # + index для поиска
    price = db.Column(db.Float, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id', ondelete='CASCADE'), nullable=False)
    description = db.Column(db.String(400))
    weight = db.Column(db.String(50))
    image = db.Column(db.String(200), default='images/default.png')
    category = db.Column(db.String(50), default='other')  # НОВОЕ ПОЛЕ: burger, sushi, pizza, breakfast


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    address = db.Column(db.String(255))
    total_price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    use_cashback = db.Column(db.Boolean, default=False)
    cashback_used = db.Column(db.Float, default=0.0)
    is_paid = db.Column(db.Boolean, default=False)
    payment_id = db.Column(db.String(50), default=None)
    paid_at = db.Column(db.DateTime, default=None)

    # ИСПРАВЛЕНО: добавил back_populates
    user = db.relationship('User', back_populates='orders')
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    menu_item = db.relationship('MenuItem')


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(30))
    address = db.Column(db.String(255))
    cashback_balance = db.Column(db.Float, default=0.0)
    is_admin = db.Column(db.Boolean, default=False)

    # ИСПРАВЛЕНО: убрал backref, оставил только back_populates
    orders = db.relationship('Order', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
