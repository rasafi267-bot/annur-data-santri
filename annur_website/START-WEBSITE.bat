@echo off
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (echo Jalankan INSTALL-APLIKASI.bat dahulu. & pause & exit /b 1)
start "" http://localhost:8000
echo Website Pondok Pesantren Annur Kalibaru sedang berjalan.
echo Jangan tutup jendela ini selama website digunakan.
echo Tekan Ctrl+C untuk menghentikan website.
venv\Scripts\python app.py
pause
