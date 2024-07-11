import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import pyrebase
from dotenv import load_dotenv
from PIL import Image
import io
from flasgger import Swagger, swag_from

load_dotenv()

def change_to_mbs(bytes):
    return bytes / (1024 * 1024)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 1024 * 1024  # 1MB

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
swagger = Swagger(app)

def save_image_to_firebase(cloud_name: str, local_name: str):
    config = {
        "apiKey": os.getenv('FIREBASE_API_KEY'),
        "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
        "projectId": os.getenv('FIREBASE_PROJECT_ID'),
        "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
        "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        "appId": os.getenv('FIREBASE_APP_ID'),
        "measurementId": os.getenv('FIREBASE_MEASUREMENT_ID'),
        "serviceAccount": os.getenv('FIREBASE_SERVICE_ACCOUNT'),
        "databaseURL": os.getenv('FIREBASE_DATABASE_URL')
    }

    firebase = pyrebase.initialize_app(config)
    storage = firebase.storage()
    
    storage.child(cloud_name).put(local_name)

def allowed_filename(filename: str):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image, max_size_kb):
    img_format = image.format
    output = io.BytesIO()
    image.save(output, format=img_format)
    output.seek(0)
    size_kb = len(output.getvalue()) / 1024
    quality = 95
    width, height = image.size

    while size_kb > max_size_kb and quality > 10:
        width = int(width   * 0.95)
        height = int(height * 0.95)
        image = image.resize((width, height), Image.LANCZOS)
        output = io.BytesIO()
        image.save(output, format=img_format)
        output.seek(0)
        size_kb = len(output.getvalue()) / 1024
    
    output.seek(0)
    return Image.open(output)

@app.route("/upload", methods=["POST"])
@swag_from({
    'summary': 'Upload an image',
    'description': 'Upload an image, resize if necessary, and save to Firebase',
    'parameters': [
        {
            'name': 'img',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'The image file to upload'
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully saved image',
            'schema': {
                'type': 'object',
                'properties': {
                    'response': {
                        'type': 'string'
                    }
                }
            }
        },
        403: {
            'description': 'No file selected or invalid file type',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string'
                    }
                }
            }
        }
    }
})
def upload():
    if 'img' not in request.files:
        return jsonify({"error": "no file selected"}), 403

    file = request.files['img']
    if file.filename == '':
        return jsonify({"error": "no file sent"}), 403
    
    if allowed_filename(file.filename):
        new_name = secure_filename(file.filename)
        complete_name_with_folder = os.path.join(UPLOAD_FOLDER, new_name)
        print("new name", new_name)
        
        file.save(complete_name_with_folder)
        size_in_bytes = os.path.getsize(complete_name_with_folder)
        size_in_mbs = change_to_mbs(size_in_bytes)
        print("size of image : ", size_in_mbs, " MBS")
        
        if size_in_mbs > 1:
            print("size greater than 1 MB, resizing")
            image = Image.open(complete_name_with_folder)
            resized_image = resize_image(image, max_size_kb=1024)
            resized_image.save(complete_name_with_folder)

        print("saving on firebase")
        save_image_to_firebase(new_name, complete_name_with_folder)
        
        print("deleting local copy of image")
        os.remove(complete_name_with_folder)
        return jsonify({"response": "successfully saved image"}), 200

    return jsonify({"response": "Image type not allowed"}), 403

if __name__ == '__main__':
    app.run(debug=True)
    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
