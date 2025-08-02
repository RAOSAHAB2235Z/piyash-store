from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the database exists
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        image TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

# Route: Home Page
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return render_template('index.html', products=products)

# Route: Product Detail Page
@app.route('/product/<int:product_id>')
def view_product(product_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = c.fetchone()
    conn.close()
    return render_template('product_detail.html', product=product)

# Route: Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect('/admin/dashboard')
        else:
            return "Invalid credentials"
    return render_template('admin_login.html')

# Route: Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/admin/login')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', products=products)

# Route: Add Product
@app.route('/admin/add', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin'):
        return redirect('/admin/login')
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']

        image_file = request.files['image']
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)

        db_path = '/' + image_path.replace('\\', '/')

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO products (name, price, image) VALUES (?, ?, ?)", (name, price, db_path))
        conn.commit()
        conn.close()
        return redirect('/admin/dashboard')
    return render_template('add_product.html')

# Route: Edit Product
@app.route('/admin/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not session.get('admin'):
        return redirect('/admin/login')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image_path = None

        if 'image' in request.files and request.files['image'].filename != '':
            image_file = request.files['image']
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            db_path = '/' + image_path.replace('\\', '/')
        else:
            c.execute("SELECT image FROM products WHERE id = ?", (product_id,))
            db_path = c.fetchone()[0]

        c.execute("UPDATE products SET name = ?, price = ?, image = ? WHERE id = ?", (name, price, db_path, product_id))
        conn.commit()
        conn.close()
        return redirect('/admin/dashboard')
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = c.fetchone()
    conn.close()
    return render_template('edit_product.html', product=product)

# Route: Delete Product
@app.route('/admin/delete/<int:product_id>')
def delete_product(product_id):
    if not session.get('admin'):
        return redirect('/admin/login')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/dashboard')

# Route: Logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
