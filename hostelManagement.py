import mysql.connector
import customtkinter as ctk
from tkinter import ttk, messagebox
import pandas as pd
import tkinter.filedialog as filedialog
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image as ReportLabImage, Spacer
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
from PIL import Image as PILImage
import os

# Database Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0987654321",  # Use your MySQL password here
    database="hostel_db"
)
cursor = conn.cursor()
def update_image_path(student_id, image_path):
    query = "UPDATE students SET image_path = %s WHERE id = %s"
    cursor.execute(query, (image_path, student_id))
    conn.commit()
    messagebox.showinfo("Success", "Image path updated successfully!")


# Function to add student
def add_student():
    name = entry_name.get()
    age = entry_age.get()
    room = entry_room.get()
    fees = fees_var.get()
    image_path = entry_image_path.get()

    if not name or not age or not room:
        messagebox.showerror("Error", "All fields must be filled!")
        return

    query = "INSERT INTO students (name, age, room_number, fees_paid, image_path) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (name, int(age), room, fees, image_path))
    conn.commit()
    messagebox.showinfo("Success", "Student added!")
    view_students()
    clear_entries()

# Function to update student
def update_student():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showerror("Error", "Select a student to update")
        return

    student_id = tree.item(selected_item)["values"][0]
    name = entry_name.get()
    age = entry_age.get()
    room = entry_room.get()
    fees = fees_var.get()
    image_path = entry_image_path.get()

    query = "UPDATE students SET name=%s, age=%s, room_number=%s, fees_paid=%s, image_path=%s WHERE id=%s"
    cursor.execute(query, (name, int(age), room, fees, image_path, student_id))
    conn.commit()
    messagebox.showinfo("Success", "Student record updated!")
    view_students()
    clear_entries()

# Function to delete student
def delete_student():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showerror("Error", "Select a student to delete")
        return

    student_id = tree.item(selected_item)["values"][0]
    
    query = "DELETE FROM students WHERE id=%s"
    cursor.execute(query, (student_id,))
    conn.commit()
    messagebox.showinfo("Success", "Student record deleted!")
    view_students()

# Function to view students
def view_students():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    for student in students:
        tree.insert("", "end", values=student)

# Function to search students
def search_student(event=None):
    query = entry_search.get().lower()
    query = f"%{query}%"

    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT * FROM students WHERE name LIKE %s OR room_number LIKE %s", (query, query))
    students = cursor.fetchall()

    for student in students:
        tree.insert("", "end", values=student)

# Function to clear input fields
def clear_entries():
    entry_name.delete(0, "end")
    entry_age.delete(0, "end")
    entry_room.delete(0, "end")
    entry_image_path.delete(0, "end")

# Function to export students to Excel
def export_data():
    # Fetch data from MySQL database
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    # Create a DataFrame
    df = pd.DataFrame(students, columns=["ID", "Name", "Age", "Room No", "Fees Paid","Image Path "])

    # Open the save file dialog
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")])

    if file_path:
        # Save the file
        df.to_excel(file_path, index=False)
        print(f"Data exported successfully to {file_path}")
    else:
        print("Export canceled")

# Example of how to use this function
  # Hide the root window, only show the file dialog

# Call export_data to test
export_data()

# Function to handle student selection
def select_student(event):
    selected_item = tree.focus()
    if selected_item:
        values = tree.item(selected_item)["values"]
        entry_name.delete(0, "end")
        entry_name.insert(0, values[1])
        entry_age.delete(0, "end")
        entry_age.insert(0, values[2])
        entry_room.delete(0, "end")
        entry_room.insert(0, values[3])
        fees_var.set(values[4])
        entry_image_path.delete(0, "end")
        entry_image_path.insert(0, values[5])
        
        # Display the student's image
        if values[5]:
            display_image(values[5])

def upload_image():
    file_path = askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        entry_image_path.delete(0, "end")
        entry_image_path.insert(0, file_path)

from PIL import Image, ImageTk

# Create a new frame for the student image
  # Move the image frame to the top

def display_image(image_path):
    try:
        # Open the image
        image = Image.open(image_path)

        # Resize the image to fit in the UI
        image = image.resize((300, 300), Image.Resampling.LANCZOS)

        # Convert image to a format tkinter understands
        image = ImageTk.PhotoImage(image)

        # Check if image label exists, update it. Otherwise, create a new label
        if hasattr(display_frame, 'image_label'):
            display_frame.image_label.configure(image=image)
            display_frame.image_label.image = image  # Keep reference to avoid garbage collection
        else:
            display_frame.image_label = ctk.CTkLabel(display_frame, image=image)
            display_frame.image_label.pack()

    except Exception as e:
        messagebox.showerror("Error", f"Unable to display image: {e}")


def export_to_pdf():
    cursor.execute("SELECT id, name, age, room_number, fees_paid, image_path FROM students")
    students = cursor.fetchall()

    if not students:
        messagebox.showwarning("Warning", "No student data available to export!")
        return

    pdf_filename = ".pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
    elements = []

    # Table Header
    data = [["ID", "Name", "Age", "Room No", "Fees Paid", "Photo"]]

    for student in students:
        student_id, name, age, room, fees, image_path = student

        # Handle Image
        if os.path.exists(image_path):
            img = PILImage.open(image_path)
            img = img.resize((50, 50))  # Resize image for the PDF
            temp_image_path = "temp_image.jpg"
            img.save(temp_image_path)
            student_image = ReportLabImage(temp_image_path, width=50, height=50)
        else:
            student_image = "No Image"

        # Append student data including the image
        data.append([student_id, name, age, room, fees, student_image])

    # Create Table with Images
    table = Table(data, colWidths=[50, 100, 50, 80, 80, 60])

    # Table Styling
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black)
    ])

    table.setStyle(style)
    elements.append(Spacer(1, 12))  # Space before table
    elements.append(table)

    # Build the PDF
    doc.build(elements)

    messagebox.showinfo("Success", f"PDF file '{pdf_filename}' generated successfully!")

    # Open the PDF file
    os.system(f"start {pdf_filename}")  # Windows: "start", macOS: "open", Linux: "xdg-open"


# Main Window
root = ctk.CTk()
root.title("Hostel Management System")
root.geometry("850x600")

# Gradient background
root.configure(bg="#2f3e4e")

# Sidebar with smooth hover effects
sidebar = ctk.CTkFrame(root, width=200, height=600, fg_color="#3c4e69")
sidebar.pack(side="left", fill="y")

ctk.CTkLabel(sidebar, text="🏨 Dashboard", font=("Arial", 24, "bold"), text_color="white").pack(pady=20)

def change_button_color_on_hover(event, button):
    button.configure(fg_color="#4f6d87")

def reset_button_color(event, button):
    button.configure(fg_color="#3c4e69")

# Adding stylish buttons with hover effects
btn_manage = ctk.CTkButton(sidebar, text="View Students", fg_color="#3c4e69", command=view_students, font=("Arial", 16), width=180)
btn_manage.pack(pady=10)
btn_manage.bind("<Enter>", lambda event: change_button_color_on_hover(event, btn_manage))
btn_manage.bind("<Leave>", lambda event: reset_button_color(event, btn_manage))

btn_export = ctk.CTkButton(sidebar, text="Export Data", fg_color="#3c4e69", command=export_data, font=("Arial", 16), width=180)
btn_export.pack(pady=10)
btn_export.bind("<Enter>", lambda event: change_button_color_on_hover(event, btn_export))
btn_export.bind("<Leave>", lambda event: reset_button_color(event, btn_export))

btn_logout = ctk.CTkButton(sidebar, text="Exit", fg_color="#c12e2a", command=root.quit, font=("Arial", 16), width=180)
btn_logout.pack(pady=10)
btn_logout.bind("<Enter>", lambda event: change_button_color_on_hover(event, btn_logout))
btn_logout.bind("<Leave>", lambda event: reset_button_color(event, btn_logout))


# Top Bar
top_bar = ctk.CTkFrame(root, height=60, fg_color="gray30")
top_bar.pack(fill="x")

# Search Input
entry_search = ctk.CTkEntry(top_bar, width=300, placeholder_text="Search Students...", fg_color="gray")
entry_search.pack(side="right", padx=20, pady=10)
entry_search.bind("<KeyRelease>", search_student)

# Student Input Form
form_frame = ctk.CTkFrame(root, width=600, height=150, corner_radius=15, fg_color="black")
form_frame.pack(pady=20)

ctk.CTkLabel(form_frame, text="Name:").grid(row=0, column=0, padx=10, pady=5)
entry_name = ctk.CTkEntry(form_frame, width=200)
entry_name.grid(row=0, column=1, padx=10, pady=5)

ctk.CTkLabel(form_frame, text="Age:").grid(row=1, column=0, padx=10, pady=5)
entry_age = ctk.CTkEntry(form_frame, width=200)
entry_age.grid(row=1, column=1, padx=10, pady=5)

ctk.CTkLabel(form_frame, text="Room No:").grid(row=2, column=0, padx=10, pady=5)
entry_room = ctk.CTkEntry(form_frame, width=200)
entry_room.grid(row=2, column=1, padx=10, pady=5)

# Fees Paid Checkbox
fees_var = ctk.IntVar()
ctk.CTkLabel(form_frame, text="Fees Status:").grid(row=3, column=0, padx=10, pady=5)
fees_status_var = ctk.StringVar(value="OK")  # Default option

ctk.CTkRadioButton(form_frame, text="Paid", variable=fees_status_var, value="Paid").grid(row=3, column=1, padx=10, pady=5)
ctk.CTkRadioButton(form_frame, text="Pending", variable=fees_status_var, value="Pending").grid(row=3, column=2, padx=10, pady=5)


# Image upload input field
ctk.CTkLabel(form_frame, text="Student Image:").grid(row=4, column=0, padx=10, pady=5)
entry_image_path = ctk.CTkEntry(form_frame, width=200, fg_color="lightgray")
entry_image_path.grid(row=4, column=1, padx=10, pady=5)
btn_upload_image = ctk.CTkButton(form_frame, text="Upload Image", command=upload_image)
btn_upload_image.grid(row=4, column=2, padx=10, pady=5)

# Buttons for Add, Update, Delete
btn_frame = ctk.CTkFrame(root)
btn_frame.pack(pady=10)

btn_add = ctk.CTkButton(btn_frame, text="Add Student", command=add_student, fg_color="green", hover_color="lightgreen")
btn_add.grid(row=0, column=0, padx=10, pady=10)

btn_update = ctk.CTkButton(btn_frame, text="Update Student", command=update_student, fg_color="blue", hover_color="lightblue")
btn_update.grid(row=0, column=1, padx=10, pady=10)

btn_delete = ctk.CTkButton(btn_frame, text="Delete Student", command=delete_student, fg_color="red", hover_color="lightcoral")
btn_delete.grid(row=0, column=2, padx=10, pady=10)

btn_pdf = ctk.CTkButton(btn_frame, text="Create PDF", command=export_to_pdf, fg_color="purple")
btn_pdf.grid(row=0, column=3, padx=10, pady=10)

# Top Bar (Header)
top_bar = ctk.CTkFrame(root, height=60, fg_color="gray30")
top_bar.pack(fill="x")



# Table to view students
table_frame = ctk.CTkFrame(root)
table_frame.pack(fill="both", expand=True, padx=20, pady=10)

columns = ("ID", "Name", "Age", "Room No", "Fees Status", "Image Path")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
tree.bind("<<TreeviewSelect>>", select_student)

# Treeview Headers
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)

tree.pack(fill="both", expand=True)

view_students()

# Frame to display the image of the student
display_frame = ctk.CTkFrame(root)
display_frame.pack(side="top",padx=100, pady=10)

root.mainloop()