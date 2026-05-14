# create_full_db.py
import os
import sqlite3
from werkzeug.security import generate_password_hash

# Удаляем старый файл БД, если есть
db_path = 'food.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"🗑️ Старый файл {db_path} удалён.")

# Создаём новую базу данных
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Таблица пользователей
cursor.execute('''
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    phone VARCHAR(30),
    address VARCHAR(255),
    cashback_balance FLOAT DEFAULT 0,
    is_admin BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 2. Таблица ресторанов
cursor.execute('''
CREATE TABLE restaurant (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(150) NOT NULL,
    city VARCHAR(100),
    delivery_time INTEGER DEFAULT 30,
    image VARCHAR(200) DEFAULT 'images/default.png'
)
''')

# 3. Таблица блюд (с категорией dessert!)
cursor.execute('''
CREATE TABLE menu_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    price FLOAT NOT NULL,
    restaurant_id INTEGER NOT NULL,
    description VARCHAR(400),
    weight VARCHAR(50),
    image VARCHAR(200) DEFAULT 'images/default.png',
    category VARCHAR(50) DEFAULT 'other',
    FOREIGN KEY (restaurant_id) REFERENCES restaurant (id)
)
''')

# 4. Таблица заказов
cursor.execute('''
CREATE TABLE "order" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    address VARCHAR(255),
    total_price FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    use_cashback BOOLEAN DEFAULT 0,
    cashback_used FLOAT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user (id)
)
''')

# 5. Таблица позиций заказа
cursor.execute('''
CREATE TABLE order_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (order_id) REFERENCES "order" (id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_item (id)
)
''')

print("✅ Все 5 таблиц созданы!")

# --- Добавляем администратора ---
password_hash = generate_password_hash("admin123")
cursor.execute('''
INSERT INTO user (username, email, password_hash, phone, address, cashback_balance, is_admin)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', ("Admin", "admin@food.com", password_hash, "+79990000000", "Администрация", 0, 1))

# --- Добавляем рестораны ---
restaurants = [
    ("Pizza House", "Москва", 40, "images/pizza1.png"),
    ("Sushi Time", "Санкт-Петербург", 35, "images/sushi.png"),
    ("Burger King", "Москва", 30, "images/burger_king.png"),
    ("Taco Bell", "Казань", 25, "images/taco_bell.png"),
    ("Pasta Palace", "Новосибирск", 45, "images/pasta_palace.png"),
    ("Ramen House", "Москва", 50, "images/ramen_house.png"),
    ("Steak Grill", "Санкт-Петербург", 55, "images/steak_grill.png"),
    ("Salad Bar", "Казань", 20, "images/salad_bar.png"),
    ("Dim Sum Express", "Новосибирск", 35, "images/dim_sum.png"),
    ("Dessert Heaven", "Москва", 30, "images/dessert_heaven.png")
]

for name, city, delivery, img in restaurants:
    cursor.execute('''
    INSERT INTO restaurant (name, city, delivery_time, image)
    VALUES (?, ?, ?, ?)
    ''', (name, city, delivery, img))

print("✅ 10 ресторанов добавлены!")

# Получаем ID ресторанов для привязки блюд
cursor.execute("SELECT id, name FROM restaurant")
restaurant_ids = {name: id for id, name in cursor.fetchall()}

# --- Добавляем блюда с категориями (включая десерты!) ---
menu_items = [
    # Pizza House (пицца)
    ("Маргарита", 490, restaurant_ids["Pizza House"], "Томатный соус, сыр моцарелла, базилик", "450 г",
     "images/margarita.png", "pizza"),
    ("Пепперони", 550, restaurant_ids["Pizza House"], "Классическая пицца с колбасой и сыром", "500 г",
     "images/pepperoni.png", "pizza"),
    ("Гавайская", 520, restaurant_ids["Pizza House"], "Сыр, ветчина, ананас", "480 г", "images/hawai.png", "pizza"),
    ("Четыре сыра", 600, restaurant_ids["Pizza House"], "Моцарелла, пармезан, дорблю, гауда", "500 г",
     "images/four_cheese.png", "pizza"),

    # Sushi Time (суши)
    ("Филадельфия", 620, restaurant_ids["Sushi Time"], "Ролл с лососем, сыром и огурцом", "300 г",
     "images/philadelphia.png", "sushi"),
    ("Калифорния", 580, restaurant_ids["Sushi Time"], "Ролл с крабом и икрой масаго", "280 г", "images/california.png",
     "sushi"),

    # Burger King (бургеры)
    ("Классический бургер", 350, restaurant_ids["Burger King"], "Говяжья котлета, салат, помидор, соус", "250 г",
     "images/restaurant3_dish1.png", "burger"),
    ("Чизбургер", 400, restaurant_ids["Burger King"], "Бургер с плавленым сыром и соусом", "260 г",
     "images/restaurant3_dish2.png", "burger"),
    ("Беконбургер", 450, restaurant_ids["Burger King"], "Бургер с беконом и соусом BBQ", "270 г",
     "images/restaurant3_dish3.png", "burger"),

    # Завтраки (добавим в Pizza House)
    ("Овсяная каша с ягодами", 250, restaurant_ids["Pizza House"], "Полезный завтрак с ягодами", "250 г",
     "images/oatmeal.png", "breakfast"),
    ("Сырники со сметаной", 320, restaurant_ids["Pizza House"], "Домашние сырники", "200 г", "images/syrniki.png",
     "breakfast"),

    # Напитки (добавим в Pizza House)
    ("Coca-cola", 100, restaurant_ids["Pizza House"], "Газированный напиток", "330 мл", "images/cola.png", "drink"),
    ("Чай Ассам", 220, restaurant_ids["Pizza House"], "Классический черный чай", "500 мл", "images/tea.png", "drink"),

    # ========== ДЕСЕРТЫ (новая категория!) ==========
    ("Тирамису", 350, restaurant_ids["Pizza House"], "Классический итальянский десерт с маскарпоне", "150 г",
     "images/tiramisu.png", "dessert"),
    ("Чизкейк", 320, restaurant_ids["Dessert Heaven"], "Нежный чизкейк с ягодным соусом", "180 г",
     "images/cheesecake.png", "dessert"),
    ("Панна-котта", 280, restaurant_ids["Dessert Heaven"], "Сливочный десерт с ягодным топингом", "120 г",
     "images/panna_cotta.png", "dessert"),
    ("Фондан", 380, restaurant_ids["Burger King"], "Шоколадный кекс с жидкой начинкой", "120 г", "images/fondant.png",
     "dessert"),
    ("Мороженое пломбир", 150, restaurant_ids["Dessert Heaven"], "Классическое мороженое", "100 г",
     "images/icecream.png", "dessert"),
]

for name, price, rest_id, desc, weight, img, cat in menu_items:
    cursor.execute('''
    INSERT INTO menu_item (name, price, restaurant_id, description, weight, image, category)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, price, rest_id, desc, weight, img, cat))

conn.commit()
conn.close()

print("✅ Блюда добавлены (включая десерты!)")
print("\n" + "=" * 50)
print("🎉 БАЗА ДАННЫХ ГОТОВА!")
print("=" * 50)
print("👑 Администратор: admin@food.com / admin123")
print("🍕 Ресторанов: 10")
print("🍽️ Блюд с десертами: добавлены")
print("\n🚀 Запустите 'python run.py'")