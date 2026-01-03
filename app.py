# app.py
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, abort
from flask_session import Session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import PyPDF2
from funcs import chat, load_llm, load_llm1, MODEL_NAME
import shutil
import os

# Import database and auth modules
import db
from models import User
from auth import register_user, login_user_auth

# Flask app initialization
app = Flask(__name__)

# Flask session configuration
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.get(int(user_id))

# Initialize database on startup
try:
    db.init_database()
    print("Database initialized successfully")
except Exception as e:
    print(f"Database already initialized or error: {e}")


# ==================
# AUTHENTICATION ROUTES
# ==================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        success, message, user = login_user_auth(username, password)

        if success:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            return render_template('login.html', error=message)

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validate password confirmation
        if password != confirm_password:
            return render_template('register.html',
                                 error="Passwords do not match",
                                 username=username,
                                 email=email)

        success, message, user_id = register_user(username, email, password)

        if success:
            # Auto-login after registration
            user = User.get(user_id)
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('register.html',
                                 error=message,
                                 username=username,
                                 email=email)

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('login'))


# ==================
# MAIN ROUTES
# ==================

@app.route('/')
@login_required
def index():
    """Home page showing user's courses"""
    # Get courses from database instead of session
    courses = db.get_user_courses(current_user.id)
    return render_template('index.html', courses=courses)


@app.route('/new_course')
@login_required
def new_course():
    session.pop('chat_history', None)
    return render_template('new_course.html')


@app.route('/send', methods=['POST'])
@login_required
def send():
    user_message = request.json.get('formdata')

    if 'chat_history' not in session:
        session['chat_history'] = []

    bot_response, updated_chat_history = generate_bot_response(user_message, session['chat_history'])
    session['chat_history'] = updated_chat_history

    return jsonify({'response': bot_response})


@app.route('/clear', methods=['POST'])
@login_required
def clear_chat():
    session.pop('chat_history', None)
    return jsonify({'status': 'success'})


@app.route('/finish', methods=['POST'])
@login_required
def handle_finish():
    print("FINISHED!")

    # Get duration from request or default to 20 weeks
    duration_weeks = 20
    if request.json and 'duration_weeks' in request.json:
        duration_weeks = int(request.json['duration_weeks'])

    # Get chat history
    chat_history = session.get('chat_history', [])

    if not chat_history:
        return jsonify({'status': 'error', 'message': 'No conversation history found'}), 400

    # Extract course name with minimal context
    course_name = extract_course_name(chat_history)
    course_name = course_name.strip().replace('\n', ' ').replace('"', '').replace("'", "")

    if course_name.lower().startswith('assistant:'):
        course_name = course_name[10:].strip()

    print(f"DEBUG: Generated course name: '{course_name}'")

    # Generate study guide (ONE API call)
    print("Generating study guide...")
    study_guide = generate_study_guide(chat_history)

    # Generate complete schedule (ONE API call instead of 20!)
    print(f"Generating {duration_weeks}-week schedule...")
    schedule = generate_complete_schedule(study_guide, duration_weeks)

    # Save to database
    try:
        # Calculate start date (next Monday from today)
        from datetime import date, timedelta
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        start_date = today + timedelta(days=days_until_monday)

        # Create course in database
        course_id = db.create_course(
            user_id=current_user.id,
            name=course_name,
            study_guide=study_guide,
            schedule_data=schedule,
            duration_weeks=duration_weeks,
            start_date=start_date
        )
        print(f"DEBUG: Created course with ID {course_id}, start date: {start_date}")

        # Parse and save activities
        from funcs import parse_schedule_to_activities
        activities = parse_schedule_to_activities(schedule, course_id, start_date)
        if activities:
            db.bulk_create_activities(activities)
            print(f"DEBUG: Created {len(activities)} activities")

        # Initialize streak record
        db.initialize_user_streak(current_user.id, course_id)

        # Clear chat history from session
        session.pop('chat_history', None)

        print("Course creation completed!")
        return jsonify({'status': 'success', 'course_id': course_id, 'course_name': course_name})

    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        print(f"Error creating course: {e}")
        return jsonify({'status': 'error', 'message': f'Error creating course: {str(e)}'}), 500


@app.route('/course/<int:course_id>')
@login_required
def course_page(course_id):
    """Dynamically serve the page for each course based on course ID."""
    # Load course from database
    course = db.get_course_by_id(course_id)

    if not course:
        abort(404, "Course not found")

    # Verify ownership
    if course['user_id'] != current_user.id:
        abort(403, "You don't have permission to view this course")

    # Split study guide into lines for template
    final_respond = course['study_guide'].split('\n')

    # Split schedule into lines for template
    schedule_content = course['schedule_data'].split('\n')

    return render_template('course_template.html',
                         course_name=course['name'],
                         course_id=course_id,
                         model_respond1=final_respond,
                         schedule_content=schedule_content)


@app.route('/load_file', methods=['POST'])
@login_required
def get_file():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    pdf_file = request.files['pdf_file']

    if pdf_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Create uploads directory if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    upload_path = f'uploads/{pdf_file.filename}'
    pdf_file.save(upload_path)

    # Extract text from PDF
    try:
        with open(upload_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

        # Preprocess text
        text = text.replace("\n", " ").replace("\t", " ")
        text = text[:3000]  # Limit to first 3000 chars to avoid huge context
        text += " [PDF file content]"

        bot_response, updated_chat_history = generate_bot_response(text, session.get('chat_history', []))
        session['chat_history'] = updated_chat_history

        return jsonify({'response': bot_response})
    except Exception as e:
        return jsonify({'error': f'Error processing PDF: {str(e)}'}), 500


@app.route('/clear_courses', methods=['GET', 'POST'])
@login_required
def clear_courses():
    """Clear all courses for current user"""
    # Get all user courses and delete them
    courses = db.get_user_courses(current_user.id)
    for course in courses:
        db.delete_course(course['id'])

    if request.method == 'POST':
        return jsonify({'status': 'success'})
    else:
        return redirect('/')


# Load model names
model_l70 = load_llm()
model_l70_1 = load_llm1()


def extract_course_name(chat_history):
    """Extract course name with minimal context"""
    # Only use last 6 messages for context
    recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history

    prompt = f"""Based on this conversation, extract ONLY the course subject name in maximum 2 words.
Output ONLY the course name, nothing else.

Recent conversation:
{chr(10).join(recent_history)}

Course name (2 words max):"""

    generated_text = chat(
        model=model_l70,
        messages=[{"role": "user", "content": prompt}],
        options={"max_tokens": 50, "temperature": 0.3}
    )

    return generated_text.strip()


def summarize_course_content(chat_history):
    """Summarize chat history to reduce token usage"""
    if len(chat_history) <= 10:
        return chr(10).join(chat_history)

    # Extract key information from chat
    user_messages = [msg for msg in chat_history if msg.startswith('user:')]

    # Take first 3 and last 3 user messages
    key_messages = user_messages[:3] + user_messages[-3:]

    return chr(10).join(key_messages)


def generate_study_guide(chat_history):
    """Generate study guide with summarized context"""
    # Summarize chat history instead of sending everything
    course_summary = summarize_course_content(chat_history)

    prompt = f"""You are OLEG, an educational assistant. Create a comprehensive study guide based on this course information:

{course_summary}

Create a structured study guide with these sections for each major topic (minimum 3 topics):

**Topic 1: [Topic Name]**

**Definition:** Clear explanation of the topic and its main concepts.

**Theoretical Foundations:** Main theories and scientific concepts underlying this topic.

**Practical Application:** Real-world applications and use cases in different fields.

**Key Terms:**
* **Term 1:** Definition
* **Term 2:** Definition
* **Term 3:** Definition

**Resources:**
* Book/Article 1
* Book/Article 2

Repeat this structure for all major topics in the course. Format everything clearly."""

    generated_text = chat(
        model=model_l70_1,
        messages=[{"role": "user", "content": prompt}],
        options={"max_tokens": 4000, "temperature": 0.7}
    )

    return generated_text


def generate_complete_schedule(study_guide, duration_weeks=20):
    """Generate entire schedule in ONE API call"""

    # Limit study guide context to avoid token overflow
    study_guide_summary = study_guide[:2500] if len(study_guide) > 2500 else study_guide

    total_days = duration_weeks * 7

    prompt = f"""You are OLEG. Based on this study guide, create a COMPLETE {duration_weeks}-week study schedule ({total_days} days total).

Study Guide:
{study_guide_summary}

Requirements:
- {duration_weeks} weeks total
- Maximum 1 hour of study per day
- Distribute all topics evenly across all weeks
- Include checkpoint tests after completing each major topic with solutions
- Each week should have 7 days of activities

Generate the ENTIRE {duration_weeks}-week schedule in ONE response. Format each week clearly:

**Week 1 (September 1-7)**
- Day 1: Introduction to [Topic] (30 min)
- Day 2: Study [Subtopic] (45 min)
- Day 3: Practice [Concept] (1 hour)
- Day 4: Review [Material] (30 min)
- Day 5: Deep dive into [Topic] (1 hour)
- Day 6: Study [Resource] (45 min)
- Day 7: Weekly review (30 min)

**Week 2 (September 8-14)**
[Continue pattern...]

**Checkpoint Test 1** (after Week 3-4)
Questions:
1. [Question about covered material]
2. [Question about covered material]
3. [Question about covered material]

Solutions:
1. [Detailed solution]
2. [Detailed solution]
3. [Detailed solution]

Generate ALL {duration_weeks} weeks with appropriate checkpoint tests distributed throughout:"""

    generated_text = chat(
        model=model_l70_1,
        messages=[{"role": "user", "content": prompt}],
        options={"max_tokens": 8000, "temperature": 0.7}
    )

    return generated_text


def generate_bot_response(message, chat_history):
    """Optimized chat response - only keep recent context"""
    chat_history.append(f"user: {message}")

    # Only use last 10 messages for context (not entire history!)
    recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history

    prompt = f"""You are OLEG: An educational assistant helping users create study courses.

Be brief, friendly, and helpful. Ask clarifying questions if needed.

Recent conversation:
{chr(10).join(recent_history)}

Respond briefly to the user's last message:"""

    generated_text = chat(
        model=model_l70,
        messages=[{"role": "user", "content": prompt}],
        options={"max_tokens": 500, "temperature": 0.7}
    )

    chat_history.append(f"assistant: {generated_text}")

    # Keep only last 20 messages in session to prevent memory bloat
    if len(chat_history) > 20:
        chat_history = chat_history[-20:]

    return generated_text, chat_history


# ==================
# CALENDAR & TASK API ENDPOINTS
# ==================

@app.route('/api/course/<int:course_id>/calendar/<int:year>/<int:month>')
@login_required
def get_calendar(course_id, year, month):
    """Get calendar data for a specific month"""
    # Verify ownership
    if not db.verify_course_ownership(course_id, current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403

    from datetime import date
    calendar_data = db.get_calendar_data(current_user.id, course_id, year, month)

    return jsonify(calendar_data)


@app.route('/api/course/<int:course_id>/tasks/<date_str>')
@login_required
def get_daily_tasks(course_id, date_str):
    """Get tasks for a specific date"""
    # Verify ownership
    if not db.verify_course_ownership(course_id, current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403

    from datetime import date
    try:
        target_date = date.fromisoformat(date_str)
        tasks = db.get_activities_for_date(course_id, target_date)
        return jsonify({'tasks': tasks})
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400


@app.route('/api/course/<int:course_id>/daily-lesson/<date_str>')
@login_required
def get_daily_lesson(course_id, date_str):
    """Get complete daily lesson with all content and steps for a specific date"""
    # Verify ownership
    if not db.verify_course_ownership(course_id, current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403

    from datetime import date
    try:
        target_date = date.fromisoformat(date_str)
        activities = db.get_activities_for_date(course_id, target_date)

        if not activities:
            return jsonify({
                'date': date_str,
                'has_content': False,
                'message': 'No lesson scheduled for this day'
            })

        # Check if this is a test day
        is_test_day = any(act['activity_type'] in ['test', 'checkpoint'] for act in activities)

        # Get course for study guide context
        course = db.get_course_by_id(course_id)

        # Generate content for activities that don't have it yet
        from funcs import generate_task_content, load_llm
        model = load_llm()

        for activity in activities:
            # Check if content needs to be generated
            if not activity.get('content_generated'):
                # Generate content based on activity type
                content = generate_task_content(
                    task_title=activity['title'],
                    task_type=activity['activity_type'],
                    study_guide_summary=course['study_guide'][:2000],  # First 2000 chars
                    model=model
                )

                # Update the activity with generated content
                db.update_activity_content(
                    activity['id'],
                    theory_content=content.get('theory_content'),
                    test_questions=content.get('test_questions'),
                    test_solutions=content.get('test_solutions')
                )

                # Update the activity dict
                activity['theory_content'] = content.get('theory_content')
                activity['test_questions'] = content.get('test_questions')
                activity['test_solutions'] = content.get('test_solutions')
                activity['content_generated'] = 1

        # Collect all content and determine lesson type
        lesson_data = {
            'date': date_str,
            'day_number': activities[0]['day_number'] if activities else None,
            'week_number': activities[0]['week_number'] if activities else None,
            'is_test_day': is_test_day,
            'has_content': True,
            'activities': activities,
            'lesson_title': None,
            'steps': [],
            'completed': all(act['completed_at'] for act in activities)
        }

        # Determine lesson title from first activity
        if activities:
            first_activity = activities[0]
            lesson_data['lesson_title'] = first_activity['title']

        return jsonify(lesson_data)

    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400


@app.route('/api/course/<int:course_id>/task/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(course_id, task_id):
    """Mark a task as complete"""
    # Verify ownership
    if not db.verify_course_ownership(course_id, current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403

    from datetime import date
    activity = db.get_activity_by_id(task_id)

    if not activity or activity['course_id'] != course_id:
        return jsonify({'error': 'Task not found'}), 404

    notes = request.json.get('notes', '') if request.json else ''
    success = db.mark_activity_complete(task_id, notes)

    if success:
        # Update daily progress and streak
        target_date = date.fromisoformat(activity['scheduled_date'])
        db.update_daily_progress(current_user.id, course_id, target_date)
        db.update_streak_record(current_user.id, course_id)

        return jsonify({'status': 'success', 'message': 'Task marked as complete'})
    else:
        return jsonify({'status': 'error', 'message': 'Task already completed'}), 400


@app.route('/api/course/<int:course_id>/task/<int:task_id>/incomplete', methods=['POST'])
@login_required
def incomplete_task(course_id, task_id):
    """Mark a task as incomplete"""
    # Verify ownership
    if not db.verify_course_ownership(course_id, current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403

    from datetime import date
    activity = db.get_activity_by_id(task_id)

    if not activity or activity['course_id'] != course_id:
        return jsonify({'error': 'Task not found'}), 404

    success = db.mark_activity_incomplete(task_id)

    if success:
        # Update daily progress and streak
        target_date = date.fromisoformat(activity['scheduled_date'])
        db.update_daily_progress(current_user.id, course_id, target_date)
        db.update_streak_record(current_user.id, course_id)

        return jsonify({'status': 'success', 'message': 'Task marked as incomplete'})
    else:
        return jsonify({'status': 'error', 'message': 'Task was not completed'}), 400


@app.route('/api/course/<int:course_id>/info')
@login_required
def get_course_info(course_id):
    """Get basic course info"""
    # Verify ownership
    if not db.verify_course_ownership(course_id, current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403

    course = db.get_course_by_id(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    return jsonify({
        'id': course['id'],
        'name': course['name'],
        'duration_weeks': course.get('duration_weeks', 20),
        'start_date': course.get('start_date')
    })


@app.route('/api/course/<int:course_id>/statistics')
@login_required
def get_statistics(course_id):
    """Get course statistics and streak info"""
    # Verify ownership
    if not db.verify_course_ownership(course_id, current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403

    stats = db.get_progress_stats(current_user.id, course_id)
    streak = db.get_user_streak(current_user.id, course_id)

    return jsonify({
        'statistics': stats,
        'streak': streak
    })


@app.route('/api/course/<int:course_id>/task/<int:task_id>/content', methods=['GET'])
@login_required
def get_task_content(course_id, task_id):
    """Get or generate content for a specific task"""
    # Verify ownership
    if not db.verify_course_ownership(course_id, current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403

    # Get task from database
    activity = db.get_activity_by_id(task_id)

    if not activity or activity['course_id'] != course_id:
        return jsonify({'error': 'Task not found'}), 404

    # If content already generated, return it
    if activity.get('content_generated'):
        return jsonify({
            'task': activity,
            'generated': True
        })

    # Generate content on-demand
    try:
        from funcs import generate_task_content, load_llm

        # Get course for study guide
        course = db.get_course_by_id(course_id)
        study_guide_summary = course['study_guide'][:1500] if len(course['study_guide']) > 1500 else course['study_guide']

        # Generate content
        model = load_llm()
        content = generate_task_content(
            task_title=activity['title'],
            task_type=activity['activity_type'],
            study_guide_summary=study_guide_summary,
            model=model
        )

        # Update task in database
        db.update_activity_content(
            activity_id=task_id,
            theory_content=content['theory_content'],
            test_questions=content['test_questions'],
            test_solutions=content['test_solutions']
        )

        # Get updated activity
        updated_activity = db.get_activity_by_id(task_id)

        return jsonify({
            'task': updated_activity,
            'generated': True
        })

    except Exception as e:
        print(f"Error generating task content: {e}")
        return jsonify({'error': 'Failed to generate content'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)