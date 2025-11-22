from flask import Flask, request, send_file, render_template
from io import BytesIO
from PIL import Image
import numpy as np

app = Flask(__name__)

# ------------------ Permutation + Diffusion -----------------
def encrypt_image(img, key):
    np.random.seed(key)
    arr = np.array(img)
    shape = arr.shape
    flat = arr.flatten()
    
    # Permutation
    idx = np.arange(flat.size)
    np.random.shuffle(idx)
    flat_perm = flat[idx]
    
    # Diffusion
    flat_diff = flat_perm ^ (key % 256)
    
    return Image.fromarray(flat_diff.reshape(shape).astype(np.uint8))

def decrypt_image(img, key):
    np.random.seed(key)
    arr = np.array(img)
    shape = arr.shape
    flat = arr.flatten()
    
    # Reverse Diffusion
    flat_diff = flat ^ (key % 256)
    
    # Reverse Permutation
    idx = np.arange(flat.size)
    np.random.shuffle(idx)
    reverse_idx = np.argsort(idx)
    flat_orig = flat_diff[reverse_idx]
    
    return Image.fromarray(flat_orig.reshape(shape).astype(np.uint8))

# ------------------ Routes -----------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    key = int(request.form['key'])
    file = request.files['image']
    img = Image.open(file).convert('RGB')
    img_enc = encrypt_image(img, key)
    
    buf = BytesIO()
    img_enc.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png', as_attachment=True, download_name='encrypted.png')

@app.route('/decrypt', methods=['POST'])
def decrypt():
    key = int(request.form['key'])
    file = request.files['image']
    img = Image.open(file).convert('RGB')
    img_dec = decrypt_image(img, key)
    
    buf = BytesIO()
    img_dec.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png', as_attachment=True, download_name='decrypted.png')

if __name__ == '__main__':
    app.run(debug=True)
