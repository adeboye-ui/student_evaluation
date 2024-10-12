import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from matplotlib import pyplot as plt

def create_connection():
    conn = sqlite3.connect("student_evaluation.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS evaluations (
                        id INTEGER PRIMARY KEY,
                        student_name TEXT NOT NULL,
                        attendance INTEGER,
                        classwork INTEGER,
                        socialization INTEGER,
                        neatness INTEGER,
                        evaluation_result TEXT
                      )""")
    conn.commit()
    return conn

def train_model():
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM evaluations", conn)
    conn.close()

    if df.empty:
        return None

    X = df[['attendance', 'classwork', 'socialization', 'neatness']]
    y = df['evaluation_result'].apply(lambda x: ["Needs Improvement", "Average", "Good", "Excellent"].index(x))

    model = DecisionTreeClassifier()
    model.fit(X, y)
    return model

def predict_performance(model, attendance, classwork, socialization, neatness):
    input_data = np.array([[attendance, classwork, socialization, neatness]])
    prediction = model.predict(input_data)[0]
    return ["Needs Improvement", "Average", "Good", "Excellent"][prediction]


def visualize_data():
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM evaluations", conn)
    conn.close()

    if df.empty:
        messagebox.showinfo("No Data", "No student data available to visualize.")
        return

    df['evaluation_result'].value_counts().plot(kind='bar', color='skyblue', title="Evaluation Results Distribution")
    plt.show()


def save_evaluation():
    student_name = entry_name.get()
    attendance = int(entry_attendance.get())
    classwork = int(entry_classwork.get())
    socialization = int(entry_socialization.get())
    neatness = int(entry_neatness.get())

    if not student_name:
        messagebox.showerror("Input Error", "Please enter the student's name.")
        return

    model = train_model()
    if model:
        evaluation_result = predict_performance(model, attendance, classwork, socialization, neatness)
    else:
        evaluation_result = "Needs Improvement"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO evaluations (student_name, attendance, classwork, socialization, neatness, evaluation_result) VALUES (?, ?, ?, ?, ?, ?)",
                   (student_name, attendance, classwork, socialization, neatness, evaluation_result))
    conn.commit()
    conn.close()

    messagebox.showinfo("Evaluation Result", f"Student: {student_name}\nPerformance: {evaluation_result}")
    clear_form()
    load_data()

def clear_form():
    entry_name.delete(0, tk.END)
    entry_attendance.delete(0, tk.END)
    entry_classwork.delete(0, tk.END)
    entry_socialization.delete(0, tk.END)
    entry_neatness.delete(0, tk.END)

def load_data():
    for row in table.get_children():
        table.delete(row)

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evaluations")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        table.insert("", tk.END, values=row)

def delete_record():
    selected_item = table.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a record to delete.")
        return

    item = table.item(selected_item)['values']
    record_id = item[0]

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM evaluations WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Record deleted successfully.")
    load_data()


def main_window():
    root = tk.Tk()
    root.title("Student Evaluation System")
    root.geometry("800x600")
    root.config(bg="#1e3d59")  

   
    tk.Label(root, text="Student Evaluation System", bg="#1e3d59", fg="white", 
             font=("Arial", 24, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

  
    input_bg = "#f5f5f5" 

    tk.Label(root, text="Student Name", bg="#1e3d59", fg="yellow", font=("Arial", 12)).grid(row=1, column=0, sticky="w")
    global entry_name
    entry_name = tk.Entry(root, bg=input_bg)
    entry_name.grid(row=1, column=1, pady=5)

    tk.Label(root, text="Attendance (0-100)", bg="#1e3d59", fg="yellow", font=("Arial", 12)).grid(row=2, column=0, sticky="w")
    global entry_attendance
    entry_attendance = tk.Entry(root, bg=input_bg)
    entry_attendance.grid(row=2, column=1, pady=5)

    tk.Label(root, text="Classwork (0-100)", bg="#1e3d59", fg="yellow", font=("Arial", 12)).grid(row=3, column=0, sticky="w")
    global entry_classwork
    entry_classwork = tk.Entry(root, bg=input_bg)
    entry_classwork.grid(row=3, column=1, pady=5)

    tk.Label(root, text="Socialization (0-100)", bg="#1e3d59", fg="yellow", font=("Arial", 12)).grid(row=4, column=0, sticky="w")
    global entry_socialization
    entry_socialization = tk.Entry(root, bg=input_bg)
    entry_socialization.grid(row=4, column=1, pady=5)

    tk.Label(root, text="Neatness (0-100)", bg="#1e3d59", fg="yellow", font=("Arial", 12)).grid(row=5, column=0, sticky="w")
    global entry_neatness
    entry_neatness = tk.Entry(root, bg=input_bg)
    entry_neatness.grid(row=5, column=1, pady=5)

    
    tk.Button(root, text="Evaluate & Save", bg="#4da8da", fg="white", command=save_evaluation).grid(row=6, column=0, columnspan=2, pady=10)
    tk.Button(root, text="Visualize Data", bg="#f0a500", fg="white", command=visualize_data).grid(row=7, column=0, columnspan=2, pady=5)
    tk.Button(root, text="Delete Record", bg="#fc5185", fg="white", command=delete_record).grid(row=8, column=0, columnspan=2, pady=5)

   
    global table
    columns = ("ID", "Name", "Attendance", "Classwork", "Socialization", "Neatness", "Result")
    table = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=100)

    table.grid(row=9, column=0, columnspan=2, pady=10)
    load_data()

    root.mainloop()


main_window()
