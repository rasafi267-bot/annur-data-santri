import os, secrets, csv, io, zipfile, datetime
from pathlib import Path
from flask import Flask, request, redirect, url_for, render_template, session, flash, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()
BASE=Path(__file__).resolve().parent
app=Flask(__name__)
app.config.update(SECRET_KEY=os.getenv('SECRET_KEY') or secrets.token_hex(32),
 SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL') or ('sqlite:///'+str(BASE/'database'/'annur.db')), 
 SQLALCHEMY_TRACK_MODIFICATIONS=False, MAX_CONTENT_LENGTH=12*1024*1024)
db=SQLAlchemy(app); csrf=CSRFProtect(app)
class Admin(db.Model):
 id=db.Column(db.Integer,primary_key=True); username=db.Column(db.String(80),unique=True); password=db.Column(db.String(255))
class Student(db.Model):
 id=db.Column(db.Integer,primary_key=True); code=db.Column(db.String(30),unique=True); name=db.Column(db.String(150))
 nickname=db.Column(db.String(100)); gender=db.Column(db.String(20)); birth_place=db.Column(db.String(100)); birth_date=db.Column(db.String(30))
 address=db.Column(db.Text); school=db.Column(db.String(150)); program=db.Column(db.String(100)); room=db.Column(db.String(100))
 guardian=db.Column(db.String(150)); guardian_phone=db.Column(db.String(50)); status=db.Column(db.String(30),default='Aktif')
 notes=db.Column(db.Text); photo=db.Column(db.String(255))
class Registration(db.Model):
 id=db.Column(db.Integer,primary_key=True); number=db.Column(db.String(30),unique=True); name=db.Column(db.String(150)); gender=db.Column(db.String(20))
 birth_date=db.Column(db.String(30)); address=db.Column(db.Text); school=db.Column(db.String(150)); program=db.Column(db.String(100))
 guardian=db.Column(db.String(150)); phone=db.Column(db.String(50)); email=db.Column(db.String(150)); status=db.Column(db.String(50),default='Pendaftaran baru'); notes=db.Column(db.Text)
class Page(db.Model):
 id=db.Column(db.Integer,primary_key=True); slug=db.Column(db.String(80),unique=True); title=db.Column(db.String(150)); content=db.Column(db.Text)
def admin_required():
 if not session.get('admin'): abort(403)
def folders():
 for p in ['database','backup','uploads','uploads/santri','uploads/pendaftaran','uploads/berita','uploads/galeri','uploads/prestasi','uploads/pelanggaran','uploads/dokumen-santri']:
  (BASE/p).mkdir(parents=True,exist_ok=True)
def init_db():
 folders()
 with app.app_context():
  db.create_all()
  if not Admin.query.first():
   pw=os.getenv('ANNUR_ADMIN_PASSWORD')
   if not pw:
    pw=secrets.token_urlsafe(14)
    (BASE/'ADMIN-AWAL.txt').write_text(f'Login awal\\nUsername: admin\\nPassword: {pw}\\nSegera ganti password di dashboard.\\n',encoding='utf8')
   db.session.add(Admin(username='admin',password=generate_password_hash(pw)))
   db.session.commit()
init_db()
@app.route('/')
def home():
 pages=Page.query.all()
 return render_template('home.html',pages=pages)
@app.route('/page/<slug>')
def page(slug):
 p=Page.query.filter_by(slug=slug).first_or_404(); return render_template('page.html',page=p)
@app.route('/pendaftaran',methods=['GET','POST'])
def register():
 if request.method=='POST':
  name=request.form.get('name','').strip(); phone=request.form.get('phone','').strip()
  if not name or not phone: flash('Nama dan nomor WhatsApp wajib diisi.'); return redirect(url_for('register'))
  year=datetime.datetime.now().year; count=Registration.query.count()+1
  num=f'PDA-{year}-{count:04d}'
  r=Registration(number=num,name=name,gender=request.form.get('gender',''),birth_date=request.form.get('birth_date',''),address=request.form.get('address',''),school=request.form.get('school',''),program=request.form.get('program',''),guardian=request.form.get('guardian',''),phone=phone,email=request.form.get('email',''))
  db.session.add(r); db.session.commit()
  return render_template('success.html',number=num)
 return render_template('register.html')
@app.route('/cek-pendaftaran',methods=['GET','POST'])
def check_registration():
 r=None
 if request.method=='POST':
  r=Registration.query.filter_by(number=request.form.get('number','').strip(),birth_date=request.form.get('birth_date','')).first()
  if not r: flash('Data tidak ditemukan. Periksa nomor pendaftaran dan tanggal lahir.')
 return render_template('check.html',r=r)
@app.route('/data-santri',methods=['GET','POST'])
def lookup():
 s=None
 if request.method=='POST':
  code=request.form.get('code','').strip().upper()
  # Public lookup only returns non-sensitive profile data; code alone is not a secure credential.
  s=Student.query.filter_by(code=code,status='Aktif').first()
  if not s: flash('Data tidak ditemukan atau tidak aktif.')
 return render_template('lookup.html',s=s)
@app.route('/admin',methods=['GET','POST'])
def login():
 if session.get('admin'): return redirect(url_for('dashboard'))
 if request.method=='POST':
  a=Admin.query.filter_by(username=request.form.get('username')).first()
  if a and check_password_hash(a.password,request.form.get('password','')):
   session.clear(); session['admin']=a.id; return redirect(url_for('dashboard'))
  flash('Login gagal.')
 return render_template('login.html')
@app.route('/admin/dashboard')
def dashboard():
 admin_required(); return render_template('dashboard.html',students=Student.query.order_by(Student.id.desc()).all(),regs=Registration.query.order_by(Registration.id.desc()).all())
@app.route('/admin/student/save',methods=['POST'])
def save_student():
 admin_required()
 sid=request.form.get('id'); s=Student.query.get(int(sid)) if sid else None
 if not s:
  s=Student(code=f'ANNUR-{(Student.query.count()+1):04d}')
  db.session.add(s)
 s.name=request.form.get('name',''); s.nickname=request.form.get('nickname',''); s.gender=request.form.get('gender',''); s.birth_place=request.form.get('birth_place',''); s.birth_date=request.form.get('birth_date',''); s.address=request.form.get('address',''); s.school=request.form.get('school',''); s.program=request.form.get('program',''); s.room=request.form.get('room',''); s.guardian=request.form.get('guardian',''); s.guardian_phone=request.form.get('guardian_phone',''); s.status=request.form.get('status','Aktif'); s.notes=request.form.get('notes','')
 db.session.commit(); flash('Data santri disimpan.'); return redirect(url_for('dashboard'))
@app.route('/admin/student/delete/<int:sid>',methods=['POST'])
def delete_student(sid):
 admin_required(); s=Student.query.get_or_404(sid); db.session.delete(s); db.session.commit(); return redirect(url_for('dashboard'))
@app.route('/admin/registration/status/<int:rid>',methods=['POST'])
def reg_status(rid):
 admin_required(); r=Registration.query.get_or_404(rid); r.status=request.form.get('status'); r.notes=request.form.get('notes','')
 if r.status=='Menjadi santri aktif':
  if not Student.query.filter_by(name=r.name).first():
   s=Student(code=f'ANNUR-{Student.query.count()+1:04d}',name=r.name,gender=r.gender,birth_date=r.birth_date,address=r.address,school=r.school,program=r.program,guardian=r.guardian,guardian_phone=r.phone)
   db.session.add(s)
 db.session.commit(); flash('Status pendaftaran diperbarui.'); return redirect(url_for('dashboard'))
@app.route('/admin/password',methods=['POST'])
def change_password():
 admin_required()
 a=Admin.query.get(session['admin'])
 if not check_password_hash(a.password,request.form.get('old','')): flash('Password lama salah.')
 else: a.password=generate_password_hash(request.form.get('new','')); db.session.commit(); flash('Password diperbarui.')
 return redirect(url_for('dashboard'))
@app.route('/admin/export')
def export():
 admin_required(); out=io.StringIO(); w=csv.writer(out); w.writerow(['Kode','Nama','Program','Asrama','Status'])
 for s in Student.query.all(): w.writerow([s.code,s.name,s.program,s.room,s.status])
 return send_file(io.BytesIO(out.getvalue().encode('utf-8-sig')),mimetype='text/csv',download_name='data-santri.csv',as_attachment=True)
@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))
@app.route('/admin/pages',methods=['GET','POST'])
def pages():
 admin_required()
 if request.method=='POST':
  slug=request.form.get('slug','').strip(); p=Page.query.filter_by(slug=slug).first() or Page(slug=slug); p.title=request.form.get('title',''); p.content=request.form.get('content',''); db.session.add(p); db.session.commit(); flash('Halaman tersimpan.')
 return render_template('pages.html',pages=Page.query.all())
if __name__=='__main__':
 app.run(port=8000,debug=False)
