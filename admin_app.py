import tkinter as tk
from tkinter import messagebox
import mysql.connector

# MySQL configuration
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123',
    'database': 'job_db'
}

# Connect to MySQL
def connect_to_db():
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None

# 1. Application Management
def application_management():
    app_window = tk.Toplevel()
    app_window.title("Application Management")

    applicants_frame = tk.LabelFrame(app_window, text="Applicants", padx=10, pady=10)
    applicants_frame.pack(padx=20, pady=10)

    applicants_list = tk.Listbox(applicants_frame, width=50)
    applicants_list.pack(padx=10, pady=5)

    def view_applicants():
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT a.ApplicantID, a.ApplicantName, a.ApplicantEmail FROM Applicants a")
            applicants = cursor.fetchall()
            applicants_list.delete(0, tk.END)
            for applicant in applicants:
                applicants_list.insert(tk.END, f"{applicant[0]} - {applicant[1]} ({applicant[2]})")
            cursor.close()
            conn.close()

    view_applicants_button = tk.Button(applicants_frame, text="View Applicants", command=view_applicants)
    view_applicants_button.pack(pady=10)

    def select_or_reject_applicant(action):
        selected_applicant = applicants_list.get(tk.ACTIVE)
        if selected_applicant:
            applicant_id = selected_applicant.split(" - ")[0]
            conn = connect_to_db()
            if conn:
                cursor = conn.cursor()
                if action == "accept":
                    # Fetch job ID and applicant details
                    cursor.execute(f"""
                        SELECT a.JobID, ap.ApplicantName, ap.ApplicantEmail, ap.ApplicantPhone, ap.ApplicantAddress
                        FROM Applications a
                        JOIN Applicants ap ON a.ApplicantID = ap.ApplicantID
                        WHERE ap.ApplicantID = {applicant_id}
                    """)
                    result = cursor.fetchone()
                    if result:
                        job_id, applicant_name, applicant_email, applicant_phone, applicant_address = result

                        # Insert employer details into Employers table
                        cursor.execute("""
                            INSERT INTO Employers (EmployerName, EmployerEmail, EmployerPhone, EmployerAddress)
                            VALUES (%s, %s, %s, %s)
                        """, (applicant_name, applicant_email, applicant_phone, applicant_address))
                        conn.commit()

                        # Fetch the last inserted EmployerID
                        employer_id = cursor.lastrowid

                        # Insert into EmployerJob table
                        cursor.execute("""
                            INSERT INTO EmployerJob (EmployerID, JobID)
                            VALUES (%s, %s)
                        """, (employer_id, job_id))

                        # Remove from Applicants and Applications
                        cursor.execute(f"DELETE FROM Applicants WHERE ApplicantID={applicant_id}")
                        cursor.execute(f"DELETE FROM Applications WHERE ApplicantID={applicant_id}")
                        messagebox.showinfo("Success", f"Applicant {applicant_id} accepted.")

                elif action == "reject":
                    # Remove from Applicants and Applications
                    cursor.execute(f"DELETE FROM Applicants WHERE ApplicantID={applicant_id}")
                    cursor.execute(f"DELETE FROM Applications WHERE ApplicantID={applicant_id}")
                    messagebox.showinfo("Success", f"Applicant {applicant_id} rejected.")

                conn.commit()
                cursor.close()
                conn.close()
                view_applicants()

    select_button = tk.Button(applicants_frame, text="Accept Applicant", command=lambda: select_or_reject_applicant("accept"))
    select_button.pack(pady=5)

    reject_button = tk.Button(applicants_frame, text="Reject Applicant", command=lambda: select_or_reject_applicant("reject"))
    reject_button.pack(pady=5)


# 2. Employee Management
def employee_management():
    emp_window = tk.Toplevel()
    emp_window.title("Employee Management")

    employers_frame = tk.LabelFrame(emp_window, text="Employers", padx=10, pady=10)
    employers_frame.pack(padx=20, pady=10)

    employers_list = tk.Listbox(employers_frame, width=50)
    employers_list.pack(padx=10, pady=5)

    def view_employers():
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.EmployerID, e.EmployerName, ej.JobID, j.JobTitle
                FROM EmployerJob AS ej
                JOIN Employers AS e ON ej.EmployerID = e.EmployerID
                JOIN JobListings AS j ON ej.JobID = j.JobID
            """)
            employers = cursor.fetchall()
            employers_list.delete(0, tk.END)
            for employer in employers:
                employers_list.insert(tk.END, f"Employer ID: {employer[0]} - Employer: {employer[1]} - Job ID: {employer[2]} - Job Title: {employer[3]}")
            cursor.close()
            conn.close()

    view_employers_button = tk.Button(employers_frame, text="View Employers", command=view_employers)
    view_employers_button.pack(pady=10)

    def remove_employer():
        selected_employer = employers_list.get(tk.ACTIVE)
        if selected_employer:
            employer_id = selected_employer.split(" - ")[0].split(": ")[1].strip()  # Extract EmployerID
            job_id = selected_employer.split(" - ")[2].split(": ")[1].strip()      # Extract JobID

            conn = connect_to_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM EmployerJob WHERE EmployerID={employer_id} AND JobID={job_id}")
                cursor.execute(f"DELETE FROM Employers WHERE EmployerID={employer_id}")
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Success", f"Employer ID {employer_id} removed successfully.")
                view_employers()

    remove_employer_button = tk.Button(employers_frame, text="Remove Employer", command=remove_employer)
    remove_employer_button.pack(pady=5)


# 3. Job Management
def job_management():
    job_window = tk.Toplevel()
    job_window.title("Job Management")

    job_frame = tk.LabelFrame(job_window, text="Add or Update Job", padx=10, pady=10)
    job_frame.pack(padx=20, pady=10)

    tk.Label(job_frame, text="Job Title:").grid(row=0, column=0)
    job_title_entry = tk.Entry(job_frame)
    job_title_entry.grid(row=0, column=1)

    tk.Label(job_frame, text="Job Description:").grid(row=1, column=0)
    job_description_entry = tk.Entry(job_frame)
    job_description_entry.grid(row=1, column=1)

    tk.Label(job_frame, text="Job Location:").grid(row=2, column=0)
    job_location_entry = tk.Entry(job_frame)
    job_location_entry.grid(row=2, column=1)

    tk.Label(job_frame, text="Salary:").grid(row=3, column=0)
    salary_entry = tk.Entry(job_frame)
    salary_entry.grid(row=3, column=1)

    tk.Label(job_frame, text="Employment Type:").grid(row=4, column=0)
    employment_type_entry = tk.Entry(job_frame)
    employment_type_entry.grid(row=4, column=1)

    tk.Label(job_frame, text="Date Posted (YYYY-MM-DD):").grid(row=5, column=0)
    date_posted_entry = tk.Entry(job_frame)
    date_posted_entry.grid(row=5, column=1)

    def add_or_update_job():
        job_title = job_title_entry.get()
        job_description = job_description_entry.get()
        job_location = job_location_entry.get()
        salary = salary_entry.get()
        employment_type = employment_type_entry.get()
        date_posted = date_posted_entry.get()

        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO JobListings (JobTitle, JobDescription, JobLocation, Salary, EmploymentType, DatePosted) VALUES (%s, %s, %s, %s, %s, %s)",
                        (job_title, job_description, job_location, salary, employment_type, date_posted))
            messagebox.showinfo("Success", "Job listing added successfully!")
            conn.commit()
            cursor.close()
            conn.close()

    add_job_button = tk.Button(job_frame, text="Add Job", command=add_or_update_job)
    add_job_button.grid(row=6, column=1, pady=10)


# 4. Job Listings
def job_listings():
    listings_window = tk.Toplevel()
    listings_window.title("Job Listings")

    jobs_frame = tk.LabelFrame(listings_window, text="Job Listings", padx=10, pady=10)
    jobs_frame.pack(padx=20, pady=10)

    jobs_list = tk.Listbox(jobs_frame, width=50)
    jobs_list.pack(padx=10, pady=5)

    def view_jobs():
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT JobID, JobTitle FROM JobListings")
            jobs = cursor.fetchall()
            jobs_list.delete(0, tk.END)
            for job in jobs:
                jobs_list.insert(tk.END, f"{job[0]} - {job[1]}")
            cursor.close()
            conn.close()

    view_jobs_button = tk.Button(jobs_frame, text="View Job Listings", command=view_jobs)
    view_jobs_button.pack(pady=10)

def admin_dashboard():
    root = tk.Tk()
    root.title("Admin Dashboard")

    app_mgmt_button = tk.Button(root, text="Application Management", command=application_management, width=30)
    app_mgmt_button.grid(row=0, column=0, padx=20, pady=10)

    emp_mgmt_button = tk.Button(root, text="Employee Management", command=employee_management, width=30)
    emp_mgmt_button.grid(row=1, column=0, padx=20, pady=10)

    job_mgmt_button = tk.Button(root, text="Job Management", command=job_management, width=30)
    job_mgmt_button.grid(row=2, column=0, padx=20, pady=10)

    job_listings_button = tk.Button(root, text="Job Listings", command=job_listings, width=30)
    job_listings_button.grid(row=3, column=0, padx=20, pady=10)

    root.mainloop()


if __name__ == "__main__":
    admin_dashboard()
