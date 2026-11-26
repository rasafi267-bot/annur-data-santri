@echo off
cd /d "%~dp0"
echo Daftar backup:
dir /b backup\*.zip
set /p FILE="Ketik nama file backup: "
if not exist "backup\%FILE%" (echo File tidak ditemukan. & pause & exit /b 1)
set /p Y="Restore akan mengganti file website. Lanjut? (Y/N): "
if /i not "%Y%"=="Y" exit /b 0
powershell -NoProfile -Command "$stamp=Get-Date -Format 'yyyy-MM-dd-HHmm'; Compress-Archive -Path app.py,templates,static,database,uploads -DestinationPath ('backup\sebelum-restore-'+$stamp+'.zip') -Force; Expand-Archive -Path ('backup\%FILE%') -DestinationPath '.' -Force"
echo Restore selesai; jalankan ulang server.
pause
