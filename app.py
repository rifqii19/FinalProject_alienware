from flask import Flask, render_template, request, flash, redirect, url_for
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
import os
import datetime

client = MongoClient('mongodb+srv://rifqiabc9:rifqi123@cluster0.us7dlk3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.heavenheart

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def dashboard():
    fruit_collection =list(db.produtcs.find().sort('_id', DESCENDING))
    return render_template('dashboard.html', fruit_collection=fruit_collection)

@app.route('/fruits')
def fruits():
    fruit_collection =list(db.produtcs.find().sort('_id', DESCENDING))
    return render_template('fruits.html', fruit_collection=fruit_collection)

@app.route('/fruit/add', methods=['GET', 'POST'])
def add_fruit():
    if request.method == "GET":
        return render_template('add-fruit.html')
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
            filename = f"fruit-{datetime.datetime.now().strftime('%H-%M-%S')}.{ext}"
            image.save(f"{save_to}/{filename}")

        db.produtcs.insert_one({
            'name': name, 'price': price, 'description': description, 'image': filename
        })

        flash('Berhasil menambahkan data produtcs')
        return redirect(url_for('fruits'))

@app.route('/fruit/edit/<id>', methods=['GET', 'POST'])
def edit_fruit(id):
    if request.method == 'GET':
        fruit = db.produtcs.find_one({'_id': ObjectId(id)})
        return render_template('edit-fruit.html', fruit=fruit)

    else:
        name = request.form.get('name')
        price = int(request.form.get('price'))
        description = request.form.get('description')
        image = request.files['image']
        
        if image:
            save_to = 'static/uploads'
            fruit = db.produtcs.find_one({'_id': ObjectId(id)})
            target = f"static/uploads/{fruit['image']}"

            if os.path.exists(target):
                os.remove(target)
            
            ext = image.filename.split('.')[-1]
            filename = f"fruit-{datetime.datetime.now().strftime('%H-%M-%S')}.{ext}"
            image.save(f"{save_to}/{filename}")

            db.produtcs.update_one({'_id': ObjectId(id)}, {'$set': {'image': filename}})
        
        db.produtcs.update_one({'_id': ObjectId(id)}, {'$set':{'name': name, 'price': price, 'description': description}})
            
        flash('Berhasil mengubah data produtcs!')
        return redirect(url_for('fruits'))
    
@app.route('/fruit/delete/<id>', methods=['POST'])
def delete_fruit(id):
    fruit = db.produtcs.find_one({'_id': ObjectId(id)})
    target = f"static/uploads/{fruit['image']}"

    if os.path.exists(target):
        os.remove(target)

    db.produtcs.delete_one({'_id': ObjectId(id)})

    flash('Berhasil menghapus data produtcs!')
    return redirect(url_for('fruits'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)