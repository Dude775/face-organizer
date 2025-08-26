@echo off
chcp 65001 >nul
echo ========================================
echo    מארגן תמונות לפי זיהוי פנים
echo    Face Organizer Application
echo ========================================
echo.

echo עובר לתיקייה הנכונה...
cd /d "%~dp0"
echo התיקייה הנוכחית: %CD%
echo.

echo בודק אם Python מותקן...
python --version >nul 2>&1
if errorlevel 1 (
    echo שגיאה: Python לא מותקן במחשב שלך!
    echo אנא התקן Python מ: https://www.python.org/downloads/
    echo וודא שסימנת "Add Python to PATH" בהתקנה
    pause
    exit /b 1
)

echo Python מותקן בהצלחה!
echo.

echo בודק אם הספריות הנדרשות מותקנות...
python -c "import face_recognition" >nul 2>&1
if errorlevel 1 (
    echo מתקין ספריות נדרשות...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo שגיאה בהתקנת הספריות!
        pause
        exit /b 1
    )
    echo הספריות הותקנו בהצלחה!
) else (
    echo כל הספריות כבר מותקנות!
)

echo.
echo בודק אם המודלים של זיהוי פנים מותקנים...
python -c "import face_recognition_models" >nul 2>&1
if errorlevel 1 (
    echo מתקין מודלים של זיהוי פנים...
    pip install --user face-recognition-models
    if errorlevel 1 (
        echo מנסה דרך אחרת...
        pip install git+https://github.com/ageitgey/face_recognition_models
    )
    echo המודלים הותקנו בהצלחה!
) else (
    echo המודלים כבר מותקנים!
)

echo.
echo מפעיל את האפליקציה...
python face_organizer.py

if errorlevel 1 (
    echo.
    echo שגיאה בהפעלת האפליקציה!
    pause
) else (
    echo.
    echo האפליקציה נסגרה בהצלחה!
)

pause
