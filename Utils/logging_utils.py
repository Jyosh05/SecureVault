
from datetime import datetime
from flask import session
from Utils.general_utils import mydb


mycursor = mydb.cursor(buffered=True)

def log_this(event, threat_level='low'):
    """Logs an event, retrieving user_id from the session if available."""

    user_id = session.get('user_id')  # Get user_id from session, no default needed

    mycursor.execute("SELECT MAX(ID) FROM audit_log")  # Correct table name
    actual_id = mycursor.fetchone()

    if actual_id[0] is None:
        next_id = 1  # Start from 1 if the table is empty
    else:
        next_id = actual_id[0] + 1

    sql = """
    INSERT INTO audit_log (ID, Action, Event_Time, User_ID, Threat_Level) 
    VALUES (%s, %s, %s, %s, %s)
    """  # Include Threat_Level
    val = (next_id, event, datetime.now(), user_id, threat_level)
    mycursor.execute(sql, val)
    mydb.commit()
