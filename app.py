from flask import Flask, render_template, request, flash, redirect, url_for
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash  # Import check_password_hash
import os
import datetime

client = MongoClient('mongodb+srv://rifqiabc9:rifqi123@cluster0.us7dlk3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.heavenheart

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(str(user_data['_id']), user_data['username'])
    return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        db.users.insert_one({'username': username, 'password': hashed_password})
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):  # Use check_password_hash here
            user_obj = User(str(user['_id']), user['username'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    produk_collection = list(db.produtcs.find().sort('_id', DESCENDING))
    return render_template('dashboard.html', produk_collection=produk_collection)

@app.route('/produks')
@login_required
def produks():
    produk_collection = list(db.produtcs.find().sort('_id', DESCENDING))
    return render_template('produks.html', produk_collection=produk_collection)

@app.route('/report')
@login_required
def report():
    report_list = [{"month": "Jan", "value": 500000}, {"month": "Feb", "value": 1500000}, {"month": "Mar", "value": 250000}]

    return render_template('report.html', report_list=report_list)

@app.template_filter()
def format_currency(value):
    return "Rp {:,}".format(int(value))

@app.route("/order")
def order_report():
    orders = db.orders.find()
    return render_template("order.html", orders=orders,)


@app.route('/produk/add', methods=['GET', 'POST'])
@login_required
def add_produk():
    if request.method == "GET":
        return render_template('add-produk.html')
    else:
        name = request.form.get('name')
        price = int(request.form.get('price'))
        description = request.form.get('description')
        image = request.files['image']
        filename = ''

        if image:
            save_to = 'static/uploads'
            if not os.path.exists(save_to):
                os.makedirs(save_to)

            ext = image.filename.split('.')[-1]
            filename = f"produk-{datetime.datetime.now().strftime('%H-%M-%S')}.{ext}"
            image.save(f"{save_to}/{filename}")

        db.produtcs.insert_one({
            'name': name, 'price': price, 'description': description, 'image': filename
        })

        flash('Successfully added a new produk.')
        return redirect(url_for('produks'))

@app.route('/produk/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_produk(id):
    if request.method == 'GET':
        produk = db.produtcs.find_one({'_id': ObjectId(id)})
        return render_template('edit-produk.html', produk=produk)

    else:
        name = request.form.get('name')
        price = int(request.form.get('price'))
        description = request.form.get('description')
        image = request.files['image']
        
        if image:
            save_to = 'static/uploads'
            produk = db.produtcs.find_one({'_id': ObjectId(id)})
            target = f"static/uploads/{produk['image']}"

            if os.path.exists(target):
                os.remove(target)
            
            ext = image.filename.split('.')[-1]
            filename = f"produk-{datetime.datetime.now().strftime('%H-%M-%S')}.{ext}"
            image.save(f"{save_to}/{filename}")

            db.produtcs.update_one({'_id': ObjectId(id)}, {'$set': {'image': filename}})
        
        db.produtcs.update_one({'_id': ObjectId(id)}, {'$set':{'name': name, 'price': price, 'description': description}})
            
        flash('Successfully updated the produk.')
        return redirect(url_for('produks'))
    
@app.route('/produk/delete/<id>', methods=['POST'])
@login_required
def delete_produk(id):
    produk = db.produtcs.find_one({'_id': ObjectId(id)})
    target = f"static/uploads/{produk['image']}"

    if os.path.exists(target):
        os.remove(target)

    db.produtcs.delete_one({'_id': ObjectId(id)})

    flash('Successfully deleted the produk.')
    return redirect(url_for('produks'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
