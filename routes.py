from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Restaurant, MenuItem, Order, OrderItem
from forms import RegistrationForm, LoginForm, ProfileForm
from datetime import datetime, timedelta
from sqlalchemy import or_, func, and_
from functools import wraps
import uuid
from datetime import datetime

main_bp = Blueprint('main', __name__)

# --- Главная ---
@main_bp.route('/')
def index():
    restaurants = Restaurant.query.all()
    return render_template('index.html', restaurants=restaurants)

# --- Страница ресторана ---
@main_bp.route('/restaurant/<int:restaurant_id>')
def restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    return render_template('restaurant.html', restaurant=restaurant, menu_items=menu_items)

# --- Детали блюда ---
@main_bp.route('/menu/<int:item_id>')
def menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    return render_template('menu_item.html', item=item)

# --- Добавить в корзину ---
@main_bp.route('/add_to_cart/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    item = MenuItem.query.get_or_404(item_id)
    cart = session.get('cart', {})
    key = str(item_id)
    if key in cart:
        cart[key]['quantity'] += 1
    else:
        cart[key] = {'name': item.name, 'price': float(item.price), 'quantity': 1, 'image': item.image}
    session['cart'] = cart
    session.modified = True
    flash(f'Блюдо "{item.name}" добавлено в корзину!', 'success')
    return redirect(url_for('main.restaurant', restaurant_id=item.restaurant_id))

# --- Корзина ---
@main_bp.route('/cart')
@login_required
def cart():
    cart = session.get('cart', {})
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())

    # Рассчитываем скидки
    discounts = calculate_discounts(cart, subtotal)

    # Итоговая сумма после скидок
    total_discount = discounts['burger_king_discount']
    final_total = subtotal - total_discount

    return render_template('cart.html',
                           cart=cart,
                           subtotal=subtotal,
                           final_total=final_total,
                           discounts=discounts)


# --- Оформление ---
@main_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Корзина пуста!', 'warning')
        return redirect(url_for('main.cart'))

    address = request.form.get('address')
    if not address:
        flash('Укажите адрес доставки', 'warning')
        return redirect(url_for('main.cart'))

    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    discounts = calculate_discounts(cart, subtotal)

    # Итоговая сумма после скидок
    total_discount = discounts['burger_king_discount']
    final_total = max(0, subtotal - total_discount)

    # НОВОЕ: Проверяем, хочет ли пользователь использовать кэшбэк
    use_cashback = request.form.get('use_cashback') == 'on'
    cashback_to_use = 0
    cashback_balance = current_user.cashback_balance or 0

    if use_cashback and cashback_balance > 0:
        cashback_to_use = min(cashback_balance, final_total)
        final_total = max(0, final_total - cashback_to_use)
        current_user.cashback_balance = cashback_balance - cashback_to_use
        flash(f' Использовано кэшбэка: {cashback_to_use:.0f} ₽. Остаток: {current_user.cashback_balance:.0f} ₽',
              'success')

    # Создаем заказ
    order = Order(
        user_id=current_user.id,
        address=address,
        total_price=final_total,
        use_cashback=use_cashback,
        cashback_used=cashback_to_use,
        is_paid=False
    )
    db.session.add(order)
    db.session.commit()

    # Добавляем товары в заказ
    for item_key, data in cart.items():
        oi = OrderItem(order_id=order.id, menu_item_id=int(item_key), quantity=data['quantity'])
        db.session.add(oi)

    # НАЧИСЛЯЕМ КЭШБЭК НА БАЛАНС ПОЛЬЗОВАТЕЛЯ ТОЛЬКО если не использовали кэшбэк на этот заказ
    if discounts['pizza_house_cashback'] > 0:
        current_user.cashback_balance = (current_user.cashback_balance or 0) + discounts['pizza_house_cashback']
        flash(
            f'Начислен кэшбэк 10% от Pizza House: {discounts["pizza_house_cashback"]:.0f} ₽! Теперь на вашем счету: {current_user.cashback_balance:.0f} ₽',
            'success')

    # Сообщения о скидках
    discount_messages = []
    if discounts['burger_king_discount'] > 0:
        discount_messages.append(f' Применена скидка 20% на Burger King: -{discounts["burger_king_discount"]:.0f} ₽')

    if discounts['free_delivery']:
        discount_messages.append(' Бесплатная доставка!')

    if discount_messages:
        flash(' | '.join(discount_messages), 'success')

    db.session.commit()
    session['cart'] = {}
    flash(f' Заказ #{order.id} оформлен! Осталось оплатить {final_total:.0f} ₽', 'success')
    return redirect(url_for('main.payment_page', order_id=order.id))


# --- Remove from cart ---
@main_bp.route('/remove_from_cart/<item_key>', methods=['POST'])
@login_required
def remove_from_cart(item_key):
    cart = session.get('cart', {})
    if item_key in cart:
        del cart[item_key]
        session['cart'] = cart
        session.modified = True
        flash('Блюдо удалено из корзины', 'success')
    return redirect(url_for('main.cart'))

# --- Register ---
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter(or_(User.username == form.username.data, User.email == form.email.data)).first():
            flash('Пользователь с таким именем/email уже существует.', 'error')
            return redirect(url_for('main.register'))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('main.index'))
    return render_template('register.html', form=form)

# --- Login ---
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)  # ← ТОЛЬКО ЭТО МЕНЯЕТСЯ
            flash(f'Добро пожаловать, {user.username}!', 'success')
            return redirect(url_for('main.index'))
        flash('Неверный email или пароль', 'error')
    return render_template('login.html', form=form)

# --- Logout ---
@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта.', 'info')
    return redirect(url_for('main.index'))

# --- Profile ---
@main_bp.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.id.desc()).all()
    now = datetime.utcnow()
    for order in orders:
        if not order.created_at:
            order.created_at = now
        delivery_times = [it.menu_item.restaurant.delivery_time for it in order.items if it.menu_item]
        max_delivery = max(delivery_times) if delivery_times else 0
        order.is_active = now < order.created_at + timedelta(minutes=max_delivery)
    return render_template('profile.html', user=current_user, orders=orders)

# --- Edit profile ---
# --- Edit profile ---
@main_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        db.session.commit()
        # УБИРАЕМ ЭТУ СТРОКУ (или закомментируем):
        # flash('Данные обновлены!', 'success')
        return redirect(url_for('main.profile'))
    return render_template('edit_profile.html', form=form)


@main_bp.route("/search_items")
def search_items():
    query = request.args.get("q", "").strip()

    if not query or len(query) < 1:
        return jsonify({"menu_items": [], "restaurants": []})

    query_lower = query.lower()

    # Поиск блюд
    menu_items = MenuItem.query.filter(
        db.func.lower(MenuItem.name).contains(query_lower)
    ).limit(10).all()

    # Поиск ресторанов
    restaurants = Restaurant.query.filter(
        db.func.lower(Restaurant.name).contains(query_lower)
    ).limit(10).all()

    return jsonify({
        "menu_items": [{"id": item.id, "name": item.name} for item in menu_items],
        "restaurants": [{"id": r.id, "name": r.name} for r in restaurants],
    })


@main_bp.route('/search')
def search():
    query = request.args.get('query', '').strip()

    if not query or len(query) < 1:
        return redirect(url_for('main.index'))

    # Приводим запрос к нижнему регистру для сравнения
    query_lower = query.lower()

    # Поиск блюд (регистронезависимый + частичное совпадение)
    menu_items = MenuItem.query.filter(
        db.func.lower(MenuItem.name).contains(query_lower)
    ).all()

    # Поиск ресторанов (регистронезависимый + частичное совпадение)
    restaurants = Restaurant.query.filter(
        db.func.lower(Restaurant.name).contains(query_lower)
    ).all()

    return render_template('search_results.html',
                           query=query,
                           search_results=menu_items,
                           restaurants=restaurants)
@main_bp.route('/debug_menu')
def debug_menu():
    """Страница для отладки - показывает все блюда"""
    all_items = MenuItem.query.all()
    result = "<h1>Все блюда в базе:</h1>"
    for item in all_items:
        result += f"<p>{item.id}: {item.name} (ресторан: {item.restaurant.name})</p>"
    return result


# --- Добавь эту функцию для расчета скидок ---
def calculate_discounts(cart, total):
    """Рассчитывает скидки и кэшбэк на основе акций"""
    discounts = {
        'burger_king_discount': 0,  # 20% скидка на Burger King
        'pizza_house_cashback': 0,  # 10% кэшбэк на Pizza House
        'free_delivery': False  # Бесплатная доставка
    }

    # Проверяем товары из Burger King (restaurant_id=3)
    burger_king_items = []
    for item_key, item_data in cart.items():
        item = MenuItem.query.get(int(item_key))
        if item and item.restaurant_id == 3:  # Burger King
            burger_king_items.append(item_data)

    # Скидка 20% на Burger King если есть товары оттуда
    if burger_king_items:
        bk_subtotal = sum(item['price'] * item['quantity'] for item in burger_king_items)
        discounts['burger_king_discount'] = bk_subtotal * 0.20

    # Кэшбэк 10% на Pizza House (restaurant_id=1)
    pizza_house_items = []
    for item_key, item_data in cart.items():
        item = MenuItem.query.get(int(item_key))
        if item and item.restaurant_id == 1:  # Pizza House
            pizza_house_items.append(item_data)

    if pizza_house_items:
        ph_subtotal = sum(item['price'] * item['quantity'] for item in pizza_house_items)
        discounts['pizza_house_cashback'] = ph_subtotal * 0.10

    # Бесплатная доставка от 1000 ₽
    if total >= 1000:
        discounts['free_delivery'] = True

    return discounts


@main_bp.route('/category/<category_name>')
def category(category_name):
    """Показывает рестораны, у которых есть блюда выбранной категории"""

    if category_name == 'all':
        restaurants = Restaurant.query.all()
        category_title = "Все рестораны"
        return render_template('category.html',
                               restaurants=restaurants,
                               category_title=category_title,
                               current_category=category_name)

    # ПРАВИЛЬНОЕ соответствие категорий
    categories_map = {
        'pizza': 'Пицца',
        'burger': 'Бургеры',
        'sushi': 'Суши',
        'breakfast': 'Завтраки',
        'dessert': 'Десерты',      # ← ДОЛЖНО БЫТЬ 'dessert': 'Десерты'
        'drink': 'Напитки',
        'other': 'Другое'
    }

    # Находим все рестораны, у которых есть блюда нужной категории
    restaurants_with_category = db.session.query(Restaurant).join(MenuItem).filter(
        MenuItem.category == category_name
    ).distinct().all()

    category_title = categories_map.get(category_name, category_name)

    return render_template('category.html',
                           restaurants=restaurants_with_category,
                           category_title=category_title,
                           current_category=category_name)
@main_bp.route('/about')
def about():
    return render_template('about.html')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Доступ запрещен. Требуются права администратора.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


# ========== АДМИН-ПАНЕЛЬ ==========

# Главная админ-панели
@main_bp.route('/admin')
@login_required
@admin_required
def admin_panel():
    restaurants = Restaurant.query.all()
    users = User.query.all()
    orders = Order.query.order_by(Order.id.desc()).limit(10).all()
    menu_count = MenuItem.query.count()
    return render_template('admin/admin_panel.html',
                           restaurants=restaurants,
                           users=users,
                           orders=orders,
                           menu_count=menu_count)


# Управление ресторанами
@main_bp.route('/admin/restaurants')
@login_required
@admin_required
def admin_restaurants():
    restaurants = Restaurant.query.all()
    return render_template('admin/admin_restaurants.html', restaurants=restaurants)


@main_bp.route('/admin/restaurant/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_restaurant():
    if request.method == 'POST':
        name = request.form.get('name')
        city = request.form.get('city')
        delivery_time = request.form.get('delivery_time')
        image = request.form.get('image', 'images/default.png')

        restaurant = Restaurant(
            name=name,
            city=city,
            delivery_time=delivery_time,
            image=image
        )
        db.session.add(restaurant)
        db.session.commit()
        flash(f'Ресторан "{name}" добавлен!', 'success')
        return redirect(url_for('main.admin_restaurants'))

    return render_template('admin/admin_restaurant_form.html', title="Добавить ресторан")


@main_bp.route('/admin/restaurant/edit/<int:restaurant_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    if request.method == 'POST':
        restaurant.name = request.form.get('name')
        restaurant.city = request.form.get('city')
        restaurant.delivery_time = request.form.get('delivery_time')
        restaurant.image = request.form.get('image', restaurant.image)
        db.session.commit()
        flash(f'Ресторан "{restaurant.name}" обновлен!', 'success')
        return redirect(url_for('main.admin_restaurants'))

    return render_template('admin/admin_restaurant_form.html', title="Редактировать ресторан", restaurant=restaurant)


@main_bp.route('/admin/restaurant/delete/<int:restaurant_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    name = restaurant.name
    db.session.delete(restaurant)
    db.session.commit()
    flash(f'Ресторан "{name}" удален!', 'warning')
    return redirect(url_for('main.admin_restaurants'))


@main_bp.route('/admin/menu')
@login_required
@admin_required
def admin_menu():
    # Получаем параметры сортировки
    sort_by = request.args.get('sort', 'category')  # default: по категории
    order = request.args.get('order', 'asc')
    search = request.args.get('search', '')

    # Базовый запрос
    query = MenuItem.query

    # Поиск по названию
    if search:
        query = query.filter(MenuItem.name.ilike(f'%{search}%'))

    # Сортировка
    if sort_by == 'category':
        # Сортируем по категориям в определённом порядке
        category_order = ['pizza', 'burger', 'sushi', 'breakfast', 'drink', 'other']
        if order == 'asc':
            menu_items = query.all()
            # Сортируем вручную по заданному порядку категорий
            menu_items.sort(key=lambda x: category_order.index(x.category) if x.category in category_order else 999)
        else:
            menu_items = query.order_by(MenuItem.category.desc()).all()
    elif sort_by == 'price':
        if order == 'asc':
            menu_items = query.order_by(MenuItem.price.asc()).all()
        else:
            menu_items = query.order_by(MenuItem.price.desc()).all()
    elif sort_by == 'name':
        if order == 'asc':
            menu_items = query.order_by(MenuItem.name.asc()).all()
        else:
            menu_items = query.order_by(MenuItem.name.desc()).all()
    elif sort_by == 'restaurant':
        if order == 'asc':
            menu_items = query.order_by(MenuItem.restaurant_id.asc()).all()
        else:
            menu_items = query.order_by(MenuItem.restaurant_id.desc()).all()
    else:
        menu_items = query.all()
        # По умолчанию: сначала по категориям, потом по названию
        category_order = ['pizza', 'burger', 'sushi', 'breakfast', 'drink', 'other']
        menu_items.sort(
            key=lambda x: (category_order.index(x.category) if x.category in category_order else 999, x.name))

    return render_template('admin/admin_menu.html',
                           menu_items=menu_items,
                           sort_by=sort_by,
                           order=order,
                           search=search)

@main_bp.route('/admin/menu/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_menu_item():
    restaurants = Restaurant.query.all()

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        restaurant_id = request.form.get('restaurant_id')
        description = request.form.get('description')
        weight = request.form.get('weight')
        image = request.form.get('image', 'images/default.png')
        category = request.form.get('category', 'other')

        menu_item = MenuItem(
            name=name,
            price=float(price),
            restaurant_id=int(restaurant_id),
            description=description,
            weight=weight,
            image=image,
            category=category
        )
        db.session.add(menu_item)
        db.session.commit()
        flash(f'Блюдо "{name}" добавлено!', 'success')
        return redirect(url_for('main.admin_menu'))

    return render_template('admin/admin_menu_form.html', title="Добавить блюдо", restaurants=restaurants)


@main_bp.route('/admin/menu/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_menu_item(item_id):
    menu_item = MenuItem.query.get_or_404(item_id)
    restaurants = Restaurant.query.all()

    if request.method == 'POST':
        menu_item.name = request.form.get('name')
        menu_item.price = float(request.form.get('price'))
        menu_item.restaurant_id = int(request.form.get('restaurant_id'))
        menu_item.description = request.form.get('description')
        menu_item.weight = request.form.get('weight')
        menu_item.image = request.form.get('image', menu_item.image)
        menu_item.category = request.form.get('category', 'other')
        db.session.commit()
        flash(f'Блюдо "{menu_item.name}" обновлено!', 'success')
        return redirect(url_for('main.admin_menu'))

    return render_template('admin/admin_menu_form.html', title="Редактировать блюдо", menu_item=menu_item,
                           restaurants=restaurants)


@main_bp.route('/admin/menu/delete/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_menu_item(item_id):
    menu_item = MenuItem.query.get_or_404(item_id)
    name = menu_item.name
    db.session.delete(menu_item)
    db.session.commit()
    flash(f'Блюдо "{name}" удалено!', 'warning')
    return redirect(url_for('main.admin_menu'))


# Управление заказами
@main_bp.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template('admin/admin_orders.html', orders=orders)


@main_bp.route('/admin/order/delete/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Заказ удален!', 'warning')
    return redirect(url_for('main.admin_orders'))


# Пользователи
@main_bp.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/admin_users.html', users=users)


@main_bp.route('/admin/user/make_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f'Пользователь {user.username} теперь администратор!', 'success')
    return redirect(url_for('main.admin_users'))


@main_bp.route('/admin/user/remove_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_remove_admin(user_id):
    if user_id == current_user.id:
        flash('Нельзя снять права администратора с самого себя!', 'error')
        return redirect(url_for('main.admin_users'))

    user = User.query.get_or_404(user_id)
    user.is_admin = False
    db.session.commit()
    flash(f'Права администратора у {user.username} сняты.', 'info')
    return redirect(url_for('main.admin_users'))


# --- Страница оплаты ---
@main_bp.route('/payment/<int:order_id>')
@login_required
def payment_page(order_id):
    order = Order.query.get_or_404(order_id)

    # Проверяем, что заказ принадлежит текущему пользователю
    if order.user_id != current_user.id:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('main.index'))

    # Если заказ уже оплачен
    if order.is_paid:
        flash('Этот заказ уже оплачен', 'warning')
        return redirect(url_for('main.profile'))

    return render_template('payment.html', order=order)


# --- Обработка оплаты (симуляция) ---
@main_bp.route('/process_payment/<int:order_id>', methods=['POST'])
@login_required
def process_payment(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('main.index'))

    if order.is_paid:
        flash('Заказ уже оплачен', 'warning')
        return redirect(url_for('main.profile'))

    # Получаем данные карты (для симуляции)
    card_number = request.form.get('card_number', '').replace(' ', '').replace('-', '')
    card_holder = request.form.get('card_holder')
    expiry = request.form.get('expiry')
    cvv = request.form.get('cvv')

    # Простая валидация
    errors = []
    if len(card_number) != 16 or not card_number.isdigit():
        errors.append('Неверный номер карты')
    if not card_holder or len(card_holder) < 3:
        errors.append('Неверное имя держателя')
    if not expiry or len(expiry) != 5:
        errors.append('Неверный срок действия')
    if len(cvv) != 3 or not cvv.isdigit():
        errors.append('Неверный CVV код')

    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('main.payment_page', order_id=order.id))

    # СИМУЛЯЦИЯ УСПЕШНОЙ ОПЛАТЫ
    # В реальном проекте здесь был бы запрос к платежному шлюзу

    order.is_paid = True
    order.payment_id = str(uuid.uuid4())[:8].upper()
    order.paid_at = datetime.utcnow()
    db.session.commit()

    flash(f' Оплата прошла успешно! Номер транзакции: {order.payment_id}', 'success')
    return redirect(url_for('main.profile'))
