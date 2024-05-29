from flask import Flask, request, jsonify, render_template, send_file, redirect
from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['bookstore']
collection = db['books']
fs = GridFS(db)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/addBooks')
def add_books():
    return render_template('addBooks.html')

@app.route('/collection')
def book_collection():
    books = list(collection.find({}, {'title': 1, '_id': 0}))  # Only fetch title field
    return render_template('collection.html', books=books)

@app.route('/addPicture')
def add_picture():
    return render_template('addPicture.html')

@app.route('/upload_picture', methods=['POST'])
def upload_picture():
    image = request.files['image']
    description = request.form.get('description')

    # Save image to MongoDB GridFS
    file_id = fs.put(image, filename=image.filename, description=description)

    return redirect('/displayPicture')

@app.route('/displayPicture')
def display_picture():
    # Fetch all image IDs from GridFS
    files = fs.find()
    image_ids = [str(file._id) for file in files]
    return render_template('displayPicture.html', image_ids=image_ids)

@app.route('/get_picture/<file_id>')
def get_picture(file_id):
    # Retrieve the file from GridFS
    try:
        file_data = fs.get(ObjectId(file_id))
        return send_file(file_data, mimetype='image/jpeg')
    except:
        return jsonify({'error': 'File not found'}), 404

@app.route('/books', methods=['GET'])
def get_books():
    books = list(collection.find())
    return jsonify(books), 200

@app.route('/books', methods=['POST'])
def add_book():
    book = request.form.to_dict()
    if not book:
        return jsonify({'error': 'No data provided'}), 400
    collection.insert_one(book)
    return jsonify({'message': 'Book added successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
