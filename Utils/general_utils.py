import mysql.connector
from config import DB_Config
import os
import hashlib


mydb = mysql.connector.connect(
    host=DB_Config['host'],
    user=DB_Config['user'],
    password=DB_Config['password'],
    port=DB_Config['port'],
    database=DB_Config['database']
)

def check_table():
    mycursor = mydb.cursor(buffered=True)

    try:
        # Check and create user table
        mycursor.execute(f"SHOW TABLES LIKE 'user'")
        exist = mycursor.fetchone()
        if not exist:
            mycursor.execute("""
                CREATE TABLE IF NOT EXISTS user(
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    Username VARCHAR(255) NOT NULL UNIQUE,
                    Password VARCHAR(255) NOT NULL,
                    Email VARCHAR(255) NOT NULL,
                    Role ENUM('so', 'patient', 'doctor') DEFAULT 'patient'
                )
            """)

        mycursor.execute("SHOW TABLES LIKE 'file'")
        exist = mycursor.fetchone()
        if not exist:
            mycursor.execute("""
                 CREATE TABLE IF NOT EXISTS file(
                     ID INT AUTO_INCREMENT PRIMARY KEY,
                     User_ID INT,
                     Title VARCHAR(255) NOT NULL,
                     Description TEXT NOT NULL,
                     File_Name VARCHAR(255) NOT NULL,
                     File_Type VARCHAR(50) NOT NULL,
                     File_Path VARCHAR(600) NOT NULL,
                     File_Size INT NOT NULL,
                     File_Hash VARCHAR(128) NOT NULL,
                     Co_Authors INT DEFAULT NULL,
                     Uploaded_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     Deleted_At TIMESTAMP NULL DEFAULT NULL,
                     File_Classification ENUM('non-sensitive', 'sensitive', 'confidential') NOT NULL,
                     FOREIGN KEY (User_ID) REFERENCES user(ID) ON DELETE CASCADE,
                     INDEX (User_ID),
                     INDEX (Uploaded_At)
                 )
             """)

        # Check and create consent table
        mycursor.execute(f"SHOW TABLES LIKE 'consent'")
        exist = mycursor.fetchone()
        if not exist:
            mycursor.execute("""
                CREATE TABLE IF NOT EXISTS consent(
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    User_ID INT,
                    Consent_Type VARCHAR(600),
                    FOREIGN KEY (User_ID) REFERENCES user(ID) ON DELETE CASCADE
                )
            """)

        # Check and create audit log table
        mycursor.execute(f"SHOW TABLES LIKE 'audit_log'")
        exist = mycursor.fetchone()
        if not exist:
            mycursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log(
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    User_ID INT,
                    Action VARCHAR(255),
                    Threat_Level ENUM('low', 'medium', 'high', 'critical') NOT NULL,
                    Event_Time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (User_ID) REFERENCES user(ID) ON DELETE SET NULL
                )
            """)

        # Check and create link table
        mycursor.execute(f"SHOW TABLES LIKE 'link'")
        exist = mycursor.fetchone()
        if not exist:
            mycursor.execute("""
                CREATE TABLE IF NOT EXISTS link(
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    User_ID INT,
                    Expiration_Link VARCHAR(255) NOT NULL,
                    Duration TIMESTAMP NOT NULL,
                    Expired BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (User_ID) REFERENCES user(ID) ON DELETE CASCADE
                )
            """)

        # Check and create lock out table
        mycursor.execute(f"SHOW TABLES LIKE 'lock_out'")
        exist = mycursor.fetchone()
        if not exist:
            mycursor.execute("""
                CREATE TABLE IF NOT EXISTS lock_out(
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    User_ID INT,
                    Locked BOOLEAN DEFAULT FALSE,
                    Login_Attempts INT DEFAULT 0,
                    Duration DATETIME,
                    FOREIGN KEY (User_ID) REFERENCES user(ID) ON DELETE CASCADE
                )
            """)

        # Check and create temp file sharing table
        mycursor.execute(f"SHOW TABLES LIKE 'file_sharing'")
        exist = mycursor.fetchone()
        if not exist:
            mycursor.execute("""
                CREATE TABLE file_sharing (
                    Share_ID INT AUTO_INCREMENT PRIMARY KEY,
                    File_ID INT NOT NULL,  
                    Converted_File_Path VARCHAR(600) NOT NULL, 
                    Shared_By_User_ID INT NOT NULL,  
                    Shared_With_User_ID INT NOT NULL,  
                    Has_Downloaded BOOLEAN DEFAULT FALSE,  
                    Date_Shared TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (Shared_By_User_ID) REFERENCES user(ID) ON DELETE CASCADE,
                    FOREIGN KEY (Shared_With_User_ID) REFERENCES user(ID) ON DELETE CASCADE,
                    FOREIGN KEY (File_ID) REFERENCES file(ID) ON DELETE CASCADE

                )
            """)

        # Check and create soft deletion table
        mycursor.execute(f"SHOW TABLES LIKE 'soft_deletion'")
        exist = mycursor.fetchone()
        if not exist:
            mycursor.execute("""
                CREATE TABLE IF NOT EXISTS soft_deletion(
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    File_ID INT,
                    File_Path VARCHAR(255),
                    Duration TIMESTAMP,
                    FOREIGN KEY (File_ID) REFERENCES file(ID) ON DELETE CASCADE
                )
            """)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        mycursor.close()



#upload route checker
def make_dir_for_temp_upload():
    upload_folder = '../Files/Redact_&_Watermark'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    return upload_folder


ALLOWED_EXTENSIONS = {'pdf'}

# Maximum file size in bytes (5 MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def is_file_size_valid(file):
    try:
        file.seek(0, os.SEEK_END)  # Move the file pointer to the end of the file
        size = file.tell()  # Get the current position of the file pointer (file size)
        file.seek(0)  # Reset the file pointer to the start of the file
        return size <= MAX_FILE_SIZE
    except Exception as e:
        print(f"Error checking file size: {e}")
        return False

def generate_file_hash(file, algorithm='sha256'):
    try:
        # Validate the hashing algorithm
        if algorithm not in hashlib.algorithms_available:
            raise ValueError(f"Unsupported hashing algorithm: {algorithm}")

        # Initialize the hash object
        hasher = hashlib.new(algorithm)

        # If the input is a file path (str), open the file in binary mode
        if isinstance(file, str):
            with open(file, 'rb') as f:
                while chunk := f.read(8192):  # Read in chunks for efficiency
                    hasher.update(chunk)
        else:
            # For file-like objects, ensure the pointer is reset to the start
            file.seek(0)
            while chunk := file.read(8192):
                hasher.update(chunk)
            file.seek(0)  # Reset the pointer after reading

        # Return the hex digest of the hash
        return hasher.hexdigest()

    except Exception as e:
        print(f"Error generating file hash: {e}")
        raise


def temp_file_sharing_upload():
    upload_folder = "../Files/Sharing"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)

    return upload_folder