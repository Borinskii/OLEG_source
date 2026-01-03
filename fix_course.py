"""
Script to add tasks to existing courses that don't have activities
"""
import db
from funcs import parse_schedule_to_activities
from datetime import date, timedelta

def fix_courses():
    """Add tasks to courses that don't have any activities"""

    # Get all courses
    conn = db.get_db_connection()
    courses = conn.execute("SELECT * FROM courses").fetchall()
    conn.close()

    for course in courses:
        course_id = course['id']

        # Check if course has activities
        activities = db.get_activities_by_course(course_id)

        if len(activities) == 0:
            print(f"\nCourse '{course['name']}' (ID: {course_id}) has no activities")
            print("Adding tasks...")

            # Calculate start date (next Monday from today)
            today = date.today()
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            start_date = today + timedelta(days=days_until_monday)

            # Update course start_date
            conn = db.get_db_connection()
            conn.execute(
                "UPDATE courses SET start_date = ? WHERE id = ?",
                (start_date, course_id)
            )
            conn.commit()
            conn.close()

            # Parse and create activities
            schedule_data = course['schedule_data']
            activities = parse_schedule_to_activities(schedule_data, course_id, start_date)

            if activities:
                db.bulk_create_activities(activities)
                print(f"✓ Created {len(activities)} activities starting from {start_date}")
            else:
                print("✗ No activities could be parsed from schedule")
        else:
            print(f"Course '{course['name']}' already has {len(activities)} activities - skipping")

if __name__ == '__main__':
    print("Fixing courses without activities...\n")
    fix_courses()
    print("\n✓ Done!")
