from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sandipan2005',  # Add your MySQL password here
    'database': 'zap_eats'
}

# Initialize Flask-Login
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
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['email'])
    return None

import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data['id'], user_data['username'], user_data['email'])
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                (username, email, generate_password_hash(password))
            )
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Username or email already exists')
        finally:
            cursor.close()
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
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT c.*, p.name, p.price, p.image_url 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = %s
    ''', (current_user.id,))
    cart_items = cursor.fetchall()
    cursor.close()
    conn.close()
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO cart (user_id, product_id, quantity) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + %s
        ''', (current_user.id, product_id, quantity, quantity))
        conn.commit()
        flash('Item added to cart successfully!')
    except Exception as e:
        flash('Error adding item to cart')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cart WHERE user_id = %s AND product_id = %s', 
                  (current_user.id, product_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Item removed from cart')
    return redirect(url_for('cart'))

@app.route('/checkout')
@login_required
def checkout():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get cart items
    cursor.execute('''
        SELECT c.*, p.name, p.price, p.image_url 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = %s
    ''', (current_user.id,))
    cart_items = cursor.fetchall()
    
    if not cart_items:
        flash('Your cart is empty')
        return redirect(url_for('cart'))
    
    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    cursor.close()
    conn.close()
    
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/place-order', methods=['POST'])
@login_required
def place_order():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get cart items
    cursor.execute('''
        SELECT c.*, p.name, p.price 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = %s
    ''', (current_user.id,))
    cart_items = cursor.fetchall()
    
    if not cart_items:
        flash('Your cart is empty')
        return redirect(url_for('cart'))
    
    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    # Get payment method from form
    payment_method = request.form.get('paymentMethod', 'Credit Card')
    
    # Create order
    cursor.execute('INSERT INTO orders (user_id, total_amount, payment_method) VALUES (%s, %s, %s)',
                  (current_user.id, total, payment_method))
    order_id = cursor.lastrowid
    
    # Add order items
    for item in cart_items:
        cursor.execute('''
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        ''', (order_id, item['product_id'], item['quantity'], item['price']))
    
    # Clear cart
    cursor.execute('DELETE FROM cart WHERE user_id = %s', (current_user.id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Store order_id in session for confirmation page
    session['last_order_id'] = order_id
    
    flash('Order placed successfully!')
    return redirect(url_for('order_confirmation'))

@app.route('/order-confirmation')
@login_required
def order_confirmation():
    # Get the last order ID from session
    order_id = session.get('last_order_id')
    
    if not order_id:
        flash('No order found')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get order details
    cursor.execute('SELECT * FROM orders WHERE id = %s AND user_id = %s', 
                  (order_id, current_user.id))
    order = cursor.fetchone()
    
    if not order:
        cursor.close()
        conn.close()
        flash('Order not found')
        return redirect(url_for('index'))
    
    # Get order items
    cursor.execute('''
        SELECT oi.*, p.name, p.image_url 
        FROM order_items oi 
        JOIN products p ON oi.product_id = p.id 
        WHERE oi.order_id = %s
    ''', (order_id,))
    order_items = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('order_confirmation.html', order=order, order_items=order_items)

if __name__ == '__main__':
    import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
