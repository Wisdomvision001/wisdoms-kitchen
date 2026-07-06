
from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)

BASE_DIR = os.path.dirname(__file__)
ADMIN_DATA_FILE = os.path.join(BASE_DIR, 'admin_data.json')
MENU_DATA_FILE = os.path.join(BASE_DIR, 'menu_data.json')
ORDERS_DATA_FILE = os.path.join(BASE_DIR, 'orders.json')
IMAGE_DIR = os.path.join(BASE_DIR, 'static', 'images')
os.makedirs(IMAGE_DIR, exist_ok=True)

# Shop info
SHOP_NAME = "Wisdom's Kitchen"
SLOGAN = "Authentic Taste, Served Fast"

# Bank transfer mock details
BANK_DETAILS = {
    "bank_name": "First Italian Bank Nigeria",
    "account_name": "Wisdom's Kitchen Ltd",
    "account_number": "1234567890"
}

DEFAULT_ADMIN = {
    'username': 'admin',
    'password': 'wisdom123',
    'bank_name': BANK_DETAILS['bank_name'],
    'account_name': BANK_DETAILS['account_name'],
    'account_number': BANK_DETAILS['account_number'],
}


def load_json_file(path, default):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(default, f, indent=2)
    return default.copy()


def save_json_file(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def load_admin_data():
    data = load_json_file(ADMIN_DATA_FILE, DEFAULT_ADMIN)
    changed = False
    if not data.get('username'):
        data['username'] = DEFAULT_ADMIN['username']
        changed = True
    if not data.get('password'):
        data['password'] = DEFAULT_ADMIN['password']
        changed = True
    if not data.get('bank_name'):
        data['bank_name'] = DEFAULT_ADMIN['bank_name']
        changed = True
    if not data.get('account_name'):
        data['account_name'] = DEFAULT_ADMIN['account_name']
        changed = True
    if not data.get('account_number'):
        data['account_number'] = DEFAULT_ADMIN['account_number']
        changed = True
    if changed:
        save_admin_data(data)
    return data


def save_admin_data(data):
    save_json_file(ADMIN_DATA_FILE, data)


def load_menu_data():
    default_menu = [
        {'id': 1, 'name': 'Margherita Pizza', 'image': 'margherita.jpg', 'price': 11500,
            'desc': 'Crisp, thin crust topped with melted mozzarella, fresh basil, and vibrant tomato — a simple classic.'},
        {'id': 2, 'name': 'Pepperoni Pizza', 'image': 'Pepperoni.jpg', 'price': 15000,
            'desc': 'Golden edges and bubbling cheese crowned with spicy pepperoni that sizzles with every bite.'},
        {'id': 3, 'name': 'Spaghetti Marinara', 'image': 'spaghetti.jpg', 'price': 14000,
            'desc': 'Al dente spaghetti in a slow-simmered tomato sauce, kissed with garlic, herbs, and a shower of parmesan.'},
        {'id': 4, 'name': 'Penne Arrabbiata', 'image': 'penne.jpg', 'price': 12000,
            'desc': 'Penne tossed in a fiery tomato-chili sauce — bright, zesty, and full of personality.'},
        {'id': 5, 'name': 'Side Chips', 'image': 'side.jpg', 'price': 3000,
            'desc': 'Crispy, golden fries seasoned with sea salt — the perfect crunchy companion.'},
        {'id': 6, 'name': 'Combo: Slice + Chips', 'image': 'combo.jpg', 'price': 2000,
            'desc': 'A satisfying pairing of a warm slice and crispy chips — comfort food done right.'}
    ]
    data = load_json_file(MENU_DATA_FILE, default_menu)
    normalized = []
    for item in data:
        normalized.append({
            'id': int(item.get('id', 0)),
            'name': str(item.get('name', '')).strip(),
            'image': str(item.get('image', 'placeholder.jpg')).strip(),
            'price': float(item.get('price', 0)),
            'desc': str(item.get('desc', '')).strip(),
        })
    return normalized


def save_menu_data(menu):
    save_json_file(MENU_DATA_FILE, menu)


def load_orders_data():
    return load_json_file(ORDERS_DATA_FILE, [])


def save_orders_data(orders):
    save_json_file(ORDERS_DATA_FILE, orders)


def summarize_orders_for_day(orders, day=None):
    if day is None:
        day = datetime.now().date().isoformat()

    order_count = 0
    item_count = 0
    revenue = 0.0

    for order in orders:
        created_at = order.get('created_at', '')
        if created_at:
            try:
                order_day = datetime.fromisoformat(
                    created_at.replace('Z', '+00:00')).date().isoformat()
            except ValueError:
                order_day = ''
        else:
            order_day = ''

        if order_day and order_day != day:
            continue

        order_count += 1
        for item in order.get('items', []):
            item_count += int(item.get('qty', 0))
        revenue += float(order.get('total', 0))

    return {
        'order_count': order_count,
        'item_count': item_count,
        'revenue': round(revenue, 2),
    }


admin_data = load_admin_data()
ADMIN_USERNAME = admin_data['username']
ADMIN_PASSWORD = admin_data['password']
BANK_DETAILS = {
    'bank_name': admin_data.get('bank_name', BANK_DETAILS['bank_name']),
    'account_name': admin_data.get('account_name', BANK_DETAILS['account_name']),
    'account_number': admin_data.get('account_number', BANK_DETAILS['account_number']),
}
MENU = load_menu_data()
ORDERS = load_orders_data()


def get_item(item_id):
    for item in MENU:
        if item['id'] == item_id:
            return item
    return None


def is_admin_logged_in():
    return session.get('admin_logged_in', False)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in():
        return redirect(url_for('admin'))

    error = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        error = 'Invalid username or password.'

    return render_template('admin_login.html', shop=SHOP_NAME, slogan=SLOGAN, error=error)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/')
def home():
    return render_template('home.html', shop=SHOP_NAME, slogan=SLOGAN)


@app.route('/menu')
def menu():
    return render_template('menu.html', menu=MENU, shop=SHOP_NAME)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))

    global ADMIN_USERNAME, ADMIN_PASSWORD, BANK_DETAILS
    message = ''
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_item':
            name = request.form.get('name', '').strip()
            desc = request.form.get('desc', '').strip()
            price = float(request.form.get('price') or 0)
            image_filename = request.form.get('image', '').strip()
            image_file = request.files.get('image_file')
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(IMAGE_DIR, filename)
                image_file.save(image_path)
                image_filename = filename
            image_filename = image_filename or 'placeholder.jpg'
            next_id = max((item['id'] for item in MENU), default=0) + 1
            MENU.append({
                'id': next_id,
                'name': name,
                'image': image_filename,
                'price': price,
                'desc': desc,
            })
            save_menu_data(MENU)
            message = f'Added menu item: {name}'
        elif action == 'update_item':
            item_id = request.form.get('item_id')
            item = get_item(int(item_id)) if item_id else None
            if item:
                item['name'] = request.form.get('name', item['name']).strip()
                item['price'] = float(
                    request.form.get('price') or item['price'])
                item['desc'] = request.form.get('desc', item['desc']).strip()
                image_filename = request.form.get('image', '').strip()
                image_file = request.files.get('image_file')
                if image_file and image_file.filename:
                    filename = secure_filename(image_file.filename)
                    image_path = os.path.join(IMAGE_DIR, filename)
                    image_file.save(image_path)
                    item['image'] = filename
                elif image_filename:
                    item['image'] = image_filename
                save_menu_data(MENU)
                message = f'Updated menu item: {item["name"]}'
            else:
                message = 'Menu item not found.'
        elif action == 'remove_item':
            item_id = request.form.get('item_id')
            MENU[:] = [item for item in MENU if str(item['id']) != item_id]
            save_menu_data(MENU)
            message = 'Menu item removed.'
        elif action == 'change_password':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            new_username = request.form.get('new_username', '').strip()
            if current_password != ADMIN_PASSWORD:
                message = 'Current password is incorrect.'
            elif not new_password:
                message = 'Enter a new password.'
            elif new_password != confirm_password:
                message = 'New passwords do not match.'
            else:
                if new_username:
                    ADMIN_USERNAME = new_username
                    admin_data['username'] = new_username
                ADMIN_PASSWORD = new_password
                admin_data['password'] = new_password
                save_admin_data(admin_data)
                message = 'Admin credentials updated successfully.'
        elif action == 'save_bank':
            bank_name = request.form.get('bank_name', '').strip()
            account_name = request.form.get('account_name', '').strip()
            account_number = request.form.get('account_number', '').strip()
            if not bank_name or not account_name or not account_number:
                message = 'Please fill in all bank account fields.'
            else:
                admin_data['bank_name'] = bank_name
                admin_data['account_name'] = account_name
                admin_data['account_number'] = account_number
                save_admin_data(admin_data)
                BANK_DETAILS['bank_name'] = bank_name
                BANK_DETAILS['account_name'] = account_name
                BANK_DETAILS['account_number'] = account_number
                message = 'Payment account details updated successfully.'
        elif action == 'update_order_status':
            order_id = request.form.get('order_id')
            status = request.form.get('status', 'New').strip()
            if order_id:
                for order in ORDERS:
                    if str(order.get('id')) == str(order_id):
                        order['status'] = status
                        order['updated_at'] = datetime.now().replace(
                            microsecond=0).isoformat()
                        save_orders_data(ORDERS)
                        message = f'Order #{order_id} updated to {status}.'
                        break

    total_items = len(MENU)
    today_summary = summarize_orders_for_day(
        ORDERS, datetime.now().date().isoformat())
    return render_template(
        'admin.html',
        shop=SHOP_NAME,
        slogan=SLOGAN,
        total_items=total_items,
        menu=MENU,
        bank=BANK_DETAILS,
        message=message,
        admin_username=ADMIN_USERNAME,
        orders=ORDERS,
        today_summary=today_summary,
    )


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_id = int(request.form.get('item_id'))
    qty = int(request.form.get('quantity', 1))
    item = get_item(item_id)
    if item is None:
        return redirect(url_for('menu'))
    cart = session.get('cart', {})
    cart[str(item_id)] = cart.get(str(item_id), 0) + qty
    session['cart'] = cart
    return redirect(url_for('menu'))


@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    items = []
    total = 0
    for id_str, qty in cart.items():
        item = get_item(int(id_str))
        if item:
            subtotal = item['price'] * qty
            items.append({'item': item, 'qty': qty, 'subtotal': subtotal})
            total += subtotal
    return render_template('cart.html', items=items, total=round(total, 2), shop=SHOP_NAME)


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    item_id = request.form.get('item_id')
    cart = session.get('cart', {})
    if item_id in cart:
        cart.pop(item_id)
        session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('menu'))
    items = []
    total = 0
    for id_str, qty in cart.items():
        item = get_item(int(id_str))
        if item:
            subtotal = item['price'] * qty
            items.append({'item': item, 'qty': qty, 'subtotal': subtotal})
            total += subtotal

    if request.method == 'POST':
        # customer info
        customer = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address')
        }
        # payment choice
        payment_method = request.form.get('payment_method')
        payment = {}
        if payment_method == 'card':
            card_number = request.form.get('card_number') or ''
            payment = {
                'method': 'Card',
                'card_name': request.form.get('card_name'),
                'card_number': card_number[-4:] if len(card_number) >= 4 else card_number,
                'expiry': request.form.get('expiry')
            }
        else:
            payment = {
                'method': 'Bank Transfer',
                'bank_name': BANK_DETAILS['bank_name'],
                'account_name': BANK_DETAILS['account_name'],
                'account_number': BANK_DETAILS['account_number']
            }

        order_items = []
        for row in items:
            order_items.append({
                'name': row['item']['name'],
                'qty': row['qty'],
                'price': row['item']['price'],
                'subtotal': row['subtotal'],
            })

        order_id = max((order.get('id', 0) for order in ORDERS), default=0) + 1
        ORDERS.append({
            'id': order_id,
            'customer': customer,
            'payment': payment,
            'items': order_items,
            'total': round(total, 2),
            'status': 'New',
            'created_at': datetime.now().replace(microsecond=0).isoformat(),
        })
        save_orders_data(ORDERS)

        # clear cart (simulate order placement)
        session.pop('cart', None)
        return render_template('success.html', customer=customer, payment=payment, total=round(total, 2), shop=SHOP_NAME, items=order_items)
    return render_template('checkout.html', items=items, total=round(total, 2), shop=SHOP_NAME, bank=BANK_DETAILS)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=True)
