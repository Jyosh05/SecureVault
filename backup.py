import shutil
import os
import subprocess
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from Utils.general_utils import *
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify


backup_bp = Blueprint('backup', __name__, template_folder='templates')

# Paths
UPLOAD_FOLDER = 'Files/Perma'
BACKUP_FOLDER = 'backups'

def backup_files_directory(source_dir, backup_dir):
    backup_name = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f"files_backup_{backup_name}.zip")
    try:
        shutil.make_archive(backup_path.replace(".zip", ""), 'zip', source_dir)
        print(f"Files backup successful! Stored at: {backup_path}")
    except Exception as e:
        print(f"Error backing up files: {e}")


def backup_mysql_db(db_config, backup_dir):
    backup_name = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f"{db_config['database']}_backup_{backup_name}.sql")
    try:
        # Create the command for the MySQL dump
        dump_command = f"mysqldump -u {db_config['user']} -p{db_config['password']} -h {db_config['host']} -P {db_config['port']} {db_config['database']} > {backup_file}"

        subprocess.run(dump_command, shell=True, check=True)
        print(f"MySQL backup successful! Stored at: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error backing up MySQL database: {e}")


def delete_old_backups(backup_dir, retention_days=7):
    try:
        current_time = datetime.now()
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (current_time - file_time).days > retention_days:
                    os.remove(file_path)  # Delete the old backup file
                    print(f"Deleted old backup: {filename}")
    except Exception as e:
        print(f"Error deleting old backups: {e}")


def perform_backup():
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
    delete_old_backups(BACKUP_FOLDER, retention_days=7)
    backup_files_directory(UPLOAD_FOLDER, BACKUP_FOLDER)
    backup_mysql_db(DB_Config, BACKUP_FOLDER)


scheduler = BackgroundScheduler()
scheduler.add_job(perform_backup, 'interval', days=7, start_date='2025-02-15 00:00:00')
scheduler.start()
try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
