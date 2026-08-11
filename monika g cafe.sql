CREATE DATABASE IF NOT EXISTS monika_cafe_db;
USE monika_cafe_db;

-- Drop tables in reverse order of dependencies to avoid Foreign Key violations
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS cafe_tables;
DROP TABLE IF EXISTS menu_item_ingredients;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS menu_items;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

-- ==========================================
-- 1. AUTHENTICATION & USER MANAGEMENT MODULE
-- ==========================================

CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_profile VARCHAR(15) NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    loyalty_points INT DEFAULT 0,
    failed_login_attempts INT DEFAULT 0 NULL,
    locked_until DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    salary DECIMAL(10, 2) NOT NULL,
    hire_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Active',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    date DATE NOT NULL,
    clock_in DATETIME NOT NULL,
    clock_out DATETIME NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- ==========================================
-- 2. MENU & INVENTORY MODULE
-- ==========================================

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE menu_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255) NULL,
    price DECIMAL(10, 2) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    contact_name VARCHAR(100) NULL,
    phone VARCHAR(15) NULL,
    email VARCHAR(100) NULL
);

CREATE TABLE ingredients (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    stock_level DECIMAL(10, 2) DEFAULT 0.00,
    unit VARCHAR(20) NOT NULL,
    low_stock_threshold DECIMAL(10, 2) NOT NULL,
    supplier_id INT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE SET NULL
);

CREATE TABLE menu_item_ingredients (
    item_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity_required DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (item_id, ingredient_id),
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id) ON DELETE CASCADE
);

-- ==========================================
-- 3. ORDER, TABLES, & BILLING MODULE
-- ==========================================

CREATE TABLE cafe_tables (
    table_id INT AUTO_INCREMENT PRIMARY KEY,
    table_number VARCHAR(10) NOT NULL UNIQUE,
    seating_capacity INT NOT NULL,
    status VARCHAR(20) DEFAULT 'Available'
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NULL,
    table_id INT NULL,
    order_type VARCHAR(20) NOT NULL, -- Dine-in, Takeaway, Online
    order_status VARCHAR(20) DEFAULT 'Pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (table_id) REFERENCES cafe_tables(table_id) ON DELETE SET NULL
);

CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
);

CREATE TABLE bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    subtotal DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) NOT NULL,
    discount_applied DECIMAL(10, 2) DEFAULT 0.00,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(30) NOT NULL, -- Cash, UPI, Card
    payment_status VARCHAR(20) DEFAULT 'Unpaid',
    issued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- ==========================================
-- 4. RESERVATIONS & LOGISTICS MODULE
-- ==========================================

CREATE TABLE reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    table_id INT NOT NULL,
    reservation_time DATETIME NOT NULL,
    number_of_guests INT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (table_id) REFERENCES cafe_tables(table_id) ON DELETE CASCADE
);

CREATE TABLE feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_id INT NULL,
    rating INT NOT NULL,
    comments TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL
);

-- ==============================================================================
-- 🌱 DATA SEEDING (CRITICAL SYSTEM RECORDS)
-- ==============================================================================

-- 1. Insert default access levels
INSERT INTO roles (role_id, role_name) VALUES 
(1, 'Admin'),
(2, 'Manager'),
(3, 'Staff/Cashier'),
(4, 'Customer');

-- 2. Insert core layout categories for your menu setup
INSERT INTO categories (category_id, category_name) VALUES 
(1, 'Coffee'),
(2, 'Tea'),
(3, 'Snacks'),
(4, 'Desserts'),
(5, 'Beverages');

-- 3. Pre-populate default physical tables for reservation layouts
INSERT INTO cafe_tables (table_number, seating_capacity, status) VALUES 
('T-01', 2, 'Available'),
('T-02', 2, 'Available'),
('T-03', 4, 'Available'),
('T-04', 4, 'Available'),
('T-05', 6, 'Available');

UPDATE monika_g_cafe.users 
SET role_id = 1 
WHERE email = 'pgajjalagangulaj@gmail.com';

UPDATE users SET role_id = 1 WHERE email = 'peter@gmail.com';


CREATE TABLE customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);