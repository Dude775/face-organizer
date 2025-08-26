import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import os
import shutil
import face_recognition
import cv2
from PIL import Image, ImageTk
import numpy as np
import threading
import json
from pathlib import Path
import pickle
from datetime import datetime

class AdvancedFaceOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("מארגן תמונות מתקדם - Advanced Face Organizer")
        self.root.geometry("1000x700")
        
        # משתנים
        self.source_folder = ""
        self.output_folder = ""
        self.known_faces = []
        self.known_names = []
        self.face_encodings = []
        self.face_names = []
        self.database_file = "face_database.pkl"
        
        # טעינת מסד נתונים קיים אם יש
        self.load_database()
        
        # יצירת הממשק
        self.create_widgets()
        
    def create_widgets(self):
        # כותרת ראשית
        title_label = tk.Label(self.root, text="מארגן תמונות מתקדם לפי זיהוי פנים", 
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
        
        # מסגרת לניהול אנשים
        people_frame = tk.LabelFrame(self.root, text="ניהול אנשים", padx=20, pady=20)
        people_frame.pack(fill="x", padx=20, pady=10)
        
        # רשימת אנשים
        people_list_frame = tk.Frame(people_frame)
        people_list_frame.pack(fill="x", pady=5)
        
        tk.Label(people_list_frame, text="אנשים שזוהו:").pack(side="right")
        
        # רשימת אנשים עם scrollbar
        list_frame = tk.Frame(people_list_frame)
        list_frame.pack(side="right", padx=10)
        
        self.people_listbox = tk.Listbox(list_frame, height=6, width=30)
        people_scrollbar = tk.Scrollbar(list_frame, command=self.people_listbox.yview)
        self.people_listbox.configure(yscrollcommand=people_scrollbar.set)
        
        self.people_listbox.pack(side="right", fill="both", expand=True)
        people_scrollbar.pack(side="left", fill="y")
        
        # כפתורי ניהול אנשים
        people_buttons_frame = tk.Frame(people_frame)
        people_buttons_frame.pack(fill="x", pady=5)
        
        tk.Button(people_buttons_frame, text="שנה שם", 
                 command=self.rename_person).pack(side="right", padx=5)
        tk.Button(people_buttons_frame, text="מחק אדם", 
                 command=self.delete_person).pack(side="right", padx=5)
        tk.Button(people_buttons_frame, text="רענן רשימה", 
                 command=self.refresh_people_list).pack(side="right", padx=5)
        
        # כפתור התחלת הניתוח
        self.analyze_button = tk.Button(self.root, text="התחל ניתוח תמונות", 
                                       command=self.start_analysis,
                                       bg="green", fg="white", font=("Arial", 12, "bold"))
        self.analyze_button.pack(pady=20)
        
        # סרגל התקדמות
        self.progress = ttk.Progressbar(self.root, length=800, mode='determinate')
        self.progress.pack(pady=10)
        
        # תיבת טקסט ללוג
        log_frame = tk.LabelFrame(self.root, text="לוג פעילות", padx=20, pady=20)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.log_text = tk.Text(log_frame, height=12, width=90)
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
        # כפתורי ניהול לוג
        log_buttons_frame = tk.Frame(log_frame)
        log_buttons_frame.pack(pady=5)
        
        tk.Button(log_buttons_frame, text="נקה לוג", 
                 command=self.clear_log).pack(side="right", padx=5)
        tk.Button(log_buttons_frame, text="שמור לוג", 
                 command=self.save_log).pack(side="right", padx=5)
        
        # רענון רשימת אנשים
        self.refresh_people_list()
    
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
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log_message(f"הלוג נשמר ב: {filename}")
    
    def refresh_people_list(self):
        self.people_listbox.delete(0, tk.END)
        for name in self.known_names:
            self.people_listbox.insert(tk.END, name)
    
    def rename_person(self):
        selection = self.people_listbox.curselection()
        if not selection:
            messagebox.showwarning("אזהרה", "אנא בחר אדם מהרשימה")
            return
        
        old_name = self.people_listbox.get(selection[0])
        new_name = simpledialog.askstring("שנה שם", f"הכנס שם חדש עבור {old_name}:")
        
        if new_name and new_name.strip():
            new_name = new_name.strip()
            # עדכון השם ברשימה
            index = self.known_names.index(old_name)
            self.known_names[index] = new_name
            
            # עדכון שם התיקייה
            old_folder = os.path.join(self.output_folder, old_name)
            new_folder = os.path.join(self.output_folder, new_name)
            
            if os.path.exists(old_folder):
                try:
                    os.rename(old_folder, new_folder)
                    self.log_message(f"שם התיקייה שונה מ-{old_name} ל-{new_name}")
                except Exception as e:
                    self.log_message(f"שגיאה בשינוי שם התיקייה: {str(e)}")
            
            self.refresh_people_list()
            self.save_database()
            self.log_message(f"השם שונה מ-{old_name} ל-{new_name}")
    
    def delete_person(self):
        selection = self.people_listbox.curselection()
        if not selection:
            messagebox.showwarning("אזהרה", "אנא בחר אדם מהרשימה")
            return
        
        person_name = self.people_listbox.get(selection[0])
        result = messagebox.askyesno("מחיקת אדם", 
                                   f"האם אתה בטוח שברצונך למחוק את {person_name}?\n"
                                   f"זה ימחק את כל התמונות שלו!")
        
        if result:
            try:
                # מחיקת הפנים מהרשימה
                index = self.known_names.index(person_name)
                del self.known_names[index]
                del self.known_faces[index]
                
                # מחיקת התיקייה
                person_folder = os.path.join(self.output_folder, person_name)
                if os.path.exists(person_folder):
                    shutil.rmtree(person_folder)
                    self.log_message(f"תיקיית {person_name} נמחקה")
                
                self.refresh_people_list()
                self.save_database()
                self.log_message(f"{person_name} נמחק בהצלחה")
                
            except Exception as e:
                self.log_message(f"שגיאה במחיקת {person_name}: {str(e)}")
    
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
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
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
            self.save_database()
            self.refresh_people_list()
            
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
            # השוואה עם פנים מוכרות
            matches = face_recognition.compare_faces(self.known_faces, face_encoding, tolerance=0.6)
            
            if True in matches:
                # פנים מוכרות - מציאת השם
                first_match_index = matches.index(True)
                person_name = self.known_names[first_match_index]
                self.log_message(f"    - זוהו פנים של: {person_name}")
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
    
    def load_database(self):
        try:
            if os.path.exists(self.database_file):
                with open(self.database_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_faces = data.get('known_faces', [])
                    self.known_names = data.get('known_names', [])
        except Exception as e:
            print(f"שגיאה בטעינת מסד הנתונים: {str(e)}")
    
    def save_database(self):
        try:
            data = {
                'known_faces': self.known_faces,
                'known_names': self.known_names
            }
            with open(self.database_file, 'wb') as f:
                pickle.dump(data, f)
            self.log_message(f"מסד הנתונים נשמר בהצלחה")
        except Exception as e:
            self.log_message(f"שגיאה בשמירת מסד הנתונים: {str(e)}")

def main():
    root = tk.Tk()
    app = AdvancedFaceOrganizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
