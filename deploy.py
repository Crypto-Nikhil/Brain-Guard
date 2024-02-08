import os
import torch
import requests
from flask import Flask, request, redirect, url_for, render_template, session
from werkzeug.utils import secure_filename
from PIL import Image
from torchvision import transforms



UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__, template_folder='template')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "m4xpl0it"



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/empty_page')
def empty_page():
    filename = session.get('filename', None)
    if filename:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('index'))

@app.route('/pred_page')
def pred_page():
    pred = session.get('pred_label', 'Prediction not available')
    f_name = session.get('filename', None)
    return render_template('pred.html', pred=pred, f_name=f_name)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        f = request.files['bt_image']
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as img:
                try:
                    predicted = requests.post("http://localhost:5000/predict", files={"file": img}).json()
                    session['pred_label'] = predicted.get('class_name', 'Prediction not available')
                except Exception as e:
                    session['pred_label'] = 'Prediction error: {}'.format(str(e))
                session['filename'] = filename
            return redirect(url_for('pred_page'))
    
    return render_template('index.html')

if __name__ == "__main__":
    app.run(port=3000)
