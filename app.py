from flask import Flask, render_template, request, redirect, session, url_for
import os
import cv2
import numpy as np

# Inisialisasi aplikasi Flask
app = Flask(__name__)
app.secret_key = 'secret_key_for_session'  # Kunci rahasia untuk session

# Konfigurasi folder untuk menyimpan file upload
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan folder upload sudah ada, jika belum maka dibuat
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -----------------------------
# Routing halaman utama
# -----------------------------

# Halaman utama (homepage)
@app.route('/')
def home():
    return render_template('index.html')

# Halaman about
@app.route('/about')
def about():
    return render_template('about.html')

# Halaman upload (form upload gambar)
@app.route('/upload')
def upload_page():
    return render_template('upload.html')

# -----------------------------
# Routing untuk menangani upload gambar
# Setelah gambar diunggah, diarahkan ke halaman preview
# -----------------------------
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('image')  # Ambil file gambar dari form
    if file:
        filename = file.filename  # Ambil nama file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Path penyimpanan
        file.save(filepath)  # Simpan file ke folder upload

        # Simpan nama file ke session untuk dipakai di halaman lain
        session['filename'] = filename

        # Redirect ke halaman preview
        return redirect(url_for('preview'))
    
    # Jika tidak ada file, kembali ke halaman utama
    return redirect(url_for('home'))

# -----------------------------
# Halaman preview untuk menampilkan gambar asli yang diunggah
# -----------------------------
@app.route('/preview')
def preview():
    filename = session.get('filename')  # Ambil nama file dari session
    if not filename:
        return redirect(url_for('home'))  # Jika tidak ada file, kembali ke home

    file_url = url_for('static', filename='uploads/' + filename)  # Buat URL file
    return render_template('preview.html', file_url=file_url)

# -----------------------------
# Proses pengolahan gambar dan tampilkan hasilnya
# -----------------------------
@app.route('/process')
def process():
    filename = session.get('filename')  # Ambil nama file dari session
    if not filename:
        return redirect(url_for('home'))  # Jika tidak ada file, kembali ke home

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Path file gambar
    img = cv2.imread(filepath)  # Baca gambar

    if img is None:
        return "Gagal membaca gambar", 400  # Jika gagal membaca gambar, tampilkan error

    # 1. Konversi gambar ke grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_name = 'gray_' + filename  # Nama file hasil grayscale
    gray_path = os.path.join(app.config['UPLOAD_FOLDER'], gray_name)
    cv2.imwrite(gray_path, gray)  # Simpan hasil grayscale

    # 2. Terapkan median filter untuk mengurangi noise
    median = cv2.medianBlur(gray, 5)
    median_name = 'median_' + filename  # Nama file hasil median filter
    median_path = os.path.join(app.config['UPLOAD_FOLDER'], median_name)
    cv2.imwrite(median_path, median)  # Simpan hasil median filter

    # 3. Deteksi tepi menggunakan Canny edge detection
    edges = cv2.Canny(median, 100, 200)
    edge_name = 'edge_' + filename  # Nama file hasil deteksi tepi
    edge_path = os.path.join(app.config['UPLOAD_FOLDER'], edge_name)
    cv2.imwrite(edge_path, edges)  # Simpan hasil edge detection

    # Tampilkan semua hasil di output.html
    return render_template(
        'output.html',
        gray_img=url_for('static', filename='uploads/' + gray_name),
        median_img=url_for('static', filename='uploads/' + median_name),
        edge_img=url_for('static', filename='uploads/' + edge_name)
    )

# -----------------------------
# Jalankan aplikasi Flask
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
