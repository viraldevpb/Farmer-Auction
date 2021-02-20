from __future__ import division, print_function
import tensorflow as tf
from gevent.pywsgi import WSGIServer
from werkzeug.utils import secure_filename
# Flask utils
from flask import Flask, redirect, url_for, request, render_template
# Keras
from keras.preprocessing import image
from tensorflow.keras.models import load_model
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.applications.resnet50 import ResNet50


import sys
import os
import glob
import re
import numpy as np


print(tf.__version__)

# Define a flask app
app = Flask(__name__)

# Model saved with Keras model.save()
MODEL_PATH = 'model_resnet.h5'

# Load your trained model
model = load_model(MODEL_PATH)
model._make_predict_function()   # Necessary
'''
graph = tf.get_default_graph()
with graph.as_default():
    labels = model.predict(data)
'''

# model = ResNet50(weights='imagenet')
# model.save(MODEL_PATH)
print('Model loaded. Check http://127.0.0.1:5000/')


def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(224, 224))

    # Preprocessing the image
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    x = np.expand_dims(x, axis=0)

    x = preprocess_input(x, mode='caffe')

    preds = model.predict(x)
    return preds


'''
@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')
'''


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        #f = request.files['file']
        f = request.json['data']

        print('request.json: ', f)

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        # file_path = os.path.join(basepath, 'uploads', f.filename)

        print('base_path :', basepath)

        file_path = f.filename

        print('file_path :', file_path)

        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model)

        # Process your result for human
        # pred_class = preds.argmax(axis=-1)            # Simple argmax
        pred_class = decode_predictions(preds, top=1)  # ImageNet Decode
        result = str(pred_class[0][0][1])              # Convert to string
        return result
    return None


if __name__ == '__main__':
    app.run(debug=True, threaded=False)
