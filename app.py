import os
from flask import Flask, flash, request, redirect, url_for,jsonify
from werkzeug.utils import secure_filename
import pyrebase
from dotenv import load_dotenv


load_dotenv()


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def save_image_to_firebase(cloud_name:str,local_name:str):
    
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
    print(config)
    input("ahsan")
    firebase=pyrebase.initialize_app(config)
    storage=firebase.storage()
    
    

    storage.child(cloud_name).put(local_name)



def allowed_filename(filename:str):
    
    return '.' in filename and filename.split(".")[1] in ALLOWED_EXTENSIONS


@app.route("/upload",methods=["POST"])
def upload():
    if not request.files:
        return jsonify({"error":"no file selected"}),403
    print(os.listdir())

    file=request.files["img"]
    
    if file.filename=='':
        return jsonify({"error":"no file send"}),403
    if allowed_filename(file.filename):
        new_name=secure_filename(file.filename)
        complete_name_with_folder=os.path.join(UPLOAD_FOLDER,new_name)
        print("new name",new_name)
        file.save(complete_name_with_folder)
        print("firebase")
        save_image_to_firebase(new_name,complete_name_with_folder)
        print("deletion")
        os.remove(complete_name_with_folder)



    
    return jsonify({"response":"received"}),200



if __name__=='__main__':
    app.run(debug=True)