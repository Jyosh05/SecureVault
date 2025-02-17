from Utils.file_integrity import *
from config import VIRUSTOTAL_API_KEY
from Utils.logging_utils import log_this
import time, os, shutil, requests, io


# File Upload Blueprint
upload_bp = Blueprint('file', __name__, template_folder='templates')


UPLOAD_FOLDER = 'Files/Perma'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@upload_bp.route('/upload', methods=['GET', 'POST'])
@roles_required('doctor')
def upload_file():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash("Please log in to upload files.", 'error')
            return redirect(url_for('login.login'))

        user_id = session['user_id']
        file = request.files.get('file')
        title = request.form.get('title')
        description = request.form.get('description')

        if not file or not allowed_file(file.filename):
            flash("Invalid file type or no file uploaded.", 'error')
            log_this('Invalid file type or no file uploaded', 'high')
            return redirect(request.url)

        if not is_file_size_valid(file):
            flash("File exceeds the maximum size limit.", 'error')
            log_this('User exceeds file size limit', 'critical')
            return redirect(request.url)

        file_in_memory = io.BytesIO(file.read())

        scan_result = scan_file_virustotal(file_in_memory)
        if "error" in scan_result:
            flash(f"File rejected: {scan_result['error']}", 'error')
            # Reset memory stream for cleanup
            file_in_memory.close()
            return redirect(request.url)

        user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
        os.makedirs(user_folder, exist_ok=True)

        filename = secure_filename(file.filename)
        permanent_file_path = os.path.join(user_folder, filename)

        with open(permanent_file_path, 'wb') as f:
            f.write(file_in_memory.getvalue())

        file_in_memory.close()
        file_hash = generate_file_hash(permanent_file_path)

        try:
            mycursor = mydb.cursor()
            query = """
                INSERT INTO file (User_ID, File_Name, File_Path, File_Size, File_Hash, Title, Description, File_Type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            mycursor.execute(query, (user_id, filename, permanent_file_path, os.path.getsize(permanent_file_path), file_hash, title, description, filename.rsplit('.', 1)[1]))
            mydb.commit()
            flash("File uploaded successfully!", 'success')
        except Exception as e:
            flash(f"Error uploading file: {e}", 'error')
        log_this("File uploaded successfully")
        return redirect(url_for('file.upload_file'))

    return render_template('Features/upload.html')


def scan_file_virustotal(file_in_memory):
    """Scan a file in memory using VirusTotal API and ensure results before allowing upload."""
    url = "https://www.virustotal.com/api/v3/files"
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}

    try:
        # Instead of file_path, use in-memory bytesIO file
        files = {"file": file_in_memory}
        response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            result = response.json()
            scan_id = result.get("data", {}).get("id", None)

            if not scan_id:
                return {"error": "Failed to retrieve scan ID"}

            # Polling mechanism to wait for scan results
            report_url = f"https://www.virustotal.com/api/v3/analyses/{scan_id}"
            for _ in range(50):
                report_response = requests.get(report_url, headers=headers)
                if report_response.status_code == 200:
                    report_result = report_response.json()
                    status = report_result.get("data", {}).get("attributes", {}).get("status", "")

                    if status == "completed":
                        stats = report_result.get("data", {}).get("attributes", {}).get("stats", {})
                        malicious_count = stats.get("malicious", 0)
                        suspicious_count = stats.get("suspicious", 0)

                        if malicious_count > 0 or suspicious_count > 0:
                            return {"error": "Malware detected", "malicious": malicious_count,
                                    "suspicious": suspicious_count}

                        return {"success": "File is clean"}

                time.sleep(2)  # Wait 2 seconds before retrying

            return {"error": "Scan timed out"}

        return {"error": f"VirusTotal API error: {response.status_code}", "details": response.json()}

    except Exception as e:
        return {"error": f"Error connecting to VirusTotal: {e}"}