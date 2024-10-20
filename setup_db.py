import mysql.connector
from mysql.connector import errorcode

# Database connection configuration
config = {
    'host': 'localhost',
    'user': 'root',  # Update to your MySQL username
    'password': '123',  # Update to your MySQL password
}

def connect_to_server():
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def create_database(cursor, db_name):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} DEFAULT CHARACTER SET 'utf8'")
        print(f"Database '{db_name}' checked/created successfully!")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def connect_to_database(db_name):
    config['database'] = db_name
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def create_tables(cursor):
    TABLES = {
        'Employers': (
            "CREATE TABLE IF NOT EXISTS Employers ("
            "  EmployerID INT PRIMARY KEY AUTO_INCREMENT,"
            "  EmployerName VARCHAR(100) NOT NULL,"
            "  EmployerEmail VARCHAR(100) NOT NULL UNIQUE,"
            "  EmployerPhone VARCHAR(15),"
            "  EmployerAddress TEXT"
            ")"
        ),
        'JobListings': (
            "CREATE TABLE IF NOT EXISTS JobListings ("
            "  JobID INT PRIMARY KEY AUTO_INCREMENT,"
            "  JobTitle VARCHAR(100) NOT NULL,"
            "  JobDescription TEXT,"
            "  JobLocation VARCHAR(100),"
            "  Salary DECIMAL(10, 2),"
            "  EmploymentType ENUM('Full-time', 'Part-time', 'Contract', 'Internship'),"
            "  DatePosted DATE"
            ")"
        ),
        'EmployerJob': (
            "CREATE TABLE IF NOT EXISTS EmployerJob ("
            "  EmployerID INT,"
            "  JobID INT,"
            "  PRIMARY KEY (EmployerID, JobID),"
            "  FOREIGN KEY (EmployerID) REFERENCES Employers(EmployerID) ON DELETE CASCADE,"
            "  FOREIGN KEY (JobID) REFERENCES JobListings(JobID) ON DELETE CASCADE"
            ")"
        ),
        'Applicants': (
            "CREATE TABLE IF NOT EXISTS Applicants ("
            "  ApplicantID INT PRIMARY KEY AUTO_INCREMENT,"
            "  ApplicantName VARCHAR(100) NOT NULL,"
            "  ApplicantEmail VARCHAR(100) NOT NULL UNIQUE,"
            "  ApplicantPhone VARCHAR(15),"
            "  ApplicantAddress TEXT"
            ")"
        ),
        'Resumes': (
            "CREATE TABLE IF NOT EXISTS Resumes ("
            "  ResumeID INT PRIMARY KEY AUTO_INCREMENT,"
            "  ApplicantID INT,"
            "  ResumeGDriveLink VARCHAR(255),"
            "  FOREIGN KEY (ApplicantID) REFERENCES Applicants(ApplicantID) ON DELETE CASCADE"
            ")"
        ),
        'Applications': (
            "CREATE TABLE IF NOT EXISTS Applications ("
            "  ApplicationID INT PRIMARY KEY AUTO_INCREMENT,"
            "  JobID INT,"
            "  ApplicantID INT,"
            "  ResumeID INT,"
            "  ApplicationDate DATE,"
            "  Status ENUM('Pending', 'Reviewed', 'Accepted', 'Rejected'),"
            "  FOREIGN KEY (JobID) REFERENCES JobListings(JobID) ON DELETE CASCADE,"
            "  FOREIGN KEY (ApplicantID) REFERENCES Applicants(ApplicantID) ON DELETE CASCADE,"
            "  FOREIGN KEY (ResumeID) REFERENCES Resumes(ResumeID) ON DELETE CASCADE"
            ")"
        ),
    }

    for table_name, ddl in TABLES.items():
        try:
            cursor.execute(ddl)
            print(f"Table '{table_name}' checked/created successfully!")
        except mysql.connector.Error as err:
            print(f"Error creating table {table_name}: {err}")

def add_sample_data(cursor):
    # Sample data for JobListings
    job_listings = [
        ("Software Engineer", "Develop software solutions.", "Bengaluru, India", 60000.00, "Full-time", "2024-01-01"),
        ("Web Developer", "Build and maintain websites.", "Delhi, India", 50000.00, "Part-time", "2024-01-02"),
        ("Data Scientist", "Analyze and interpret complex data.", "Pune, India", 70000.00, "Full-time", "2024-01-03"),
        ("UX/UI Designer", "Design user-friendly interfaces.", "Bengaluru, India", 55000.00, "Contract", "2024-01-04"),
    ]

    cursor.executemany(
        "INSERT INTO JobListings (JobTitle, JobDescription, JobLocation, Salary, EmploymentType, DatePosted) VALUES (%s, %s, %s, %s, %s, %s)",
        job_listings
    )
    print("Sample job listings added successfully!")

def setup_database():
    conn = connect_to_server()
    if conn:
        cursor = conn.cursor()
        db_name = "job_db"

        create_database(cursor, db_name)

        cursor.close()
        conn.close()

        conn = connect_to_database(db_name)
        if conn:
            cursor = conn.cursor()
            create_tables(cursor)
            add_sample_data(cursor)
            conn.commit()
            cursor.close()
            conn.close()
        else:
            print("Failed to connect to the database.")
    else:
        print("Failed to connect to MySQL server.")

if __name__ == "__main__":
    setup_database()
