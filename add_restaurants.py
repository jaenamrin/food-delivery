# add_restaurants.py
from app import app
from models import db, Restaurant, MenuItem

with app.app_context():
    # Проверяем, сколько ресторанов уже есть
    existing = Restaurant.query.count()
    print(f"📊 В базе уже {existing} ресторанов")

    # Создаём недостающие рестораны
    new_restaurants = []

    # Проверяем и добавляем Pizza House
    if not Restaurant.query.filter_by(name="Pizza House").first():
        new_restaurants.append(
            Restaurant(name="Pizza House", city="Москва", delivery_time=40, image="images/pizza1.png"))
        print("➕ Добавлен Pizza House")

    # Sushi Time
    if not Restaurant.query.filter_by(name="Sushi Time").first():
        new_restaurants.append(
            Restaurant(name="Sushi Time", city="Санкт-Петербург", delivery_time=35, image="images/sushi.png"))
        print("➕ Добавлен Sushi Time")

    # Burger King
    if not Restaurant.query.filter_by(name="Burger King").first():
        new_restaurants.append(
            Restaurant(name="Burger King", city="Москва", delivery_time=30, image="images/burger_king.png"))
        print("➕ Добавлен Burger King")

    # Taco Bell
    if not Restaurant.query.filter_by(name="Taco Bell").first():
        new_restaurants.append(
            Restaurant(name="Taco Bell", city="Казань", delivery_time=25, image="images/taco_bell.png"))
        print("➕ Добавлен Taco Bell")

    # Pasta Palace
    if not Restaurant.query.filter_by(name="Pasta Palace").first():
        new_restaurants.append(
            Restaurant(name="Pasta Palace", city="Новосибирск", delivery_time=45, image="images/pasta_palace.png"))
        print("➕ Добавлен Pasta Palace")

    # Ramen House
    if not Restaurant.query.filter_by(name="Ramen House").first():
        new_restaurants.append(
            Restaurant(name="Ramen House", city="Москва", delivery_time=50, image="images/ramen_house.png"))
        print("➕ Добавлен Ramen House")

    # Steak Grill
    if not Restaurant.query.filter_by(name="Steak Grill").first():
        new_restaurants.append(
            Restaurant(name="Steak Grill", city="Санкт-Петербург", delivery_time=55, image="images/steak_grill.png"))
        print("➕ Добавлен Steak Grill")

    # Salad Bar
    if not Restaurant.query.filter_by(name="Salad Bar").first():
        new_restaurants.append(
            Restaurant(name="Salad Bar", city="Казань", delivery_time=20, image="images/salad_bar.png"))
        print("➕ Добавлен Salad Bar")

    # Dim Sum Express
    if not Restaurant.query.filter_by(name="Dim Sum Express").first():
        new_restaurants.append(
            Restaurant(name="Dim Sum Express", city="Новосибирск", delivery_time=35, image="images/dim_sum.png"))
        print("➕ Добавлен Dim Sum Express")

    # Dessert Heaven
    if not Restaurant.query.filter_by(name="Dessert Heaven").first():
        new_restaurants.append(
            Restaurant(name="Dessert Heaven", city="Москва", delivery_time=30, image="images/dessert_heaven.png"))
        print("➕ Добавлен Dessert Heaven")

    # Сохраняем рестораны
    if new_restaurants:
        db.session.add_all(new_restaurants)
        db.session.commit()
        print(f"\n✅ Добавлено {len(new_restaurants)} ресторанов!")
    else:
        print("\n⚠️ Все рестораны уже существуют в базе!")

    # Показываем итог
    print("\n📋 Текущий список ресторанов:")
    for r in Restaurant.query.all():
        print(f"   - {r.name} ({r.city}) | Доставка: {r.delivery_time} мин")