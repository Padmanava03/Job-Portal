import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from mysql.connector import errorcode

# Database connection configuration
config = {
    'host': 'localhost',
    'user': 'root',  # Update to your MySQL username
    'password': '123',  # Update to your MySQL password
    'database': 'job_db'  # Ensure this matches your database name
}

def connect_to_database():
    """Connecting to the MySQL database."""
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Connection Error", str(err))
        return None

def load_job_listings():
    """Loading job listings from the database."""
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT JobID, JobTitle, JobLocation, Salary FROM JobListings")
        jobs = cursor.fetchall()
        cursor.close()
        conn.close()
        return jobs
    return []

def populate_job_listings():
    """Populating the job listings in the treeview."""
    job_list.delete(*job_list.get_children())
    jobs = load_job_listings()

    for job in jobs:
        job_list.insert("", tk.END, values=job)

def apply_for_job():
    """Submiting the job application to the database."""
    job_id = job_id_entry.get()
    applicant_name = applicant_name_entry.get()
    applicant_email = applicant_email_entry.get()
    phone_number = phone_number_entry.get()
    address = address_entry.get()
    resume_file_path = resume_file_entry.get()

    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        try:
            # Inserting applicant details
            cursor.execute("""
                INSERT INTO Applicants (ApplicantName, ApplicantEmail, ApplicantPhone, ApplicantAddress)
                VALUES (%s, %s, %s, %s)
            """, (applicant_name, applicant_email, phone_number, address))
            applicant_id = cursor.lastrowid

            # Inserting resume details
            cursor.execute("""
                INSERT INTO Resumes (ApplicantID, ResumeGDriveLink)
                VALUES (%s, %s)
            """, (applicant_id, resume_file_path))
            resume_id = cursor.lastrowid

            # Inserting application details
            cursor.execute("""
                INSERT INTO Applications (JobID, ApplicantID, ResumeID, ApplicationDate, Status)
                VALUES (%s, %s, %s, CURDATE(), 'Pending')
            """, (job_id, applicant_id, resume_id))

            conn.commit()
            messagebox.showinfo("Success", "Application submitted successfully!")
            clear_application_fields()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to submit application: {err}")
        finally:
            cursor.close()
            conn.close()

def clear_application_fields():
    """Clearing all input fields in the application form."""
    job_id_entry.delete(0, tk.END)
    applicant_name_entry.delete(0, tk.END)
    applicant_email_entry.delete(0, tk.END)
    phone_number_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)
    resume_file_entry.delete(0, tk.END)

# GUI setup
app = tk.Tk()
app.title("Job Application Portal")
app.geometry("800x600")
app.configure(bg="#f0f0f0")

# Job Listings Section
job_frame = tk.Frame(app, bg="#ffffff", bd=2, relief=tk.SUNKEN)
job_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

job_list_label = tk.Label(job_frame, text="Available Job Listings", font=("Helvetica", 16), bg="#ffffff")
job_list_label.pack(pady=10)

columns = ("Job ID", "Job Title", "Location", "Salary")
job_list = ttk.Treeview(job_frame, columns=columns, show="headings", height=8)
job_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

for col in columns:
    job_list.heading(col, text=col)

scrollbar = ttk.Scrollbar(job_frame, orient="vertical", command=job_list.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
job_list.configure(yscroll=scrollbar.set)

populate_job_listings()

# Application Form Section
application_frame = tk.Frame(app, bg="#ffffff", bd=2, relief=tk.SUNKEN)
application_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

app_form_label = tk.Label(application_frame, text="Apply for a Job", font=("Helvetica", 16), bg="#ffffff")
app_form_label.pack(pady=10)

input_labels = [
    "Job ID",
    "Your Name",
    "Your Email",
    "Phone Number",
    "Address",
    "Resume G-Drive link",
]

entry_variables = []
for label_text in input_labels:
    label = tk.Label(application_frame, text=label_text, bg="#ffffff")
    label.pack(pady=5)
    entry = tk.Entry(application_frame, width=40)
    entry.pack(pady=5)
    entry_variables.append(entry)

job_id_entry, applicant_name_entry, applicant_email_entry, phone_number_entry, address_entry, resume_file_entry = entry_variables

submit_button = tk.Button(application_frame, text="Submit Application", command=apply_for_job, bg="#4CAF50", fg="white", font=("Helvetica", 12))
submit_button.pack(pady=20)

app.mainloop()
