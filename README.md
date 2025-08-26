# מארגן תמונות לפי זיהוי פנים - Face Organizer

אפליקציה מתקדמת לזיהוי פנים ומיון אוטומטי של תמונות במחשב שלך!

## מה האפליקציה עושה?

- 🔍 **זיהוי פנים אוטומטי** - מזהה פנים בתמונות שלך
- 📁 **מיון חכם** - מארגן תמונות לתיקיות לפי אנשים
- 🚀 **מהיר ויעיל** - עובד על אלפי תמונות במהירות
- 💾 **שמירת מסד נתונים** - שומר את המידע על הפנים לפעם הבאה

## איך זה עובד?

1. **בחר תיקיית מקור** - התיקייה שמכילה את כל התמונות שלך
2. **בחר תיקיית פלט** - איפה תרצה שהתמונות הממוינות יישמרו
3. **לחץ "התחל ניתוח"** - האפליקציה תעבור על כל התמונות
4. **קבל תוצאות** - כל התמונות ימוינו לתיקיות לפי אנשים

## התקנה

### דרישות מקדימות:
- Python 3.8 או גרסה חדשה יותר
- Windows 10/11

### שלבי התקנה:

1. **התקן Python** (אם עוד לא התקנת):
   - הורד מ: https://www.python.org/downloads/
   - וודא שסימנת "Add Python to PATH" בהתקנה

2. **התקן את הספריות הנדרשות**:
   ```bash
   pip install -r requirements.txt
   ```

3. **הפעל את האפליקציה**:
   ```bash
   python face_organizer.py
   ```

## שימוש

### הפעלה ראשונה:
1. הפעל את האפליקציה
2. בחר תיקיית תמונות מקור (איפה התמונות שלך)
3. בחר תיקיית פלט (איפה תרצה את התוצאות)
4. לחץ "התחל ניתוח תמונות"

### מה קורה אחרי הניתוח:
- כל התמונות ימוינו לתיקיות בשמות כמו "אדם_1", "אדם_2" וכו'
- כל תיקייה תכיל תמונות של אותו אדם
- ייווצר קובץ `face_database.json` עם המידע על הפנים

## תכונות מתקדמות:

- **זיהוי מדויק** - משתמש באלגוריתמים מתקדמים לזיהוי פנים
- **עיבוד מקביל** - עובד על מספר תמונות במקביל
- **ממשק עברי** - ממשק משתמש נוח בעברית
- **לוג מפורט** - רואה בדיוק מה קורה בכל שלב
- **סרגל התקדמות** - יודע כמה זמן נשאר

## פתרון בעיות נפוצות:

### שגיאה: "face_recognition module not found"
```bash
pip install face-recognition
```

### שגיאה: "cv2 module not found"
```bash
pip install opencv-python
```

### האפליקציה איטית מדי:
- וודא שיש לך מספיק זיכרון RAM
- נסה לעבוד על פחות תמונות בבת אחת
- סגור אפליקציות אחרות בזמן העבודה

## תמיכה טכנית:

האפליקציה משתמשת בספריות הבאות:
- `face_recognition` - זיהוי פנים מתקדם
- `opencv-python` - עיבוד תמונות
- `Pillow` - טעינת תמונות
- `tkinter` - ממשק משתמש גרפי

## רישיון:

פרויקט חופשי לשימוש אישי ומסחרי.

## תמיכה:

אם יש לך שאלות או בעיות, תוכל ליצור קשר או לפתוח issue בפרויקט.

---

**הערה**: האפליקציה עובדת הכי טוב עם תמונות באיכות טובה ובתאורה טובה. תמונות מטושטשות אוות מדי עלולות לא להיות מזוהות נכון.
