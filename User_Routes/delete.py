from Utils.rbac_utils import roles_required
from Utils.general_utils import *
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
import requests
from Utils.rbac_utils import *
import os
from datetime import datetime, timedelta


delete_bp = Blueprint('delete', __name__, template_folder='templates')

@delete_bp.route('/recycle_bin', methods=['GET'])
@roles_required('doctor')
def recycle_bin():
    try:
        mycursor = mydb.cursor(dictionary=True)

        # Fetch soft-deleted files with title from the 'file' table
        mycursor.execute("""
            SELECT sd.File_ID, sd.File_Path, f.Title
            FROM soft_deletion sd
            JOIN file f ON sd.File_ID = f.ID
        """)
        soft_deleted_files = mycursor.fetchall()

        return render_template('Features/bin.html', soft_deleted_files=soft_deleted_files)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch recycle bin files: {str(e)}"}), 500


@delete_bp.route('/soft_delete/<int:file_id>', methods=['POST', 'GET'])
def soft_delete(file_id):
    try:
        mycursor = mydb.cursor(dictionary=True)

        # Check if the file exists
        mycursor.execute("SELECT ID, File_Path FROM file WHERE ID = %s", (file_id,))
        file = mycursor.fetchone()

        if not file:
            return jsonify({"error": "File not found"}), 404

        # Move file to soft deletion table (keeping a record for recovery purposes)
        expiry_date = datetime.now() + timedelta(days=30)
        mycursor.execute(
            "INSERT INTO soft_deletion (File_ID, File_Path, Expiry_Date) VALUES (%s, %s, %s)",
            (file["ID"], file["File_Path"], expiry_date)  # Keep original path
        )

        # Flag the file as soft deleted
        mycursor.execute("UPDATE file SET Deleted_At = NOW() WHERE ID = %s", (file_id,))

        mydb.commit()
        flash("File moved to recycle bin.", 'success')  # Flash message on success
        return redirect(url_for('view_files.view_files'))

    except Exception as e:
        mydb.rollback()
        flash(f"Failed to soft delete file: {str(e)}", 'error')  # Flash message on failure
        return redirect(url_for('view_files.view_files'))


@delete_bp.route('/restore/<int:file_id>', methods=['POST'])
def restore_file(file_id):
    try:
        # Fetch the file details from the 'file' table
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("""SELECT * FROM file WHERE ID = %s""", (file_id,))
        file = mycursor.fetchone()

        if not file:
            raise ValueError("File not found")

        # Step 1: Delete the file entry from the 'soft_deletion' table
        mycursor.execute("""
            DELETE FROM soft_deletion WHERE File_ID = %s
        """, (file_id,))

        # Step 2: Set the 'Deleted_At' field in the 'file' table to NULL (restore the file)
        mycursor.execute("""
            UPDATE file
            SET Deleted_At = NULL
            WHERE ID = %s
        """, (file_id,))

        # Commit the transaction to make changes permanent
        mydb.commit()

        flash("File restored successfully", 'success')
    except Exception as e:
        mydb.rollback()  # Ensure no partial changes if error occurs
        flash(f"Error: {str(e)}", 'error')

    return redirect(url_for('view_files.view_files'))



@delete_bp.route('/hard_delete/<int:file_id>', methods=['POST'])
def hard_delete(file_id):
    try:
        mycursor = mydb.cursor(dictionary=True)

        # Check if the file exists in soft deletion
        mycursor.execute("SELECT File_ID, File_Path FROM soft_deletion WHERE File_ID = %s", (file_id,))
        file = mycursor.fetchone()

        if not file:
            return jsonify({"error": "File not found in soft deletion"}), 404

        file_path = file["File_Path"]
        if os.path.exists(file_path):
            os.remove(file_path)

        mycursor.execute("DELETE FROM soft_deletion WHERE File_ID = %s", (file_id,))
        mycursor.execute("DELETE FROM file WHERE ID = %s", (file_id,))

        mydb.commit()

        flash("File Permanently Deleted.", 'success')  # Flash message on success
        return redirect(url_for('delete.recycle_bin'))

    except Exception as e:
        mydb.rollback()
        flash(f"Failed to delete: {str(e)}", 'error')
        return redirect(url_for('delete.recycle_bin'))



