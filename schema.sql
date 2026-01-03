-- OLEG Database Schema
-- SQLite database for user management, courses, activities, and progress tracking

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    study_guide TEXT NOT NULL,
    schedule_data TEXT NOT NULL,
    duration_weeks INTEGER DEFAULT 20,
    start_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, name)
);

-- Activities table
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    day_number INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    scheduled_date DATE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    duration_minutes INTEGER,
    activity_type VARCHAR(50) DEFAULT 'study',
    theory_content TEXT,
    test_questions TEXT,
    test_solutions TEXT,
    content_generated BOOLEAN DEFAULT 0,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- Activity completions table
CREATE TABLE IF NOT EXISTS activity_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE,
    UNIQUE(activity_id)
);

-- Daily progress table
CREATE TABLE IF NOT EXISTS daily_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    date DATE NOT NULL,
    activities_completed INTEGER DEFAULT 0,
    total_activities INTEGER DEFAULT 0,
    is_complete BOOLEAN DEFAULT 0,
    completed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE(user_id, course_id, date)
);

-- User streaks table
CREATE TABLE IF NOT EXISTS user_streaks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    total_study_days INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE(user_id, course_id)
);

-- Checkpoint tests table
CREATE TABLE IF NOT EXISTS checkpoint_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    checkpoint_number INTEGER NOT NULL,
    week_after INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    questions TEXT NOT NULL,
    solutions TEXT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- Checkpoint submissions table
CREATE TABLE IF NOT EXISTS checkpoint_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checkpoint_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    score INTEGER,
    notes TEXT,
    FOREIGN KEY (checkpoint_id) REFERENCES checkpoint_tests(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_courses_user_id ON courses(user_id);
CREATE INDEX IF NOT EXISTS idx_activities_course_id ON activities(course_id);
CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_activity_completions_activity_id ON activity_completions(activity_id);
CREATE INDEX IF NOT EXISTS idx_daily_progress_user_course ON daily_progress(user_id, course_id);
CREATE INDEX IF NOT EXISTS idx_daily_progress_date ON daily_progress(date);
CREATE INDEX IF NOT EXISTS idx_user_streaks_user_course ON user_streaks(user_id, course_id);
