import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rahasia-negara-aman-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rst_slamet_riyadi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Berita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    konten = db.Column(db.Text, nullable=False)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    gambar = db.Column(db.String(300), nullable=True)

class Dokter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False)
    spesialis = db.Column(db.String(150), nullable=False)
    jadwal = db.Column(db.String(200), nullable=False)
    foto = db.Column(db.String(300), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/berita_acara")
def berita_acara():
    daftar_berita = Berita.query.order_by(Berita.tanggal.desc()).all()
    return render_template("berita.html", berita=daftar_berita)

@app.route("/jadwal_dokter")
def jadwal_dokter():
    daftar_dokter = Dokter.query.all()
    return render_template("jadwal.html", dokter=daftar_dokter)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Gagal. Cek username dan password.', 'danger')
    return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username sudah ada.', 'warning')
        else:
            new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Akun berhasil dibuat! Silakan login.', 'success')
            return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def init_db():
    with app.app_context():
        db.create_all()
        # Seed Data jika kosong
        if not Berita.query.first():
            b1 = Berita(judul="Penyuluhan Jantung Sehat", konten="Edukasi kesehatan jantung bagi prajurit...", gambar="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=500&q=60")
            b2 = Berita(judul="Peresmian Alat MRI Baru", konten="RST Slamet Riyadi kini dilengkapi MRI terbaru...", gambar="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=500&q=60")
            db.session.add_all([b1, b2])
            db.session.commit()
        if not Dokter.query.first():
            d1 = Dokter(nama="dr. Budi Santoso, Sp.PD", spesialis="Penyakit Dalam", jadwal="Senin - Kamis (08.00 - 14.00)", foto="https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?auto=format&fit=crop&w=300&q=80")
            d2 = Dokter(nama="dr. Sarah Wijaya, Sp.A", spesialis="Anak", jadwal="Selasa - Jumat (09.00 - 15.00)", foto="https://images.unsplash.com/photo-1594824476967-48c8b964273f?auto=format&fit=crop&w=300&q=80")
            d3 = Dokter(nama="dr. Hartono, Sp.B", spesialis="Bedah Umum", jadwal="Senin, Rabu, Jumat (10.00 - 16.00)", foto="https://images.unsplash.com/photo-1537368910025-700350fe46c7?auto=format&fit=crop&w=300&q=80")
            d4 = Dokter(nama="dr. Linda Kusuma, Sp.M", spesialis="Mata", jadwal="Selasa & Kamis (08.00 - 12.00)", foto="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=300&q=80")
            db.session.add_all([d1, d2, d3, d4])
            db.session.commit()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)