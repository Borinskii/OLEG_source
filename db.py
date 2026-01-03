import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
import json

DATABASE_PATH = 'oleg.db'

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign key constraints
    return conn

def init_database():
    """Initialize database with schema from schema.sql"""
    if not os.path.exists('schema.sql'):
        raise FileNotFoundError("schema.sql file not found")

    conn = get_db_connection()
    try:
        with open('schema.sql', 'r') as f:
            schema = f.read()
        conn.executescript(schema)
        conn.commit()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        conn.close()

# ====================
# USER OPERATIONS
# ====================

def create_user(username: str, email: str, password_hash: str) -> int:
    """Create a new user and return user_id"""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        raise ValueError(f"User with that username or email already exists: {e}")
    finally:
        conn.close()

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    conn = get_db_connection()
    try:
        user = conn.execute(
            "SELECT id, username, email, created_at, last_login FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username (including password_hash for authentication)"""
    conn = get_db_connection()
    try:
        user = conn.execute(
            "SELECT id, username, email, password_hash, created_at, last_login FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    conn = get_db_connection()
    try:
        user = conn.execute(
            "SELECT id, username, email, password_hash, created_at, last_login FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def update_last_login(user_id: int):
    """Update user's last login timestamp"""
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now(), user_id)
        )
        conn.commit()
    finally:
        conn.close()

# ====================
# COURSE OPERATIONS
# ====================

def create_course(user_id: int, name: str, study_guide: str, schedule_data: str, duration_weeks: int = 20, start_date = None) -> int:
    """Create a new course and return course_id"""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO courses (user_id, name, study_guide, schedule_data, duration_weeks, start_date) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, name, study_guide, schedule_data, duration_weeks, start_date)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Course '{name}' already exists for this user")
    finally:
        conn.close()

def get_course_by_id(course_id: int) -> Optional[Dict]:
    """Get course by ID"""
    conn = get_db_connection()
    try:
        course = conn.execute(
            "SELECT * FROM courses WHERE id = ?",
            (course_id,)
        ).fetchone()
        return dict(course) if course else None
    finally:
        conn.close()

def get_user_courses(user_id: int) -> List[Dict]:
    """Get all courses for a user"""
    conn = get_db_connection()
    try:
        courses = conn.execute(
            "SELECT * FROM courses WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
        return [dict(course) for course in courses]
    finally:
        conn.close()

def get_course_by_name(user_id: int, name: str) -> Optional[Dict]:
    """Get course by user_id and name"""
    conn = get_db_connection()
    try:
        course = conn.execute(
            "SELECT * FROM courses WHERE user_id = ? AND name = ?",
            (user_id, name)
        ).fetchone()
        return dict(course) if course else None
    finally:
        conn.close()

def delete_course(course_id: int):
    """Delete a course (cascades to activities, completions, etc.)"""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        conn.commit()
    finally:
        conn.close()

def update_course(course_id: int, study_guide: str = None, schedule_data: str = None):
    """Update course content"""
    conn = get_db_connection()
    try:
        if study_guide:
            conn.execute(
                "UPDATE courses SET study_guide = ?, updated_at = ? WHERE id = ?",
                (study_guide, datetime.now(), course_id)
            )
        if schedule_data:
            conn.execute(
                "UPDATE courses SET schedule_data = ?, updated_at = ? WHERE id = ?",
                (schedule_data, datetime.now(), course_id)
            )
        conn.commit()
    finally:
        conn.close()

# ====================
# ACTIVITY OPERATIONS
# ====================

def create_activity(course_id: int, week_number: int, day_number: int,
                   day_of_week: int, scheduled_date: date, title: str,
                   description: str = None, duration_minutes: int = None,
                   activity_type: str = 'study') -> int:
    """Create a new activity and return activity_id"""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO activities
               (course_id, week_number, day_number, day_of_week, scheduled_date,
                title, description, duration_minutes, activity_type)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (course_id, week_number, day_number, day_of_week, scheduled_date,
             title, description, duration_minutes, activity_type)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def bulk_create_activities(activities: List[Dict]):
    """Bulk insert activities for a course"""
    conn = get_db_connection()
    try:
        conn.executemany(
            """INSERT INTO activities
               (course_id, week_number, day_number, day_of_week, scheduled_date,
                title, description, duration_minutes, activity_type)
               VALUES (:course_id, :week_number, :day_number, :day_of_week, :scheduled_date,
                       :title, :description, :duration_minutes, :activity_type)""",
            activities
        )
        conn.commit()
    finally:
        conn.close()

def get_activities_by_course(course_id: int) -> List[Dict]:
    """Get all activities for a course"""
    conn = get_db_connection()
    try:
        activities = conn.execute(
            """SELECT a.*, ac.completed_at
               FROM activities a
               LEFT JOIN activity_completions ac ON a.id = ac.activity_id
               WHERE a.course_id = ?
               ORDER BY a.day_number""",
            (course_id,)
        ).fetchall()
        return [dict(activity) for activity in activities]
    finally:
        conn.close()

def get_activities_for_date(course_id: int, target_date: date) -> List[Dict]:
    """Get activities for a specific date"""
    conn = get_db_connection()
    try:
        activities = conn.execute(
            """SELECT a.*, ac.completed_at, ac.notes
               FROM activities a
               LEFT JOIN activity_completions ac ON a.id = ac.activity_id
               WHERE a.course_id = ? AND a.scheduled_date = ?
               ORDER BY a.id""",
            (course_id, target_date)
        ).fetchall()
        return [dict(activity) for activity in activities]
    finally:
        conn.close()

def get_activity_by_id(activity_id: int) -> Optional[Dict]:
    """Get activity by ID"""
    conn = get_db_connection()
    try:
        activity = conn.execute(
            """SELECT a.*, ac.completed_at, ac.notes, c.user_id
               FROM activities a
               LEFT JOIN activity_completions ac ON a.id = ac.activity_id
               JOIN courses c ON a.course_id = c.id
               WHERE a.id = ?""",
            (activity_id,)
        ).fetchone()
        return dict(activity) if activity else None
    finally:
        conn.close()

def update_activity_content(activity_id: int, theory_content: str = None,
                           test_questions: str = None, test_solutions: str = None):
    """Update activity content (theory or test)"""
    conn = get_db_connection()
    try:
        conn.execute(
            """UPDATE activities
               SET theory_content = ?,
                   test_questions = ?,
                   test_solutions = ?,
                   content_generated = 1
               WHERE id = ?""",
            (theory_content, test_questions, test_solutions, activity_id)
        )
        conn.commit()
    finally:
        conn.close()

# ====================
# ACTIVITY COMPLETION OPERATIONS
# ====================

def mark_activity_complete(activity_id: int, notes: str = None) -> bool:
    """Mark an activity as complete"""
    conn = get_db_connection()
    try:
        # Check if already completed
        existing = conn.execute(
            "SELECT id FROM activity_completions WHERE activity_id = ?",
            (activity_id,)
        ).fetchone()

        if existing:
            return False  # Already completed

        conn.execute(
            "INSERT INTO activity_completions (activity_id, notes) VALUES (?, ?)",
            (activity_id, notes)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def mark_activity_incomplete(activity_id: int) -> bool:
    """Mark an activity as incomplete (remove completion)"""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM activity_completions WHERE activity_id = ?",
            (activity_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def is_activity_completed(activity_id: int) -> bool:
    """Check if an activity is completed"""
    conn = get_db_connection()
    try:
        result = conn.execute(
            "SELECT id FROM activity_completions WHERE activity_id = ?",
            (activity_id,)
        ).fetchone()
        return result is not None
    finally:
        conn.close()

# ====================
# DAILY PROGRESS OPERATIONS
# ====================

def update_daily_progress(user_id: int, course_id: int, target_date: date):
    """Update daily progress for a specific date"""
    conn = get_db_connection()
    try:
        # Get all activities for this date
        activities = conn.execute(
            """SELECT a.id, ac.completed_at
               FROM activities a
               LEFT JOIN activity_completions ac ON a.id = ac.activity_id
               WHERE a.course_id = ? AND a.scheduled_date = ?""",
            (course_id, target_date)
        ).fetchall()

        total_activities = len(activities)
        completed_activities = sum(1 for a in activities if a['completed_at'])
        is_complete = total_activities > 0 and completed_activities == total_activities

        # Upsert daily progress
        conn.execute(
            """INSERT INTO daily_progress
               (user_id, course_id, date, activities_completed, total_activities, is_complete, completed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id, course_id, date) DO UPDATE SET
               activities_completed = ?,
               total_activities = ?,
               is_complete = ?,
               completed_at = CASE WHEN ? = 1 AND completed_at IS NULL THEN ? ELSE completed_at END""",
            (user_id, course_id, target_date, completed_activities, total_activities,
             is_complete, datetime.now() if is_complete else None,
             completed_activities, total_activities, is_complete, is_complete, datetime.now())
        )
        conn.commit()
    finally:
        conn.close()

def get_daily_progress(user_id: int, course_id: int, target_date: date) -> Optional[Dict]:
    """Get daily progress for a specific date"""
    conn = get_db_connection()
    try:
        progress = conn.execute(
            """SELECT * FROM daily_progress
               WHERE user_id = ? AND course_id = ? AND date = ?""",
            (user_id, course_id, target_date)
        ).fetchone()
        return dict(progress) if progress else None
    finally:
        conn.close()

def get_monthly_progress(user_id: int, course_id: int, year: int, month: int) -> List[Dict]:
    """Get daily progress for a specific month"""
    conn = get_db_connection()
    try:
        progress = conn.execute(
            """SELECT * FROM daily_progress
               WHERE user_id = ? AND course_id = ?
               AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
               ORDER BY date""",
            (user_id, course_id, str(year), f"{month:02d}")
        ).fetchall()
        return [dict(p) for p in progress]
    finally:
        conn.close()

# ====================
# STREAK OPERATIONS
# ====================

def calculate_streak(user_id: int, course_id: int) -> int:
    """
    Calculate current streak based on daily_progress
    Returns the current streak count
    """
    conn = get_db_connection()
    try:
        # Get all completed days ordered by date DESC
        completed_days = conn.execute(
            """SELECT date FROM daily_progress
               WHERE user_id = ? AND course_id = ? AND is_complete = 1
               ORDER BY date DESC""",
            (user_id, course_id)
        ).fetchall()

        if not completed_days:
            return 0

        today = date.today()
        yesterday = today - timedelta(days=1)

        # Streak must include today or yesterday
        most_recent = date.fromisoformat(completed_days[0]['date'])
        if most_recent < yesterday:
            return 0  # Streak broken

        # Count consecutive days
        streak = 0
        expected_date = today if most_recent == today else yesterday

        for row in completed_days:
            day = date.fromisoformat(row['date'])
            if day == expected_date:
                streak += 1
                expected_date -= timedelta(days=1)
            else:
                break

        return streak
    finally:
        conn.close()

def update_streak_record(user_id: int, course_id: int):
    """Update streak table with latest streak info"""
    current_streak = calculate_streak(user_id, course_id)

    conn = get_db_connection()
    try:
        # Get existing streak record
        existing = conn.execute(
            "SELECT longest_streak FROM user_streaks WHERE user_id = ? AND course_id = ?",
            (user_id, course_id)
        ).fetchone()

        # Count total study days
        total_days = conn.execute(
            """SELECT COUNT(DISTINCT date) as count FROM daily_progress
               WHERE user_id = ? AND course_id = ? AND activities_completed > 0""",
            (user_id, course_id)
        ).fetchone()['count']

        if existing:
            longest = max(existing['longest_streak'], current_streak)
            conn.execute(
                """UPDATE user_streaks
                   SET current_streak = ?, longest_streak = ?,
                       last_activity_date = ?, total_study_days = ?
                   WHERE user_id = ? AND course_id = ?""",
                (current_streak, longest, date.today(), total_days, user_id, course_id)
            )
        else:
            conn.execute(
                """INSERT INTO user_streaks
                   (user_id, course_id, current_streak, longest_streak,
                    last_activity_date, total_study_days)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, course_id, current_streak, current_streak,
                 date.today(), total_days)
            )

        conn.commit()
        return current_streak
    finally:
        conn.close()

def get_user_streak(user_id: int, course_id: int) -> Dict:
    """Get streak information for a user and course"""
    conn = get_db_connection()
    try:
        streak = conn.execute(
            "SELECT * FROM user_streaks WHERE user_id = ? AND course_id = ?",
            (user_id, course_id)
        ).fetchone()

        if streak:
            return dict(streak)
        else:
            # Return default streak info
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'total_study_days': 0,
                'last_activity_date': None
            }
    finally:
        conn.close()

def initialize_user_streak(user_id: int, course_id: int):
    """Initialize streak record for a new course"""
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO user_streaks (user_id, course_id)
               VALUES (?, ?)""",
            (user_id, course_id)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # Streak record already exists
        pass
    finally:
        conn.close()

# ====================
# PROGRESS STATISTICS
# ====================

def get_progress_stats(user_id: int, course_id: int) -> Dict:
    """Get comprehensive progress statistics"""
    conn = get_db_connection()
    try:
        # Total activities
        total_result = conn.execute(
            "SELECT COUNT(*) as count FROM activities WHERE course_id = ?",
            (course_id,)
        ).fetchone()
        total = total_result['count']

        # Completed activities
        completed_result = conn.execute(
            """SELECT COUNT(*) as count FROM activity_completions ac
               JOIN activities a ON ac.activity_id = a.id
               WHERE a.course_id = ?""",
            (course_id,)
        ).fetchone()
        completed = completed_result['count']

        # Days studied
        days_result = conn.execute(
            """SELECT COUNT(DISTINCT date) as count FROM daily_progress
               WHERE user_id = ? AND course_id = ? AND activities_completed > 0""",
            (user_id, course_id)
        ).fetchone()
        days_studied = days_result['count']

        # Weekly breakdown
        weekly = conn.execute(
            """SELECT week_number,
                      COUNT(*) as total,
                      SUM(CASE WHEN ac.id IS NOT NULL THEN 1 ELSE 0 END) as completed
               FROM activities a
               LEFT JOIN activity_completions ac ON a.id = ac.activity_id
               WHERE a.course_id = ?
               GROUP BY week_number
               ORDER BY week_number""",
            (course_id,)
        ).fetchall()

        weekly_progress = [dict(w) for w in weekly]

        return {
            'total_activities': total,
            'completed_activities': completed,
            'progress_percentage': round((completed / total * 100), 1) if total > 0 else 0,
            'days_studied': days_studied,
            'weekly_progress': weekly_progress
        }
    finally:
        conn.close()

# ====================
# CHECKPOINT OPERATIONS
# ====================

def create_checkpoint(course_id: int, checkpoint_number: int, week_after: int,
                     title: str, questions: str, solutions: str) -> int:
    """Create a checkpoint test"""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO checkpoint_tests
               (course_id, checkpoint_number, week_after, title, questions, solutions)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (course_id, checkpoint_number, week_after, title, questions, solutions)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def bulk_create_checkpoints(checkpoints: List[Dict]):
    """Bulk insert checkpoints for a course"""
    conn = get_db_connection()
    try:
        conn.executemany(
            """INSERT INTO checkpoint_tests
               (course_id, checkpoint_number, week_after, title, questions, solutions)
               VALUES (:course_id, :checkpoint_number, :week_after, :title,
                       :questions, :solutions)""",
            checkpoints
        )
        conn.commit()
    finally:
        conn.close()

def get_course_checkpoints(course_id: int) -> List[Dict]:
    """Get all checkpoints for a course"""
    conn = get_db_connection()
    try:
        checkpoints = conn.execute(
            "SELECT * FROM checkpoint_tests WHERE course_id = ? ORDER BY checkpoint_number",
            (course_id,)
        ).fetchall()
        return [dict(cp) for cp in checkpoints]
    finally:
        conn.close()

# ====================
# UTILITY FUNCTIONS
# ====================

def get_calendar_data(user_id: int, course_id: int, year: int, month: int) -> Dict:
    """Get calendar data for a specific month with completion status"""
    conn = get_db_connection()
    try:
        # Get all days in the month with activities
        days = conn.execute(
            """SELECT
                   a.scheduled_date as date,
                   COUNT(DISTINCT a.id) as total_activities,
                   COUNT(DISTINCT ac.activity_id) as completed_activities,
                   dp.is_complete,
                   MAX(CASE WHEN a.activity_type IN ('test', 'checkpoint') THEN 1 ELSE 0 END) as is_test_day
               FROM activities a
               LEFT JOIN activity_completions ac ON a.id = ac.activity_id
               LEFT JOIN daily_progress dp ON a.course_id = dp.course_id
                   AND a.scheduled_date = dp.date AND dp.user_id = ?
               WHERE a.course_id = ?
                   AND strftime('%Y', a.scheduled_date) = ?
                   AND strftime('%m', a.scheduled_date) = ?
               GROUP BY a.scheduled_date
               ORDER BY a.scheduled_date""",
            (user_id, course_id, str(year), f"{month:02d}")
        ).fetchall()

        calendar_days = []
        for day in days:
            total = day['total_activities']
            completed = day['completed_activities']

            # Determine status
            if total == 0:
                status = 'empty'
            elif completed == 0:
                status = 'inactive'
            elif completed == total:
                status = 'complete'
            else:
                status = 'partial'

            calendar_days.append({
                'date': day['date'],
                'status': status,
                'completed': completed,
                'total': total,
                'is_test_day': bool(day['is_test_day'])
            })

        return {'days': calendar_days}
    finally:
        conn.close()

def verify_course_ownership(course_id: int, user_id: int) -> bool:
    """Verify that a course belongs to a user"""
    conn = get_db_connection()
    try:
        result = conn.execute(
            "SELECT user_id FROM courses WHERE id = ?",
            (course_id,)
        ).fetchone()

        if not result:
            return False

        return result['user_id'] == user_id
    finally:
        conn.close()
