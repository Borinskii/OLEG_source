# app.py
from flask import Flask, render_template, request, jsonify, session, redirect
from flask_session import Session
import PyPDF2
from funcs import chat, load_llm, load_llm1, MODEL_NAME
import shutil
import os

# Flask app initialization
app = Flask(__name__)

# Flask session configuration
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


@app.route('/')
def index():
    buttons = session.get('buttons', [])
    return render_template('index.html', buttons=buttons)


@app.route('/new_course')
def new_course():
    session.pop('chat_history', None)
    return render_template('new_course.html')


@app.route('/send', methods=['POST'])
def send():
    user_message = request.json.get('formdata')

    if 'chat_history' not in session:
        session['chat_history'] = []

    bot_response, updated_chat_history = generate_bot_response(user_message, session['chat_history'])
    session['chat_history'] = updated_chat_history

    return jsonify({'response': bot_response})


@app.route('/clear', methods=['POST'])
def clear_chat():
    session.pop('chat_history', None)
    return jsonify({'status': 'success'})


@app.route('/finish', methods=['POST'])
def handle_finish():
    print("FINISHED!")

    # Clear old files
    for filename in ['schedule.txt', 'preschedule.txt', 'step3.txt', 'saved_course.txt']:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

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

    # Add to session (avoid duplicates)
    if 'buttons' not in session:
        session['buttons'] = []

    existing_courses = [btn.strip().lower() for btn in session['buttons']]
    if course_name.strip().lower() not in existing_courses:
        session['buttons'].append(course_name)
        session.modified = True
        print(f"DEBUG: Added course '{course_name}' to session")
    else:
        print(f"DEBUG: Course '{course_name}' already exists, skipping")

    # Generate study guide (ONE API call)
    print("Generating study guide...")
    study_guide = generate_study_guide(chat_history)
    with open("step3.txt", "w", encoding="UTF-8") as f:
        f.write(study_guide)

    # Generate complete 20-week schedule (ONE API call instead of 20!)
    print("Generating 20-week schedule...")
    schedule = generate_complete_schedule(study_guide)
    with open("schedule.txt", "w", encoding="UTF-8") as f:
        f.write(schedule)

    print("Course creation completed!")
    return jsonify({'status': 'success', 'course_name': course_name})


@app.route('/course/<course_name>')
def course_page(course_name):
    """Dynamically serve the page for each course based on the course name."""
    if os.path.exists("step3.txt"):
        with open("step3.txt", "r", encoding="UTF-8") as f:
            final_respond = f.read().split('\n')
    else:
        final_respond = ["Course content not found. Please regenerate the course."]

    # Load schedule content
    schedule_content = []
    if os.path.exists("schedule.txt"):
        with open("schedule.txt", "r", encoding="UTF-8") as f:
            schedule_content = f.read().split('\n')

    return render_template('course_template.html',
                         course_name=course_name,
                         model_respond1=final_respond,
                         schedule_content=schedule_content)


@app.route('/load_file', methods=['POST'])
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
def clear_courses():
    """Clear all courses"""
    session['buttons'] = []
    session.modified = True

    # Clear temporary files
    for filename in ['saved_course.txt', 'step3.txt', 'schedule.txt', 'preschedule.txt']:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

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


def generate_complete_schedule(study_guide):
    """Generate entire 20-week schedule in ONE API call"""

    # Limit study guide context to avoid token overflow
    study_guide_summary = study_guide[:2500] if len(study_guide) > 2500 else study_guide

    prompt = f"""You are OLEG. Based on this study guide, create a COMPLETE 20-week study schedule (140 days total).

Study Guide:
{study_guide_summary}

Requirements:
- 20 weeks total (September 1 - January 20)
- Maximum 1 hour of study per day
- Distribute all topics evenly across all weeks
- Include checkpoint tests after completing each major topic with solutions
- Each week should have 7 days of activities

Generate the ENTIRE 20-week schedule in ONE response. Format each week clearly:

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

Generate ALL 20 weeks with appropriate checkpoint tests distributed throughout:"""

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)