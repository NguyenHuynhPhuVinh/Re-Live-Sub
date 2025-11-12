@echo off
echo ========================================
echo AUTO VIDEO PROCESSING SYSTEM
echo ========================================
echo.
echo Script nay se mo 2 cua so:
echo 1. Auto Processing Pipeline (tu dong xu ly video)
echo 2. Stream Recorder (ghi stream)
echo.
echo Nhan phim bat ky de tiep tuc...
pause > nul

echo.
echo Dang khoi dong Auto Processing Pipeline...
start "Auto Processing Pipeline" cmd /k python auto_process_pipeline.py

timeout /t 3 > nul

echo Dang khoi dong Stream Recorder...
start "Stream Recorder" cmd /k python stream_recorder.py

echo.
echo ========================================
echo DA KHOI DONG THANH CONG!
echo ========================================
echo.
echo 2 cua so da duoc mo:
echo - Auto Processing Pipeline: Tu dong xu ly video
echo - Stream Recorder: Ghi stream YouTube
echo.
echo Dong cua so nay de tat ca 2 cua so kia van chay.
echo.
pause
