from app import app
from app import db
from app.validators import RegistrationValidator, AuthValidator

#!flask/bin/python
from flask import make_response
from flask import Flask, jsonify, request, render_template
from flask_bootstrap import Bootstrap
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity
)
# To load entire saved model from disk
from keras.models import load_model
import numpy as np
from keras.preprocessing import image
from keras.preprocessing.image import img_to_array, ImageDataGenerator, load_img
# from keras.applications.inception_resnet_v2 import preprocess_input
from PIL import Image
import base64
import io
from keras.applications.inception_resnet_v2 import InceptionResNetV2, preprocess_input
import cv2

from app.models import User

MODEL_DIR = '/data/dermatologist-ai/my_model.h5'

# transfer_model = InceptionResNetV2(include_top=False)

my_model = load_model(MODEL_DIR)
# my_model.load_weights(MODEL_DIR)
my_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

def path_to_tensor(img_path):
    img = image.load_img(img_path, target_size=(1022, 767))
    x = image.img_to_array(img)
    return np.expand_dims(x, axis=0)
    

def preprocess_image(image, target_size=(1022, 767)):
    if image.mode != "RGB":
        image.convert("RGB")
    image = image.resize(target_size)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    return preprocess_input(image)

@app.route('/')
@app.route('/index')
def index():
    """
        This is the home page, to be improved later to include a template
    """
    return "Welcome to Dermatology classification Web API"

@app.route('/register', methods=['POST'])
def register():
    """
        This is the registration function, all fields - username, email password1 
        and password2 are required. If registration is successful, a token is 
        sent to the user for subsequent auths
    """

    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    data_is_valid = False
    msg = ''

    username = request.json.get('username', None)
    email = request.json.get('email', None)
    password1 = request.json.get('password1', None)
    password2 = request.json.get('password2', None)

    if username and email and password1 and password2:
        data_is_valid, msg = RegistrationValidator.registration_validator(username, email, password1, password2)
        if data_is_valid:
            # call create user object
            user = User(username=username, email=email)
            user.set_password(password1)
            user.save_to_db()
            access_token = AuthValidator.authenticate(username)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"msg": msg}), 400
    else:
        return jsonify({"msg": "all fields are required"}), 400


@app.route('/login', methods=['POST'])
def login():
    """
        function to generate tokens and return to user, it accepts valid username and password
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    
    # authenticate user here
    if AuthValidator.validate_user(username, password):
        access_token = AuthValidator.authenticate(username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "User can not be authenticated"}), 404

def extract_InceptionV2(tensor):
    return InceptionResNetV2(include_top=False).predict(preprocess_input(tensor))

    
@app.route('/classify', methods=['POST'])
#@jwt_required
def classify():
    """
        It accepts Image for classification and returns the result
    """
    # Get test image ready
    print("helo classify")
    try:
        image_file = request.files['file']
        print(image_file)
        image_tensor = path_to_tensor(image_file)
        print(image_tensor.shape)
#         img = extract_InceptionV2(image_tensor)
        prediction = my_model.predict(image_tensor)
        print(prediction)
        return jsonify(prediction)
    except:
        raise
#        return "Could not make prediction"
