from Utils.general_utils import make_dir_for_temp_upload, allowed_file, is_file_size_valid
from Utils.rbac_utils import roles_required
from Utils.general_utils import *
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import os
import hashlib


UPLOAD_FOLDER = 'Files/Perma'


def generate_file_hash(filepath, algorithm='sha256'):
    hasher = hashlib.new(algorithm)
    try:
        with open(filepath, 'rb') as file:
            while chunk := file.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error computing hash: {e}")
        return None

def check_file_integrity(file_id):
    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT File_Path, File_Hash FROM file WHERE ID = %s", (file_id,))
        result = cursor.fetchone()

        if not result:
            return "File not found in database."

        corrected_db_path = result['File_Path'].replace("\\", "/")
        normalized_path = os.path.normpath(corrected_db_path)
        print(f"Checking integrity for: {normalized_path}")  # Debugging

        if not os.path.exists(normalized_path):
            return "File missing from storage."

        new_hash = generate_file_hash(normalized_path)

        if new_hash == result['File_Hash']:
            return "File is intact."
        else:
            return "File has been modified or tampered with!"

    except Exception as e:
        return f"Error checking file integrity: {e}"