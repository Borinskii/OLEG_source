"""
Update course task dates to start from next Monday
"""
import db
from datetime import date, timedelta

# Calculate next Monday
today = date.today()
days_until_monday = (7 - today.weekday()) % 7
if days_until_monday == 0:
    days_until_monday = 7
next_monday = today + timedelta(days=days_until_monday)

print(f"Today: {today}")
print(f"Next Monday: {next_monday}")
print()

# Get the course
conn = db.get_db_connection()
course = conn.execute("SELECT * FROM courses WHERE name = 'Machine Learning'").fetchone()
course_id = course['id']

# Get all activities
activities = conn.execute(
    "SELECT * FROM activities WHERE course_id = ? ORDER BY scheduled_date",
    (course_id,)
).fetchall()

print(f"Found {len(activities)} activities")
print(f"Current first task date: {activities[0]['scheduled_date']}")
print(f"Current last task date: {activities[-1]['scheduled_date']}")
print()

# Calculate the date shift
from datetime import datetime
old_start = datetime.strptime(activities[0]['scheduled_date'], '%Y-%m-%d').date()
date_shift = (next_monday - old_start).days

print(f"Shifting all dates by {date_shift} days...")
print()

# Update all activity dates
for activity in activities:
    old_date = datetime.strptime(activity['scheduled_date'], '%Y-%m-%d').date()
    new_date = old_date + timedelta(days=date_shift)

    conn.execute(
        "UPDATE activities SET scheduled_date = ? WHERE id = ?",
        (new_date, activity['id'])
    )

# Update course start_date
conn.execute(
    "UPDATE courses SET start_date = ? WHERE id = ?",
    (next_monday, course_id)
)

conn.commit()

print(f"[OK] Updated all {len(activities)} tasks")
print(f"[OK] New first task date: {next_monday}")
print(f"[OK] New last task date: {next_monday + timedelta(days=len(activities)-1)}")
print()
print("Done! Refresh your browser to see the tasks.")

conn.close()
