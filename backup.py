from Utils.file_integrity import *
from Utils.general_utils import *
import shutil
import os
import subprocess
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# Paths
UPLOAD_FOLDER = 'Files/Perma'
BACKUP_FOLDER = 'Backups'


os.makedirs(BACKUP_FOLDER, exist_ok=True)


def backup_files_directory():
    backup_name = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_FOLDER, f"files_backup_{backup_name}.zip")

    try:
        shutil.make_archive(backup_path.replace(".zip", ""), 'zip', UPLOAD_FOLDER)
        print(f"Files backup successful! Stored at: {backup_path}")
    except Exception as e:
        print(f"Error backing up files: {e}")


def backup_mysql_db():
    backup_name = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_FOLDER, f"{DB_Config['database']}_backup_{backup_name}.sql")
    MYSQLDUMP_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"

    try:
        dump_command = f'"{MYSQLDUMP_PATH}" -u {DB_Config["user"]} -p{DB_Config["password"]} -h {DB_Config["host"]} -P {DB_Config["port"]} {DB_Config["database"]} > "{backup_file}"'

        subprocess.run(dump_command, shell=True, check=True)
        print(f"MySQL backup successful! Stored at: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error backing up MySQL database: {e}")


def delete_old_backups(retention_days=1):
    """Deletes backup files older than the retention period."""
    try:
        current_time = datetime.now()
        for filename in os.listdir(BACKUP_FOLDER):
            file_path = os.path.join(BACKUP_FOLDER, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (current_time - file_time).days > retention_days:
                    os.remove(file_path)
                    print(f"🗑Deleted old backup: {filename}")
    except Exception as e:
        print(f"Error deleting old backups: {e}")


def perform_backup():
    delete_old_backups()
    backup_files_directory()
    backup_mysql_db()
    print("Backup process completed!")


# Schedule automatic backups every 7 days
scheduler = BackgroundScheduler()
scheduler.add_job(perform_backup, 'interval', days=7, start_date=datetime.now())
scheduler.start()

print("🟢 Backup system is running in the background.")
