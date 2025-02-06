from Utils.rbac_utils import roles_required
from Utils.general_utils import *
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
import requests
import os
from datetime import datetime, timedelta


delete_bp = Blueprint('delete', __name__, template_folder='templates')

@delete_bp.route('/recycle_bin', methods=['GET'])
def recycle_bin():
    try:
        mycursor = mydb.cursor(dictionary=True)

        # Fetch soft-deleted files
        mycursor.execute("SELECT * FROM soft_deletion")
        soft_deleted_files = mycursor.fetchall()

        return render_template('Features/bin.html', soft_deleted_files=soft_deleted_files)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch recycle bin files: {str(e)}"}), 500


@delete_bp.route('/soft_delete/<int:file_id>', methods=['POST'])
def soft_delete(file_id):
    try:
        mycursor = mydb.cursor(dictionary=True)

        # Check if the file exists
        mycursor.execute("SELECT ID, File_Path FROM file WHERE ID = %s", (file_id,))
        file = mycursor.fetchone()

        if not file:
            return jsonify({"error": "File not found"}), 404

        # Define the file's new path in the recycle bin folder
        recycle_bin_path = f"Files/RecycleBin/{os.path.basename(file['File_Path'])}"

        # Move the file to the recycle bin folder
        if os.path.exists(f"Files/Perma/{file['File_Path']}"):
            os.rename(f"Files/Perma/{file['File_Path']}", recycle_bin_path)

        # Move file to soft deletion table (keeping a record for recovery purposes)
        expiry_date = datetime.now() + timedelta(days=30)
        mycursor.execute(
            "INSERT INTO soft_deletion (File_ID, File_Path, Expiry_Date) VALUES (%s, %s, %s)",
            (file["ID"], recycle_bin_path, expiry_date)
        )

        # Flag the file as soft deleted
        mycursor.execute("UPDATE file SET Deleted_At = NOW() WHERE ID = %s", (file_id,))

        mydb.commit()
        return jsonify({"message": "File moved to soft deletion."})

    except Exception as e:
        mydb.rollback()
        return jsonify({"error": f"Failed to soft delete file: {str(e)}"}), 500


@delete_bp.route('/restore/<int:file_id>', methods=['POST'])
def restore_file(file_id):
    try:
        mycursor = mydb.cursor(dictionary=True)

        # Check if the file exists in soft deletion
        mycursor.execute("SELECT File_ID, File_Path FROM soft_deletion WHERE File_ID = %s", (file_id,))
        file = mycursor.fetchone()

        if not file:
            return jsonify({"error": "File not found in soft deletion"}), 404

        # Restore file to the main table
        mycursor.execute(
            "INSERT INTO file (ID, File_Path) VALUES (%s, %s)",
            (file["File_ID"], file["File_Path"])
        )

        # Remove from soft deletion table
        mycursor.execute("DELETE FROM soft_deletion WHERE File_ID = %s", (file_id,))

        # Reset Deleted_At in the main table
        mycursor.execute("UPDATE file SET Deleted_At = NULL WHERE ID = %s", (file["File_ID"],))

        mydb.commit()
        return jsonify({"message": "File restored successfully."})

    except Exception as e:
        mydb.rollback()
        return jsonify({"error": f"Failed to restore file: {str(e)}"}), 500


@delete_bp.route('/hard_delete/<int:file_id>', methods=['POST'])
def hard_delete(file_id):
    try:
        mycursor = mydb.cursor(dictionary=True)

        # Check if the file exists in soft deletion
        mycursor.execute("SELECT File_ID, File_Path FROM soft_deletion WHERE File_ID = %s", (file_id,))
        file = mycursor.fetchone()

        if not file:
            return jsonify({"error": "File not found in soft deletion"}), 404

        # Delete the file from the file system
        file_path = file['File_Path']
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete the file from the database
        mycursor.execute("DELETE FROM soft_deletion WHERE File_ID = %s", (file_id,))

        mydb.commit()
        return jsonify({"message": "File permanently deleted."})

    except Exception as e:
        mydb.rollback()
        return jsonify({"error": f"Failed to permanently delete file: {str(e)}"}), 500



