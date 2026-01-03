"""
Check course details and first task date
"""
import db

# Get the course
conn = db.get_db_connection()
course = conn.execute("SELECT * FROM courses WHERE name = 'Machine Learning'").fetchone()

if course:
    print(f"Course: {course['name']}")
    print(f"ID: {course['id']}")

    try:
        print(f"Duration: {course['duration_weeks']} weeks")
    except:
        print("Duration: N/A")

    try:
        print(f"Start Date: {course['start_date']}")
    except:
        print("Start Date: Not set")
    print()

    # Get first few activities
    activities = conn.execute(
        "SELECT * FROM activities WHERE course_id = ? ORDER BY scheduled_date LIMIT 5",
        (course['id'],)
    ).fetchall()

    print(f"Total activities: {len(db.get_activities_by_course(course['id']))}")
    print("\nFirst 5 activities:")
    for act in activities:
        print(f"  - {act['scheduled_date']}: {act['title']}")

conn.close()
