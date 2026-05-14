from app import app, db
from models import Restaurant, MenuItem

with app.app_context():
    db.create_all()

    if Restaurant.query.count() == 0:
        r1 = Restaurant(name="Pizza House", city="Москва", delivery_time=40)
        r2 = Restaurant(name="Sushi Time", city="Санкт-Петербург", delivery_time=35)
        db.session.add_all([r1, r2])
        db.session.commit()

        menu_items = [
            MenuItem(name="Пепперони", price=550, description="Классическая пицца с колбасой и сыром", weight="500 г", restaurant_id=r1.id),
            MenuItem(name="Маргарита", price=490, description="Томатный соус, сыр моцарелла, базилик", weight="450 г", restaurant_id=r1.id),
            MenuItem(name="Филадельфия", price=620, description="Ролл с лососем, сыром и огурцом", weight="300 г", restaurant_id=r2.id),
            MenuItem(name="Калифорния", price=580, description="Ролл с крабом и икрой масаго", weight="280 г", restaurant_id=r2.id)
        ]
        db.session.add_all(menu_items)
        db.session.commit()

        print("✅ Добавлены тестовые рестораны и блюда!")
    else:
        print("ℹ️ Данные уже существуют.")