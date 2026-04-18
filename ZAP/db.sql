-- Create the database
CREATE DATABASE IF NOT EXISTS zap_eats;
USE zap_eats;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(255),
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'Credit Card',
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Cart table
CREATE TABLE IF NOT EXISTS cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    quantity INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Insert some sample categories
INSERT INTO categories (name) VALUES 
('Starters'),
('Main Course'),
('Breads'),
('Desserts'),
('Beverages');

-- Insert sample products
INSERT INTO products (name, description, price, image_url, category_id) VALUES
('Butter Chicken', 'Tender chicken pieces in rich, creamy tomato sauce', 299.00, '/static/images/butter-chicken.webp', 2),
('Paneer Tikka', 'Grilled cottage cheese marinated in spiced yogurt', 249.00, '/static/images/paneer-tikka.webp', 1),
('Naan', 'Freshly baked Indian bread', 49.00, '/static/images/naan.webp', 3),
('Gulab Jamun', 'Sweet milk dumplings in sugar syrup', 89.00, '/static/images/gulab-jamun.webp', 4),
('Mango Lassi', 'Sweet yogurt drink with mango', 69.00, '/static/images/mango-lassi.webp', 5),
('Dal Makhani', 'Creamy black lentils cooked overnight', 199.00, '/static/images/dal-makhani.webp', 2),
('Samosa', 'Crispy pastry filled with spiced potatoes and peas', 49.00, '/static/images/samosa.webp', 1),
('Roti', 'Whole wheat Indian flatbread', 39.00, '/static/images/roti.webp', 3),
('Rasmalai', 'Cottage cheese dumplings in sweet milk', 89.00, '/static/images/rasmalai.webp', 4),
('Masala Chai', 'Spiced Indian tea', 49.00, '/static/images/masala-chai.webp', 5); 