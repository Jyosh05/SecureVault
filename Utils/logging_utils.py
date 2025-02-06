
from datetime import datetime
from flask import session
from Utils.general_utils import mydb


mycursor = mydb.cursor(buffered=True)
# def log_this(event, user_id=0):
#     #global user_id
#     # We do a select max to get the last log_id in the table
#     # the fetchone returns the field in a tuple format
#     if 'user' in session and 'ID' in session['user']:
#         user_id = session['user']['ID']
#     mycursor.execute("SELECT MAX(ID) FROM audit_log")
#     actual_id = mycursor.fetchone()
#
#     if actual_id[0] is None:
#         actual_id = (0,)  # Ensure actual_id is a tuple with the first element as 0
#     next_id = actual_id[0] + 1
#     # ts1 = timestamp()
#     sql = "INSERT INTO audit_log (ID, Action, Event_Time, USER_ID) VALUES (%s,%s,%s,%s)"
#     val = (next_id, event, datetime.now(), user_id)
#     mycursor.execute(sql, val)
#
#     mydb.commit()

def log_this(event, threat_level='low'):
    """Logs an event, retrieving user_id from the session if available."""

    user_id = session.get('user_id')  # Get user_id from session, no default needed

    # Check if user_id exists in the session and is not None
    # if user_id is None:
    #     user_id = "unknown"  # Set to "unknown" if not logged in
    # else:
    #     # Ensure it's an integer if it exists
    #     user_id = int(user_id)

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
