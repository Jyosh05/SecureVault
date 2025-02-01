from flask import render_template, Blueprint
from datetime import datetime

from Admin.home import admin_bp
from Utils.general_utils import mydb
from Utils.rbac_utils import roles_required


# ... other imports (your database connection, etc.)

# admin_bp = Blueprint('admin', __name__, url_prefix='/admin')  # If you're using Blueprints

# ... other routes

@admin_bp.route('/security_dashboard')
@roles_required('so')  # Your role-based access control
def security_dashboard():
    with mydb.cursor() as mycursor:
        # Query to count actions and group by action type
        query = """
            SELECT Action, COUNT(*) AS ActionCount
            FROM audit_log
            GROUP BY Action
        """
        mycursor.execute(query)
        data = mycursor.fetchall()

        # Query to get the count for each threat level
        threat_level_query = """
            SELECT Threat_Level, COUNT(*) AS ThreatLevelCount
            FROM audit_log
            GROUP BY Threat_Level
        """
        mycursor.execute(threat_level_query)
        threat_level_data = mycursor.fetchall()

    # Prepare data for the charts (lists for actions and counts)
    actions = [row[0] for row in data]
    action_counts = [row[1] for row in data]

    # Prepare threat level data
    threat_levels = [row[0] for row in threat_level_data]
    threat_level_counts = [row[1] for row in threat_level_data]


    return render_template('Admin/security_dashboard.html',
                           actions=actions,
                           action_counts=action_counts,
                           threat_levels=threat_levels,
                           threat_level_counts=threat_level_counts,
                           nameOfPage='Security Dashboard')

# ... your log_this function (as provided in the previous response)