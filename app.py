from flask import Flask, render_template, request, redirect, session, url_for
import os
import cv2
import numpy as np

app = Flask(__name__)
app.secret_key = 'secret_key_for_session'

# Konfigurasi folder upload
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan folder upload tersedia
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -----------------------------
# Routing halaman
# -----------------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

# -----------------------------
# Upload gambar → redirect ke preview
# -----------------------------
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('image')
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Simpan nama file di session
        session['filename'] = filename

        return redirect(url_for('preview'))
    return redirect(url_for('home'))

# -----------------------------
# Preview gambar asli
# -----------------------------
@app.route('/preview')
def preview():
    filename = session.get('filename')
    if not filename:
        return redirect(url_for('home'))

    file_url = url_for('static', filename='uploads/' + filename)
    return render_template('preview.html', file_url=file_url)

# -----------------------------
# Proses → tampilkan output.html
# -----------------------------
@app.route('/process')
def process():
    filename = session.get('filename')
    if not filename:
        return redirect(url_for('home'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img = cv2.imread(filepath)

    if img is None:
        return "Gagal membaca gambar", 400

    # 1. Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_name = 'gray_' + filename
    gray_path = os.path.join(app.config['UPLOAD_FOLDER'], gray_name)
    cv2.imwrite(gray_path, gray)

    # 2. Median filter
    median = cv2.medianBlur(gray, 5)
    median_name = 'median_' + filename
    median_path = os.path.join(app.config['UPLOAD_FOLDER'], median_name)
    cv2.imwrite(median_path, median)

    # 3. Canny edge detection
    edges = cv2.Canny(median, 100, 200)
    edge_name = 'edge_' + filename
    edge_path = os.path.join(app.config['UPLOAD_FOLDER'], edge_name)
    cv2.imwrite(edge_path, edges)

    return render_template(
        'output.html',
        gray_img=url_for('static', filename='uploads/' + gray_name),
        median_img=url_for('static', filename='uploads/' + median_name),
        edge_img=url_for('static', filename='uploads/' + edge_name)
    )

# -----------------------------
# Menjalankan aplikasi
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
