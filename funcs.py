#funcs.py
import requests
import json
from environs import Env

# Load environment variables ONCE
env = Env()
env.read_env()

# Fireworks AI configuration
FIREWORKS_API_KEY = env.str("FIREWORKS_API_KEY")
FIREWORKS_API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
MODEL_NAME = 'accounts/fireworks/models/llama-v3p3-70b-instruct'


def chat(
        model: str,
        messages: list[dict],
        options: dict = None
):
    """
    Send a chat request to Fireworks AI with automatic streaming for large responses
    """
    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Default generation options
    opts = {
        "max_tokens": 6000,
        "temperature": 0.7,
        "top_p": 1.0,
        "top_k": 1,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0
    }
    if options:
        opts.update(options)

    # Automatically enable streaming if max_tokens > 5000
    max_tokens = opts.get("max_tokens", 6000)
    use_streaming = max_tokens > 5000

    # Assemble payload
    payload = {
        "model": model,
        "messages": messages,
        "stream": use_streaming,
        **opts
    }

    if use_streaming:
        # Handle streaming response
        resp = requests.post(FIREWORKS_API_URL, headers=headers, json=payload, stream=True)
        if resp.status_code != 200:
            raise RuntimeError(f"Fireworks API error {resp.status_code}: {resp.text}")

        # Collect streamed chunks
        full_response = ""
        for line in resp.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    chunk_data = line_text[6:]  # Remove 'data: ' prefix
                    if chunk_data.strip() == '[DONE]':
                        break
                    try:
                        chunk_json = json.loads(chunk_data)
                        if 'choices' in chunk_json and len(chunk_json['choices']) > 0:
                            delta = chunk_json['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            full_response += content
                    except json.JSONDecodeError:
                        continue  # Skip malformed chunks

        return full_response
    else:
        # Handle non-streaming response (for max_tokens <= 5000)
        resp = requests.post(FIREWORKS_API_URL, headers=headers, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"Fireworks API error {resp.status_code}: {resp.text}")

        data = resp.json()
        return data["choices"][0]["message"]["content"]


def load_llm(api_key=None):
    """Compatibility function - just returns model name"""
    return MODEL_NAME


def load_llm1(api_key=None):
    """Compatibility function - just returns model name"""
    return MODEL_NAME


# ====================
# SCHEDULE GENERATION AND PARSING FUNCTIONS
# ====================

import re
from datetime import datetime, timedelta
import json

def parse_schedule_to_activities(schedule_text, course_id, start_date=None):
    """
    Parse schedule.txt into individual activity records
    Returns: List of activity dicts
    """
    activities = []
    current_week = None
    day_counter = 0

    # Use provided start date or default to next Monday
    if start_date is None:
        from datetime import date, timedelta
        today = date.today()
        # Find next Monday
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        start_date = today + timedelta(days=days_until_monday)

    # Convert to datetime if it's a date object
    if hasattr(start_date, 'year') and not hasattr(start_date, 'hour'):
        start_date = datetime.combine(start_date, datetime.min.time())

    lines = schedule_text.split('\n')

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Week header: **Week 1 (September 1-7)** or Week 1 (September 1-7)
        if 'Week' in line and '(' in line:
            week_match = re.search(r'Week\s*(\d+)', line, re.IGNORECASE)
            if week_match:
                current_week = int(week_match.group(1))
                continue

        # Skip checkpoint sections
        if 'checkpoint' in line.lower() or 'test' in line.lower():
            continue
        if line.lower().startswith('questions:') or line.lower().startswith('solutions:'):
            continue

        # Day activity: "- Day 1: Introduction to Java (30 min)" or "Day 1: ..."
        day_match = re.search(r'[-•]?\s*Day\s*(\d+):\s*(.+)', line, re.IGNORECASE)
        if day_match and current_week:
            day_counter += 1
            day_num_in_line = int(day_match.group(1))
            activity_text = day_match.group(2).strip()

            # Calculate scheduled date
            scheduled_date = start_date + timedelta(days=day_counter - 1)
            day_of_week = ((day_counter - 1) % 7) + 1

            # Parse duration from text (e.g., "30 min", "1 hour", "45 min")
            duration = extract_duration(activity_text)

            # Determine activity type
            activity_type = 'study'
            if 'review' in activity_text.lower():
                activity_type = 'review'
            elif 'practice' in activity_text.lower() or 'exercise' in activity_text.lower():
                activity_type = 'practice'
            elif 'test' in activity_text.lower() or 'quiz' in activity_text.lower():
                activity_type = 'checkpoint'

            activities.append({
                'course_id': course_id,
                'week_number': current_week,
                'day_number': day_counter,
                'day_of_week': day_of_week,
                'scheduled_date': scheduled_date.date(),
                'title': line.strip().lstrip('-•').strip(),
                'description': None,
                'duration_minutes': duration,
                'activity_type': activity_type
            })

    return activities


def extract_duration(activity_text):
    """
    Extract duration in minutes from activity text
    Examples: "30 min", "1 hour", "45 min", "1.5 hours"
    Returns duration in minutes
    """
    # Look for patterns like "30 min", "1 hour", "45 minutes", etc.

    # Check for hours first
    hour_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:hour|hr)s?', activity_text, re.IGNORECASE)
    if hour_match:
        hours = float(hour_match.group(1))
        return int(hours * 60)

    # Check for minutes
    min_match = re.search(r'(\d+)\s*(?:min|minute)s?', activity_text, re.IGNORECASE)
    if min_match:
        return int(min_match.group(1))

    # Default to 45 minutes if no duration found
    return 45


def generate_task_content(task_title, task_type, study_guide_summary, model):
    """
    Generate specific content for a task (theory or test)

    Args:
        task_title: The title of the task
        task_type: 'study', 'review', 'practice', 'test', 'checkpoint'
        study_guide_summary: Summary of the course study guide
        model: The model to use for generation

    Returns:
        dict with 'theory_content', 'test_questions', 'test_solutions'
    """

    if task_type in ['test', 'checkpoint']:
        # Generate test questions and solutions
        prompt = f"""Based on this course material, create a focused test for: {task_title}

Study Guide Context:
{study_guide_summary}

Create 5 questions about this topic. For each question:
1. Make it specific and test understanding
2. Include multiple choice or short answer format
3. Provide a detailed solution explaining the answer

Return in this JSON format:
{{
    "questions": [
        {{"question": "Question text here?", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "correct": "A"}},
        ...
    ],
    "solutions": [
        {{"question_num": 1, "answer": "A", "explanation": "Detailed explanation..."}},
        ...
    ]
}}"""

        response = chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"max_tokens": 2000, "temperature": 0.7}
        )

        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                test_data = json.loads(response[json_start:json_end])
                return {
                    'theory_content': None,
                    'test_questions': json.dumps(test_data.get('questions', [])),
                    'test_solutions': json.dumps(test_data.get('solutions', []))
                }
        except:
            pass

        # Fallback: return raw text
        return {
            'theory_content': None,
            'test_questions': response,
            'test_solutions': "See questions above"
        }

    else:
        # Generate theory content for study tasks in steps
        prompt = f"""Based on this course material, create step-by-step study content for: {task_title}

Study Guide Context:
{study_guide_summary}

Break the content into 4-6 digestible steps. Each step should be concise (100-150 words).

Return in this JSON format:
{{
    "steps": [
        {{
            "title": "Step title (e.g., 'Introduction', 'Key Concept', 'Example')",
            "content": "Detailed explanation for this step...",
            "type": "theory"
        }},
        {{
            "title": "Step title",
            "content": "Detailed explanation...",
            "type": "example"
        }},
        {{
            "title": "Practice Question",
            "content": "A simple practice question to test understanding",
            "type": "practice"
        }}
    ]
}}

The last step should be a practice question or key takeaway."""

        response = chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"max_tokens": 1500, "temperature": 0.7}
        )

        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                theory_data = json.loads(response[json_start:json_end])
                return {
                    'theory_content': json.dumps(theory_data),
                    'test_questions': None,
                    'test_solutions': None
                }
        except:
            pass

        # Fallback: create a simple single-step structure
        return {
            'theory_content': json.dumps({
                "steps": [
                    {
                        "title": "Study Material",
                        "content": response,
                        "type": "theory"
                    }
                ]
            }),
            'test_questions': None,
            'test_solutions': None
        }