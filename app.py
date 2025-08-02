from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'piyash-secret-key'

# Dummy data
products = [
    {'id': 1, 'name': 'Gyro Watch', 'price': 999, 'image': '/static/uploads/watch.jpg', 'description': 'This is a demo product page. You can customize this to add full description, features, reviews, etc.'},
    {'id': 2, 'name': 'Smart Glasses', 'price': 499, 'image': '/static/uploads/glasses.jpg', 'description': 'Futuristic smart glasses.'}
]

admin_username = 'admin'
admin_password = '902598491p'


@app.route('/')
def index():
    return render_template('index.html', products=products)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return render_template('product_detail.html', product=product)
    return 'Product not found', 404


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == admin_username and password == admin_password:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html', products=products)


@app.route('/admin/add', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image = request.form['image']
        description = request.form['description']
        product_id = len(products) + 1
        products.append({
            'id': product_id,
            'name': name,
            'price': price,
            'image': image,
            'description': description
        })
        return redirect(url_for('admin_dashboard'))
    return render_template('add_product.html')


@app.route('/admin/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return 'Product not found', 404
    if request.method == 'POST':
        product['name'] = request.form['name']
        product['price'] = request.form['price']
        product['image'] = request.form['image']
        product['description'] = request.form['description']
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_product.html', product=product)


@app.route('/admin/delete/<int:product_id>')
def delete_product(product_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    global products
    products = [p for p in products if p['id'] != product_id]
    return redirect(url_for('admin_dashboard'))


# ✅ FINAL RENDER-COMPATIBLE LINE BELOW
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
