import mysql.connector
from config import DB_Config
import os
from config import ALLOWED_EXTENSIONS


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
                    Role ENUM('so', 'user') DEFAULT 'user'
                )
            """)

        # Check and create file table
        mycursor.execute(f"SHOW TABLES LIKE 'file'")
        exist = mycursor.fetchone()
        if not exist:
            mycursor.execute("""
                CREATE TABLE IF NOT EXISTS file(
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    User_ID INT,
                    File_Meta_Data VARCHAR(255),
                    File_Path VARCHAR(600),
                    Co_Authors INT,
                    File_Classification ENUM('non-sensitive', 'sensitive', 'confidential'),
                    FOREIGN KEY (User_ID) REFERENCES user(ID) ON DELETE CASCADE
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
                    FOREIGN KEY (User_ID) REFERENCES user(ID) ON DELETE CASCADE
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
        mycursor.execute(f"SHOW TABLES LIKE 'temp_file_sharing'")
        exist = mycursor.fetchone()
        if not exist:
            mycursor.execute("""
                CREATE TABLE IF NOT EXISTS temp_file_sharing(
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    File_ID INT NOT NULL,
                    Sharing_Link VARCHAR(255),
                    Duration DATETIME,
                    Privilege ENUM('read', 'edit'),
                    Expired BOOLEAN DEFAULT FALSE,
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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS