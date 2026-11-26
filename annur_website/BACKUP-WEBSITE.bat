@echo off
cd /d "%~dp0"
if not exist backup mkdir backup
powershell -NoProfile -Command "$stamp=Get-Date -Format 'yyyy-MM-dd-HHmm'; Compress-Archive -Path app.py,models.py,requirements.txt,templates,static,database,uploads,.env,ADMIN-AWAL.txt -DestinationPath ('backup\backup-annur-'+$stamp+'.zip') -Force"
if errorlevel 1 echo Backup gagal. else echo Backup selesai di folder backup.
pause
