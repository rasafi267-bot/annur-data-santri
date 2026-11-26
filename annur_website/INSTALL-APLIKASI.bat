@echo off
cd /d "%~dp0"
echo Memeriksa Python...
python --version
if errorlevel 1 (
 echo Python belum terpasang. Unduh dari https://www.python.org/downloads/ dan centang Add Python to PATH.
 pause
 exit /b 1
)
if not exist venv python -m venv venv
call venv\Scripts\python -m pip install --upgrade pip
call venv\Scripts\pip install -r requirements.txt
if errorlevel 1 (echo Instalasi gagal. & pause & exit /b 1)
echo Instalasi selesai. Akun awal ada di ADMIN-AWAL.txt (jika dibuat).
pause
