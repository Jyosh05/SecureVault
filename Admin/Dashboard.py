from flask import render_template, Blueprint, jsonify
from datetime import datetime

from Admin.home import admin_bp
from Utils.general_utils import mydb
from Utils.rbac_utils import roles_required





# admin_bp = Blueprint('admin', __name__, url_prefix='/admin')  # If you're using Blueprints
dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates', url_prefix='/dashboard')  # New blueprint
@admin_bp.route('/security_dashboard')
@roles_required('so')  # Ensure access control
def security_dashboard():
    with mydb.cursor() as mycursor:
        # Fetch action count
        query = """
            SELECT Action, COUNT(*) AS ActionCount
            FROM audit_log
            GROUP BY Action
        """
        mycursor.execute(query)
        data = mycursor.fetchall()

        # Fetch threat level count
        threat_level_query = """
            SELECT Threat_Level, COUNT(*) AS ThreatLevelCount
            FROM audit_log
            GROUP BY Threat_Level
        """
        mycursor.execute(threat_level_query)
        threat_level_data = mycursor.fetchall()

        # Fetch events by timestamp for the line chart
        event_timeline_query = """
            SELECT DATE_FORMAT(Event_Time, '%Y-%m-%d %H:%i') AS event_time, COUNT(*) AS event_count
            FROM audit_log
            GROUP BY event_time
            ORDER BY event_time ASC
        """
        mycursor.execute(event_timeline_query)
        timeline_data = mycursor.fetchall()

        # Fetch top 5 active users
        user_activity_query = """
            SELECT User_ID, COUNT(*) AS UserActivityCount
            FROM audit_log
            GROUP BY User_ID
            ORDER BY UserActivityCount DESC
            LIMIT 5
        """
        mycursor.execute(user_activity_query)
        user_activity_data = mycursor.fetchall()

        # Fetch top 5 triggering actions
        action_trigger_query = """
            SELECT Action, COUNT(*) AS ActionTriggerCount
            FROM audit_log
            GROUP BY Action
            ORDER BY ActionTriggerCount DESC
            LIMIT 5
        """
        mycursor.execute(action_trigger_query)
        action_trigger_data = mycursor.fetchall()


    # Extract data for charts
    actions = [row[0] for row in data]
    action_counts = [row[1] for row in data]

    threat_levels = [row[0] for row in threat_level_data]
    threat_level_counts = [row[1] for row in threat_level_data]

    # Extract timestamps & event counts
    event_times = [row[0] for row in timeline_data]
    event_counts = [row[1] for row in timeline_data]

    # Define security level colors
    security_level_colors = {
        'Safe': 'green',
        'Neutral': 'gray',
        'Warning': 'orange',
        'Critical': 'red'
    }

    return render_template(
        'Admin/security_dashboard.html',
        actions=actions,
        action_counts=action_counts,
        threat_levels=threat_levels,
        threat_level_counts=threat_level_counts,
        user_activity_data=user_activity_data,  # New data for top users
        action_trigger_data=action_trigger_data,  # New data for top actions
        nameOfPage='Security Dashboard',
        security_level_colors=security_level_colors,
        event_times=event_times,
        event_counts=event_counts
    )
