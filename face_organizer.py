import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import face_recognition
import cv2
from PIL import Image, ImageTk
import numpy as np
import threading
import json
from pathlib import Path

class FaceOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("מארגן תמונות לפי פנים - Face Organizer")
        self.root.geometry("800x600")
        
        # משתנים
        self.source_folder = ""
        self.output_folder = ""
        self.known_faces = []
        self.known_names = []
        self.face_encodings = []
        self.face_names = []
        
        # יצירת הממשק
        self.create_widgets()
        
    def create_widgets(self):
        # כותרת ראשית
        title_label = tk.Label(self.root, text="מארגן תמונות לפי זיהוי פנים", 
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=20)
        
        # מסגרת לבחירת תיקיות
        folder_frame = tk.LabelFrame(self.root, text="בחירת תיקיות", padx=20, pady=20)
        folder_frame.pack(fill="x", padx=20, pady=10)
        
        # בחירת תיקיית מקור
        source_frame = tk.Frame(folder_frame)
        source_frame.pack(fill="x", pady=5)
        
        tk.Label(source_frame, text="תיקיית תמונות מקור:").pack(side="right")
        self.source_entry = tk.Entry(source_frame, width=50)
        self.source_entry.pack(side="right", padx=10)
        tk.Button(source_frame, text="בחר תיקייה", 
                 command=self.select_source_folder).pack(side="right")
        
        # בחירת תיקיית פלט
        output_frame = tk.Frame(folder_frame)
        output_frame.pack(fill="x", pady=5)
        
        tk.Label(output_frame, text="תיקיית פלט:").pack(side="right")
        self.output_entry = tk.Entry(output_frame, width=50)
        self.output_entry.pack(side="right", padx=10)
        tk.Button(output_frame, text="בחר תיקייה", 
                 command=self.select_output_folder).pack(side="right")
        
        # כפתור התחלת הניתוח
        self.analyze_button = tk.Button(self.root, text="התחל ניתוח תמונות", 
                                       command=self.start_analysis,
                                       bg="green", fg="white", font=("Arial", 12, "bold"))
        self.analyze_button.pack(pady=20)
        
        # סרגל התקדמות
        self.progress = ttk.Progressbar(self.root, length=600, mode='determinate')
        self.progress.pack(pady=10)
        
        # תיבת טקסט ללוג
        log_frame = tk.LabelFrame(self.root, text="לוג פעילות", padx=20, pady=20)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.log_text = tk.Text(log_frame, height=15, width=80)
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
        # כפתורי ניהול לוג
        log_buttons_frame = tk.Frame(log_frame)
        log_buttons_frame.pack(pady=5)
        
        tk.Button(log_buttons_frame, text="נקה לוג", 
                 command=self.clear_log).pack(side="right", padx=5)
        tk.Button(log_buttons_frame, text="בדוק תוצאות", 
                 command=self.check_results).pack(side="right", padx=5)
        tk.Button(log_buttons_frame, text="נקה תוצאות", 
                 command=self.clear_results).pack(side="right", padx=5)
        tk.Button(log_buttons_frame, text="בדיקה ידנית", 
                 command=self.manual_review).pack(side="right", padx=5)
    
    def select_source_folder(self):
        folder = filedialog.askdirectory(title="בחר תיקיית תמונות מקור")
        if folder:
            self.source_folder = folder
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, folder)
            self.log_message(f"נבחרה תיקיית מקור: {folder}")
    
    def select_output_folder(self):
        folder = filedialog.askdirectory(title="בחר תיקיית פלט")
        if folder:
            self.output_folder = folder
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)
            self.log_message(f"נבחרה תיקיית פלט: {folder}")
    
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def check_results(self):
        if not self.output_folder:
            messagebox.showerror("שגיאה", "אנא בחר תיקיית פלט קודם")
            return
        
        try:
            import subprocess
            import platform
            
            # פתיחת תיקיית התוצאות
            if platform.system() == "Windows":
                subprocess.run(["explorer", self.output_folder])
            else:
                subprocess.run(["open", self.output_folder])
                
            self.log_message("נפתחה תיקיית התוצאות - בדוק את המיון!")
            
        except Exception as e:
            self.log_message(f"שגיאה בפתיחת תיקייה: {str(e)}")
    
    def clear_results(self):
        if not self.output_folder:
            messagebox.showerror("שגיאה", "אנא בחר תיקיית פלט קודם")
            return
        
        result = messagebox.askyesno("ניקוי תוצאות", 
                                   "האם אתה בטוח שברצונך למחוק את כל התוצאות?\n"
                                   "זה ימחק את כל התיקיות שנוצרו!")
        
        if result:
            try:
                # מחיקת כל התיקיות שנוצרו
                for item in os.listdir(self.output_folder):
                    item_path = os.path.join(self.output_folder, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        self.log_message(f"נמחקה תיקייה: {item}")
                    elif item.endswith('.json'):
                        os.remove(item_path)
                        self.log_message(f"נמחק קובץ: {item}")
                
                # איפוס הרשימות
                self.known_faces = []
                self.known_names = []
                
                self.log_message("כל התוצאות נמחקו בהצלחה!")
                self.log_message("מוכן לניתוח חדש!")
                
            except Exception as e:
                self.log_message(f"שגיאה בניקוי: {str(e)}")
    
    def manual_review(self):
        if not self.output_folder:
            messagebox.showerror("שגיאה", "אנא בחר תיקיית פלט קודם")
            return
        
        # יצירת חלון בדיקה ידנית
        self.create_manual_review_window()
    
    def create_manual_review_window(self):
        # חלון חדש לבדיקה ידנית
        review_window = tk.Toplevel(self.root)
        review_window.title("בדיקה ידנית של תיקיות")
        review_window.geometry("1000x700")
        
        # כותרת
        title_label = tk.Label(review_window, text="בדיקה ידנית של תיקיות אנשים", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # מסגרת לבחירת תיקייה
        folder_frame = tk.LabelFrame(review_window, text="בחירת תיקייה לבדיקה", padx=20, pady=20)
        folder_frame.pack(fill="x", padx=20, pady=10)
        
        # רשימת תיקיות
        folders_frame = tk.Frame(folder_frame)
        folders_frame.pack(fill="x", pady=5)
        
        tk.Label(folders_frame, text="תיקיות קיימות:").pack(side="right")
        
        # רשימת תיקיות עם scrollbar
        list_frame = tk.Frame(folders_frame)
        list_frame.pack(side="right", padx=10)
        
        self.folders_listbox = tk.Listbox(list_frame, height=8, width=30)
        folders_scrollbar = tk.Scrollbar(list_frame, command=self.folders_listbox.yview)
        self.folders_listbox.configure(yscrollcommand=folders_scrollbar.set)
        
        self.folders_listbox.pack(side="right", fill="both", expand=True)
        folders_scrollbar.pack(side="left", fill="y")
        
        # כפתור בחירת תיקייה
        tk.Button(folders_frame, text="בחר תיקייה", 
                 command=self.select_folder_for_review).pack(side="right", padx=10)
        
        # רענון רשימת תיקיות
        self.refresh_folders_list()
        
        # מסגרת לתצוגת תמונות
        images_frame = tk.LabelFrame(review_window, text="תמונות בתיקייה", padx=20, pady=20)
        images_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # כפתורי פעולה
        actions_frame = tk.Frame(images_frame)
        actions_frame.pack(fill="x", pady=10)
        
        tk.Button(actions_frame, text="הסר תמונות מסומנות", 
                 command=self.remove_selected_images).pack(side="right", padx=5)
        tk.Button(actions_frame, text="בדוק תמונה", 
                 command=self.review_image).pack(side="right", padx=5)
    
    def refresh_folders_list(self):
        self.folders_listbox.delete(0, tk.END)
        if os.path.exists(self.output_folder):
            for item in os.listdir(self.output_folder):
                item_path = os.path.join(self.output_folder, item)
                if os.path.isdir(item_path):
                    # ספירת תמונות בתיקייה
                    image_count = len([f for f in os.listdir(item_path) 
                                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))])
                    self.folders_listbox.insert(tk.END, f"{item} ({image_count} תמונות)")
    
    def select_folder_for_review(self):
        selection = self.folders_listbox.curselection()
        if not selection:
            messagebox.showwarning("אזהרה", "אנא בחר תיקייה מהרשימה")
            return
        
        folder_name = self.folders_listbox.get(selection[0]).split(" (")[0]
        self.show_folder_images(folder_name)
    
    def show_folder_images(self, folder_name):
        folder_path = os.path.join(self.output_folder, folder_name)
        if not os.path.exists(folder_path):
            return
        
        # מציאת תמונות בתיקייה
        image_files = [f for f in os.listdir(folder_path) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
        
        if not image_files:
            messagebox.showinfo("מידע", f"לא נמצאו תמונות בתיקייה {folder_name}")
            return
        
        # הצגת תמונות (פשוט - רשימת שמות)
        images_text = f"תמונות בתיקייה {folder_name}:\n\n"
        for i, img in enumerate(image_files, 1):
            images_text += f"{i}. {img}\n"
        
        # חלון תצוגה
        img_window = tk.Toplevel(self.root)
        img_window.title(f"תמונות ב-{folder_name}")
        img_window.geometry("600x400")
        
        text_widget = tk.Text(img_window, wrap=tk.WORD)
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert(tk.END, images_text)
    
    def remove_selected_images(self):
        # פונקציה להסרת תמונות (לעתיד)
        messagebox.showinfo("מידע", "פונקציה זו תתווסף בגרסה הבאה")
    
    def review_image(self):
        # פונקציה לבדיקת תמונה (לעתיד)
        messagebox.showinfo("מידע", "פונקציה זו תתווסף בגרסה הבאה")
    
    def start_analysis(self):
        if not self.source_folder or not self.output_folder:
            messagebox.showerror("שגיאה", "אנא בחר תיקיית מקור ותיקיית פלט")
            return
        
        # התחלת הניתוח בחוט נפרד
        self.analyze_button.config(state="disabled", text="מעבד...")
        thread = threading.Thread(target=self.analyze_images)
        thread.daemon = True
        thread.start()
    
    def analyze_images(self):
        try:
            self.log_message("מתחיל ניתוח תמונות...")
            
            # קבלת רשימת קבצי תמונה
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
            image_files = []
            
            for root, dirs, files in os.walk(self.source_folder):
                for file in files:
                    if Path(file).suffix.lower() in image_extensions:
                        image_files.append(os.path.join(root, file))
            
            if not image_files:
                self.log_message("לא נמצאו קבצי תמונה בתיקייה")
                return
            
            self.log_message(f"נמצאו {len(image_files)} קבצי תמונה")
            
            # הגדרת סרגל התקדמות
            self.progress['maximum'] = len(image_files)
            self.progress['value'] = 0
            
            # ניתוח כל תמונה
            for i, image_path in enumerate(image_files):
                self.log_message(f"מעבד: {os.path.basename(image_path)}")
                self.process_image(image_path)
                self.progress['value'] = i + 1
                self.root.update()
            
            self.log_message("הניתוח הושלם בהצלחה!")
            self.save_face_database()
            
        except Exception as e:
            self.log_message(f"שגיאה: {str(e)}")
        finally:
            self.analyze_button.config(state="normal", text="התחל ניתוח תמונות")
    
    def process_image(self, image_path):
        try:
            # טעינת התמונה
            image = face_recognition.load_image_file(image_path)
            
            # זיהוי פנים
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if not face_encodings:
                self.log_message(f"  - לא זוהו פנים בתמונה")
                return
            
            self.log_message(f"  - זוהו {len(face_encodings)} פנים")
            
            # עיבוד כל פנים שזוהו
            for face_encoding in face_encodings:
                self.process_face(face_encoding, image_path)
                
        except Exception as e:
            self.log_message(f"  - שגיאה בעיבוד התמונה: {str(e)}")
    
    def process_face(self, face_encoding, image_path):
        # בדיקה אם הפנים כבר מוכרות
        if len(self.known_faces) == 0:
            # פנים ראשונות - יצירת קבוצה חדשה
            person_name = f"אדם_1"
            self.known_faces.append(face_encoding)
            self.known_names.append(person_name)
            self.log_message(f"    - נוצרה קבוצה חדשה: {person_name}")
        else:
            # ניסיון עם tolerance נמוך (דיוק גבוה)
            matches = face_recognition.compare_faces(self.known_faces, face_encoding, tolerance=0.45)
            
            if True in matches:
                # פנים מוכרות - מציאת השם
                first_match_index = matches.index(True)
                person_name = self.known_names[first_match_index]
                self.log_message(f"    - זוהו פנים של: {person_name} (tolerance=0.45)")
            else:
                # ניסיון עם tolerance בינוני
                matches = face_recognition.compare_faces(self.known_faces, face_encoding, tolerance=0.55)
                
                if True in matches:
                    first_match_index = matches.index(True)
                    person_name = self.known_names[first_match_index]
                    self.log_message(f"    - זוהו פנים של: {person_name} (tolerance=0.55)")
                else:
                    # פנים חדשות - יצירת קבוצה חדשה
                    person_name = f"אדם_{len(self.known_faces) + 1}"
                    self.known_faces.append(face_encoding)
                    self.known_names.append(person_name)
                    self.log_message(f"    - נוצרה קבוצה חדשה: {person_name}")
        
        # העתקת התמונה לתיקייה המתאימה
        self.copy_image_to_person_folder(image_path, person_name)
    
    def copy_image_to_person_folder(self, image_path, person_name):
        # יצירת תיקיית האדם אם לא קיימת
        person_folder = os.path.join(self.output_folder, person_name)
        os.makedirs(person_folder, exist_ok=True)
        
        # העתקת התמונה
        filename = os.path.basename(image_path)
        destination = os.path.join(person_folder, filename)
        
        # הוספת מספר אם הקובץ כבר קיים
        counter = 1
        while os.path.exists(destination):
            name, ext = os.path.splitext(filename)
            destination = os.path.join(person_folder, f"{name}_{counter}{ext}")
            counter += 1
        
        shutil.copy2(image_path, destination)
        self.log_message(f"    - הועתק ל: {person_name}/{os.path.basename(destination)}")
    
    def save_face_database(self):
        # שמירת מסד הנתונים של הפנים
        database = {
            'known_faces': [face.tolist() for face in self.known_faces],
            'known_names': self.known_names
        }
        
        database_path = os.path.join(self.output_folder, 'face_database.json')
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        
        self.log_message(f"מסד הנתונים נשמר ב: {database_path}")

def main():
    root = tk.Tk()
    app = FaceOrganizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
