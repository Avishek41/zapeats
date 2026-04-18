from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# ---------------- DATABASE ----------------
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- LOGIN SETUP ----------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if user:
        return User(user['id'], user['username'], user['email'])
    return None

# ---------------- ROUTES ----------------

@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            login_user(User(user['id'], user['username'], user['email']))
            return redirect(url_for('index'))
        
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, password)
            )
            conn.commit()
            flash('Registration successful!')
            return redirect(url_for('login'))
        except:
            flash('Username or email already exists')
        finally:
            conn.close()
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
def cart():
    conn = get_db_connection()
    cart_items = conn.execute('''
        SELECT c.*, p.name, p.price, p.image_url 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = ?
    ''', (current_user.id,)).fetchall()
    conn.close()

    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    
    conn = get_db_connection()
    existing = conn.execute(
        'SELECT * FROM cart WHERE user_id = ? AND product_id = ?',
        (current_user.id, product_id)
    ).fetchone()

    if existing:
        conn.execute(
            'UPDATE cart SET quantity = quantity + ? WHERE user_id = ? AND product_id = ?',
            (quantity, current_user.id, product_id)
        )
    else:
        conn.execute(
            'INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)',
            (current_user.id, product_id, quantity)
        )

    conn.commit()
    conn.close()
    flash('Item added to cart!')
    return redirect(url_for('index'))

@app.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    conn = get_db_connection()
    conn.execute(
        'DELETE FROM cart WHERE user_id = ? AND product_id = ?',
        (current_user.id, product_id)
    )
    conn.commit()
    conn.close()
    flash('Item removed')
    return redirect(url_for('cart'))

@app.route('/checkout')
@login_required
def checkout():
    conn = get_db_connection()
    cart_items = conn.execute('''
        SELECT c.*, p.name, p.price, p.image_url 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = ?
    ''', (current_user.id,)).fetchall()
    conn.close()

    if not cart_items:
        flash('Cart empty')
        return redirect(url_for('cart'))

    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/place-order', methods=['POST'])
@login_required
def place_order():
    conn = get_db_connection()

    cart_items = conn.execute('''
        SELECT c.*, p.price 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = ?
    ''', (current_user.id,)).fetchall()

    if not cart_items:
        flash('Cart empty')
        return redirect(url_for('cart'))

    total = sum(item['price'] * item['quantity'] for item in cart_items)
    payment_method = request.form.get('paymentMethod')

    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO orders (user_id, total_amount, payment_method) VALUES (?, ?, ?)',
        (current_user.id, total, payment_method)
    )
    order_id = cursor.lastrowid

    for item in cart_items:
        conn.execute(
            'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
            (order_id, item['product_id'], item['quantity'], item['price'])
        )

    conn.execute('DELETE FROM cart WHERE user_id = ?', (current_user.id,))
    conn.commit()
    conn.close()

    session['last_order_id'] = order_id
    return redirect(url_for('order_confirmation'))

@app.route('/order-confirmation')
@login_required
def order_confirmation():
    order_id = session.get('last_order_id')

    if not order_id:
        return redirect(url_for('index'))

    conn = get_db_connection()
    order = conn.execute(
        'SELECT * FROM orders WHERE id = ? AND user_id = ?',
        (order_id, current_user.id)
    ).fetchone()

    order_items = conn.execute('''
        SELECT oi.*, p.name, p.image_url 
        FROM order_items oi 
        JOIN products p ON oi.product_id = p.id 
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()

    conn.close()
    return render_template('order_confirmation.html', order=order, order_items=order_items)

# ---------------- RUN ----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
