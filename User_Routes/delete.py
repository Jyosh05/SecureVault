from sympy.physics.units import minutes

from Utils.rbac_utils import roles_required
from Utils.general_utils import *
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
import requests
from Utils.rbac_utils import *
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from Utils.logging_utils import log_this


delete_bp = Blueprint('delete', __name__, template_folder='templates')

@delete_bp.route('/recycle_bin', methods=['GET'])
@roles_required('doctor')
def recycle_bin():
    try:
        mycursor = mydb.cursor(dictionary=True)
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
        mycursor.execute("SELECT ID, File_Path FROM file WHERE ID = %s", (file_id,))
        file = mycursor.fetchone()

        if not file:
            return jsonify({"error": "File not found"}), 404

        expiry_date = datetime.now() + timedelta(minutes=2)
        mycursor.execute(
            "INSERT INTO soft_deletion (File_ID, File_Path, Expiry_Date) VALUES (%s, %s, %s)",
            (file["ID"], file["File_Path"], expiry_date)  # Keep original path
        )

        mycursor.execute("UPDATE file SET Deleted_At = NOW() WHERE ID = %s", (file_id,))

        mydb.commit()
        flash("File moved to recycle bin.", 'success')  # Flash message on success
        log_this("File moved to recycle Bin", "medium")
        return redirect(url_for('view_files.view_files'))

    except Exception as e:
        mydb.rollback()
        flash(f"Failed to soft delete file: {str(e)}", 'error')  # Flash message on failure
        log_this("Failed to soft delete files", "high")
        return redirect(url_for('view_files.view_files'))


@delete_bp.route('/restore/<int:file_id>', methods=['POST'])
def restore_file(file_id):
    try:
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("""SELECT * FROM file WHERE ID = %s""", (file_id,))
        file = mycursor.fetchone()

        if not file:
            raise ValueError("File not found")

        mycursor.execute("""
            DELETE FROM soft_deletion WHERE File_ID = %s
        """, (file_id,))

        mycursor.execute("""
            UPDATE file
            SET Deleted_At = NULL
            WHERE ID = %s
        """, (file_id,))
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
        log_this("User Permanently deleted file")
        return redirect(url_for('delete.recycle_bin'))

    except Exception as e:
        mydb.rollback()
        flash(f"Failed to delete: {str(e)}", 'error')
        return redirect(url_for('delete.recycle_bin'))


def auto_delete_expired_files():
    try:
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("SELECT File_ID, File_Path, Expiry_Date FROM soft_deletion WHERE Expiry_Date <= NOW()")
        expired_files = mycursor.fetchall()

        if not expired_files:
            return

        for file in expired_files:
            file_id = file["File_ID"]
            file_path = file["File_Path"]

            if os.path.exists(file_path):
                os.remove(file_path)

            mycursor.execute("DELETE FROM soft_deletion WHERE File_ID = %s", (file_id,))
            mycursor.execute("DELETE FROM file WHERE ID = %s", (file_id,))

        mydb.commit()

    except Exception as e:
        print(f"Error in auto-deletion: {str(e)}")


scheduler = BackgroundScheduler()
scheduler.add_job(auto_delete_expired_files, 'interval', minutes=1)
scheduler.start()


