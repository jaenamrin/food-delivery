from flask.cli import AppGroup
from models import db, Restaurant, MenuItem, User
from werkzeug.security import generate_password_hash

seed_cli = AppGroup("seed")


@seed_cli.command("all")
def seed_db():
    from app import app

    with app.app_context():
        db.drop_all()
        db.create_all()

        # --- Создаём администратора ---
        if User.query.filter_by(email="admin@food.com").count() == 0:
            admin = User(
                username="Admin",
                email="admin@food.com",
                phone="+79990000000",
                address="Администрация",
                cashback_balance=0,
                is_admin=True
            )
            admin.set_password("admin123")
            db.session.add(admin)
            print("✅ Создан администратор: admin@food.com / admin123")

        # --- Создаём тестового пользователя ---
        if User.query.filter_by(email="test@example.com").count() == 0:
            test_user = User(
                username="testuser",
                email="test@example.com",
                phone="+79991234567",
                address="Тестовый адрес, д. 1",
                cashback_balance=150.0
            )
            test_user.set_password("password123")
            db.session.add(test_user)
            db.session.commit()

        if Restaurant.query.count() == 0:
            # --- Создаём рестораны ---
            r1 = Restaurant(name="Pizza House", city="Москва", delivery_time=40, image="images/pizza1.png")
            r2 = Restaurant(name="Sushi Time", city="Санкт-Петербург", delivery_time=35, image="images/sushi.png")
            r3 = Restaurant(name="Burger King", city="Москва", delivery_time=30, image="images/burger_king.png")
            r4 = Restaurant(name="Taco Bell", city="Казань", delivery_time=25, image="images/taco_bell.png")
            r5 = Restaurant(name="Pasta Palace", city="Новосибирск", delivery_time=45, image="images/pasta_palace.png")
            r6 = Restaurant(name="Ramen House", city="Москва", delivery_time=50, image="images/ramen_house.png")
            r7 = Restaurant(name="Steak Grill", city="Санкт-Петербург", delivery_time=55, image="images/steak_grill.png")
            r8 = Restaurant(name="Salad Bar", city="Казань", delivery_time=20, image="images/salad_bar.png")
            r9 = Restaurant(name="Dim Sum Express", city="Новосибирск", delivery_time=35, image="images/dim_sum.png")
            r10 = Restaurant(name="Dessert Heaven", city="Москва", delivery_time=30, image="images/dessert_heaven.png")

            restaurants = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10]
            db.session.add_all(restaurants)
            db.session.flush()

            # --- Блюда ---
            menu_items = [
                # ========== Pizza House ==========
                MenuItem(name="Маргарита", price=490, description="Томатный соус, сыр моцарелла, базилик",
                         weight="450 г", restaurant_id=r1.id, image="images/margarita.png", category="pizza"),
                MenuItem(name="Пепперони", price=550, description="Классическая пицца с колбасой и сыром",
                         weight="500 г", restaurant_id=r1.id, image="images/pepperoni.png", category="pizza"),
                MenuItem(name="Гавайская", price=520, description="Сыр, ветчина, ананас", weight="480 г",
                         restaurant_id=r1.id, image="images/hawai.png", category="pizza"),
                MenuItem(name="Четыре сыра", price=600, description="Моцарелла, пармезан, дорблю, гауда",
                         weight="500 г", restaurant_id=r1.id, image="images/four_cheese.png", category="pizza"),
                MenuItem(name="Карбонара", price=580, description="Сыр, бекон, сливочный соус", weight="470 г",
                         restaurant_id=r1.id, image="images/carbonara.png", category="pizza"),
                MenuItem(name="Маргарита с базиликом", price=495, description="Свежий базилик и томаты", weight="450 г",
                         restaurant_id=r1.id, image="images/margarita_basil.png", category="pizza"),
                MenuItem(name="Молочный коктейль: ванильный", price=350, description="Молоко, мороженое, сироп",
                         weight="300 мл", restaurant_id=r1.id, image="images/milk.png", category="drink"),
                MenuItem(name="Вегетарианская", price=500, description="Овощи и сыр", weight="480 г",
                         restaurant_id=r1.id, image="images/veggie.png", category="pizza"),
                MenuItem(name="Coca-cola", price=100, description="Газированный напиток", weight="330 мл",
                         restaurant_id=r1.id, image="images/cola.png", category="drink"),
                MenuItem(name="Чай Ассам", price=220, description="Классический черный чай", weight="500 мл",
                         restaurant_id=r1.id, image="images/tea.png", category="drink"),
                MenuItem(name="Овсяная каша с ягодами", price=250, description="Полезный завтрак с ягодами",
                         weight="250 г", restaurant_id=r1.id, image="images/oatmeal.png", category="breakfast"),
                MenuItem(name="Сырники со сметаной", price=320, description="Домашние сырники", weight="200 г",
                         restaurant_id=r1.id, image="images/syrniki.png", category="breakfast"),
                MenuItem(name="Тирамису", price=350, description="Классический итальянский десерт с маскарпоне",
                         weight="150 г", restaurant_id=r1.id, image="images/tiramisu.png", category="dessert"),
                MenuItem(name="Чизкейк", price=320, description="Нежный чизкейк с ягодным соусом", weight="180 г",
                         restaurant_id=r1.id, image="images/cheesecake.png", category="dessert"),

                # ========== Sushi Time ==========
                MenuItem(name="Филадельфия", price=620, description="Ролл с лососем, сыром и огурцом", weight="300 г",
                         restaurant_id=r2.id, image="images/philadelphia.png", category="sushi"),
                MenuItem(name="Калифорния", price=580, description="Ролл с крабом и икрой масаго", weight="280 г",
                         restaurant_id=r2.id, image="images/california.png", category="sushi"),
                MenuItem(name="Ролл с тунцом", price=600, description="Тунец и огурец", weight="300 г",
                         restaurant_id=r2.id, image="images/tuna_roll.png", category="sushi"),
                MenuItem(name="Ролл с угрем", price=650, description="Угорь и соус унаги", weight="310 г",
                         restaurant_id=r2.id, image="images/eel_roll.png", category="sushi"),
                MenuItem(name="Сет ассорти", price=1200, description="Сет роллов на компанию", weight="1000 г",
                         restaurant_id=r2.id, image="images/sushi_set.png", category="sushi"),
                MenuItem(name="Футомаки", price=700, description="Толстый ролл с рыбой и овощами", weight="350 г",
                         restaurant_id=r2.id, image="images/futomaki.png", category="sushi"),
                MenuItem(name="Нигири с лососем", price=400, description="Лосось на рисе", weight="100 г",
                         restaurant_id=r2.id, image="images/nigiri_salmon.png", category="sushi"),
                MenuItem(name="Нигири с тунцом", price=420, description="Тунец на рисе", weight="100 г",
                         restaurant_id=r2.id, image="images/nigiri_tuna.png", category="sushi"),
                MenuItem(name="Молочный коктейль: шоколадный", price=560, description="Молоко, мороженое, шоколадный сироп",
                         weight="500 г", restaurant_id=r2.id, image="images/chocomilk.png", category="drink"),
                MenuItem(name="Молочный коктейль: ванильный", price=560, description="Молоко, мороженое, ванильный сироп",
                         weight="500 г", restaurant_id=r2.id, image="images/milk.png", category="drink"),
                MenuItem(name="Молочный коктейль: клубничный", price=560, description="Молоко, мороженое, клубничный сироп",
                         weight="500 г", restaurant_id=r2.id, image="images/strawmilk.png", category="drink"),
                MenuItem(name="Яблочный сок", price=280, description="Свежевыжатый яблочный сок", weight="300 мл",
                         restaurant_id=r2.id, image="images/apple_juice.png", category="drink"),
                MenuItem(name="Зеленый чай", price=200, description="Традиционный зеленый чай", weight="250 мл",
                         restaurant_id=r2.id, image="images/green_tea.png", category="drink"),
                MenuItem(name="Панна-котта", price=280, description="Сливочный десерт с ягодным топингом",
                         weight="120 г", restaurant_id=r2.id, image="images/panna_cotta.png", category="dessert"),

                # ========== Burger King ==========
                MenuItem(name="Классический бургер", price=350, description="Говяжья котлета, салат, помидор, соус",
                         weight="250 г", restaurant_id=r3.id, image="images/restaurant3_dish1.png", category="burger"),
                MenuItem(name="Чизбургер", price=400, description="Бургер с плавленым сыром и соусом", weight="260 г",
                         restaurant_id=r3.id, image="images/restaurant3_dish2.png", category="burger"),
                MenuItem(name="Беконбургер", price=450, description="Бургер с беконом и соусом BBQ", weight="270 г",
                         restaurant_id=r3.id, image="images/restaurant3_dish3.png", category="burger"),
                MenuItem(name="Дабл Чизбургер", price=500, description="Двойная котлета с сыром", weight="300 г",
                         restaurant_id=r3.id, image="images/restaurant3_dish4.png", category="burger"),
                MenuItem(name="Куриный бургер", price=380, description="Куриная котлета с салатом и соусом",
                         weight="250 г", restaurant_id=r3.id, image="images/restaurant3_dish5.png", category="burger"),
                MenuItem(name="Бургер BBQ", price=470, description="Говяжья котлета с соусом BBQ и карамелизированным луком",
                         weight="280 г", restaurant_id=r3.id, image="images/restaurant3_dish6.png", category="burger"),
                MenuItem(name="Яблочный сок", price=280, description="Свежевыжатый яблочный сок", weight="300 мл",
                         restaurant_id=r3.id, image="images/apple_juice.png", category="drink"),
                MenuItem(name="Бургер с яйцом", price=390, description="Говяжья котлета, яйцо, салат и соус",
                         weight="270 г", restaurant_id=r3.id, image="images/restaurant3_dish8.png", category="burger"),
                MenuItem(name="Мексиканский бургер", price=460, description="Говяжья котлета с перцем чили и острым соусом",
                         weight="280 г", restaurant_id=r3.id, image="images/restaurant3_dish9.png", category="burger"),
                MenuItem(name="Coca-cola", price=100, description="Газированный напиток", weight="330 мл",
                         restaurant_id=r3.id, image="images/cola.png", category="drink"),
                MenuItem(name="Бургер с яйцом и беконом", price=320, description="Завтрак-бургер", weight="230 г",
                         restaurant_id=r3.id, image="images/breakfast_burger.png", category="breakfast"),
                MenuItem(name="Фондан", price=380, description="Шоколадный кекс с жидкой начинкой", weight="120 г",
                         restaurant_id=r3.id, image="images/fondant.png", category="dessert"),

                # ========== Taco Bell ==========
                MenuItem(name="Тако с курицей", price=350, description="Курица, салат, соус", weight="200 г",
                         restaurant_id=r4.id, image="images/taco_chicken.png", category="burger"),
                MenuItem(name="Буррито", price=400, description="Мясо, рис, овощи", weight="350 г",
                         restaurant_id=r4.id, image="images/burrito.png", category="burger"),

                # ========== Pasta Palace ==========
                MenuItem(name="Спагетти Карбонара", price=550, description="Паста, бекон, сливочный соус",
                         weight="400 г", restaurant_id=r5.id, image="images/spag_carbonara.png", category="pizza"),
                MenuItem(name="Лазанья", price=600, description="Мясо, соус, сыр", weight="450 г",
                         restaurant_id=r5.id, image="images/lasagna.png", category="pizza"),

                # ========== Ramen House ==========
                MenuItem(name="Рамен с курицей", price=500, description="Лапша, бульон, курица", weight="400 г",
                         restaurant_id=r6.id, image="images/ramen_chicken.png", category="sushi"),
                MenuItem(name="Рамен с говядиной", price=550, description="Лапша, бульон, говядина", weight="450 г",
                         restaurant_id=r6.id, image="images/ramen_beef.png", category="sushi"),

                # ========== Steak Grill ==========
                MenuItem(name="Стейк Рибай", price=1200, description="Говядина, специи", weight="350 г",
                         restaurant_id=r7.id, image="images/ribeye.png", category="burger"),
                MenuItem(name="Стейк Тибон", price=1400, description="Говядина, специи", weight="400 г",
                         restaurant_id=r7.id, image="images/tbone.png", category="burger"),

                # ========== Salad Bar ==========
                MenuItem(name="Цезарь с курицей", price=350, description="Салат, курица, соус", weight="250 г",
                         restaurant_id=r8.id, image="images/caesar.png", category="breakfast"),
                MenuItem(name="Греческий салат", price=300, description="Салат, сыр фета, оливки", weight="200 г",
                         restaurant_id=r8.id, image="images/greek.png", category="breakfast"),

                # ========== Dim Sum Express ==========
                MenuItem(name="Дим сам с креветкой", price=400, description="Креветки, тесто", weight="150 г",
                         restaurant_id=r9.id, image="images/dimsum_shrimp.png", category="sushi"),
                MenuItem(name="Дим сам с овощами", price=350, description="Овощи, тесто", weight="150 г",
                         restaurant_id=r9.id, image="images/dimsum_veggie.png", category="sushi"),

                # ========== Dessert Heaven ==========
                MenuItem(name="Тирамису", price=300, description="Десерт с кофе и сыром маскарпоне", weight="150 г",
                         restaurant_id=r10.id, image="images/tiramisu.png", category="dessert"),
                MenuItem(name="Мороженое пломбир", price=150, description="Классическое мороженое", weight="100 г",
                         restaurant_id=r10.id, image="images/icecream.png", category="dessert"),
            ]

            db.session.add_all(menu_items)
            db.session.commit()
            print("✅ Добавлены тестовые рестораны и блюда с категориями!")

        else:
            print("ℹ️ Данные уже существуют.")