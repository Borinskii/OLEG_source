# O.L.E.G. - Organizational Learning & Educational Guide

An AI-powered educational platform that generates personalized study courses with daily lessons, interactive practice questions, progress tracking, and comprehensive study guides.

![O.L.E.G. Interface](static/icon.png)

## Features

### Learning Interface
- **Duolingo-Style Calendar** - Interactive calendar showing your daily study schedule
- **Daily Lessons** - Step-by-step learning content for each day (Coursera/Stepik-style)
- **Interactive Practice** - Answer practice questions and get instant AI feedback
- **Test Days** - Special test days marked on calendar with checkpoint assessments
- **Progress Tracking** - Visual tracking of completed days and overall progress
- **Streak System** - Track your current streak, longest streak, and study consistency

### Course Creation
- **AI-Powered Conversations** - Chat with OLEG to describe what you want to learn
- **Flexible Duration** - Choose 4, 8, or 20-week study plans
- **Comprehensive Study Guides** - Automatically generated guides with:
  - Clear definitions and explanations
  - Theoretical foundations
  - Practical applications
  - Key terms and concepts
  - Curated resources
- **Daily Study Schedules** - Personalized daily study plans (max 1 hour/day)
- **Checkpoint Tests** - Regular assessments with detailed solutions
- **PDF Upload Support** - Upload course materials for AI analysis

### User Experience
- **User Authentication** - Secure login and registration system
- **Interactive Course Chat** - Ask OLEG questions about course material anytime
- **Auto-Generated Content** - Theory and test content generated on-demand for each day
- **Organized Study Guide** - Collapsible accordion structure for easy navigation
- **Responsive Design** - Works on desktop and mobile devices
- **Modern UI** - Clean interface with smooth animations

## Demo

### Creating a Course
1. Register an account or log in
2. Click "Create New Course"
3. Tell OLEG what you want to learn (e.g., "I want to learn Machine Learning")
4. Select course duration (4, 8, or 20 weeks)
5. Upload any relevant materials (optional)
6. Click "Finish Course"
7. Get your complete study guide and daily schedule

### Using the Learning Interface
1. Open a course to view the calendar
2. Click on any day to view that day's lesson
3. Read through lesson steps using Previous/Next buttons
4. Answer practice questions and get feedback from OLEG
5. Complete all steps to mark the day as done
6. Track your progress, streaks, and statistics

### Example Courses
- Database Systems
- Machine Learning
- Web Development
- Data Structures
- Digital Marketing
- Python Programming
- Any topic you want

## Tech Stack

### Backend
- **Framework:** Flask (Python 3.8+)
- **Database:** SQLite with SQLAlchemy-style models
- **AI Model:** Llama 3.3 70B Instruct (via Fireworks AI)
- **Authentication:** Flask-Login with password hashing
- **Session Management:** Flask-Session (filesystem-based)
- **PDF Processing:** PyPDF2

### Frontend
- **HTML5 & CSS3** - Responsive layouts with CSS Grid/Flexbox
- **JavaScript** - jQuery for DOM manipulation and AJAX
- **UI Components** - Custom accordion, calendar, and modal components

### Database Schema
- **Users** - User accounts with authentication
- **Courses** - Course metadata and study guides
- **Activities** - Daily tasks with theory/test content
- **Activity Completions** - Track completed activities
- **Streaks** - User study streaks and statistics
- **Daily Progress** - Day-level completion tracking

## Prerequisites

- Python 3.8 or higher
- Fireworks AI API key ([Get one here](https://fireworks.ai))
- Modern web browser

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Borinskii/OLEG_source.git
cd OLEG_source
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:
```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your Fireworks AI API key:
```
FIREWORKS_API_KEY=your_actual_api_key_here
```

**Get your API key:**
1. Sign up at [fireworks.ai](https://fireworks.ai)
2. Go to your account settings
3. Generate a new API key
4. Copy and paste it into `.env`

### 5. Initialize Database

Run the migration script to set up the database:
```bash
python migrate_db.py
```

This creates `oleg.db` with all necessary tables.

### 6. Create Required Directories
```bash
mkdir uploads flask_session
```

### 7. Run the Application
```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

## Usage Guide

### First Time Setup

1. **Register Account**
   - Navigate to `http://127.0.0.1:5000`
   - Click "Register"
   - Create your account with username and password
   - Log in with your credentials

### Creating Your First Course

1. **Start a New Course**
   - Click the "Create New Course" button on the home page
   - The chat interface will open

2. **Describe Your Course**
   ```
   Examples:
   - "I want to learn Python programming"
   - "Create a course on Digital Marketing"
   - "I need to study Database Management Systems"
   ```

3. **Select Duration**
   - Choose 4 weeks (intensive), 8 weeks (moderate), or 20 weeks (comprehensive)
   - The schedule will be adjusted based on your selection

4. **Upload Materials (Optional)**
   - Click the upload icon
   - Select PDF files with course content
   - OLEG will analyze and incorporate them into the study guide

5. **Finish Course Creation**
   - Click "Finish Course" button
   - Wait while OLEG generates:
     - Comprehensive study guide with topics and resources
     - Daily schedule parsed into individual activities
     - Course structure with theory and test days

### Daily Learning Workflow

1. **View Calendar**
   - Open your course to see the calendar interface
   - Days are color-coded:
     - White: Not started
     - Yellow: In progress
     - Green: Completed
     - Yellow with test marker: Test day

2. **Start Daily Lesson**
   - Click on a day to load the lesson
   - Read the lesson title and overview
   - Use the "Ask OLEG" button for questions

3. **Navigate Through Steps**
   - Read each step carefully
   - Use Previous/Next buttons to move between steps
   - Steps include theory, examples, and practice questions

4. **Answer Practice Questions**
   - Type your answer in the text area
   - Click "Check with OLEG"
   - Receive instant feedback on your answer

5. **Complete the Day**
   - Finish all steps
   - Click "Complete Day" button
   - See your updated streak and progress

### Taking Tests

1. **Identify Test Days**
   - Test days show a test marker on the calendar
   - Usually scheduled at the end of each week

2. **Complete Test**
   - Read all questions carefully
   - Review the provided solutions
   - Use test content to assess your understanding

### Tracking Progress

- **Current Streak** - Consecutive days studied
- **Longest Streak** - Best streak achieved
- **Days Studied** - Total number of days completed
- **Progress Percentage** - Overall course completion

### Managing Courses

- **View Study Guide** - Expand "Reference Study Guide" to view comprehensive material
- **View Full Schedule** - Expand "Full Study Schedule" to see the entire plan
- **Delete Course** - Use delete button on home page (requires confirmation)

## Project Structure

```
OLEG_source/
├── app.py                      # Main Flask application with routes
├── funcs.py                    # AI/API functions and content generation
├── db.py                       # Database operations and queries
├── models.py                   # Database models (User, Course, Activity, etc.)
├── auth.py                     # Authentication routes and logic
├── schema.sql                  # Database schema definitions
├── migrate_db.py               # Database migration script
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (DO NOT COMMIT)
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── static/                    # Static assets
│   ├── style.css             # Main chat styles
│   ├── chat.css              # Course creation chat styles
│   ├── course.css            # Course page and calendar styles
│   ├── auth.css              # Login/register page styles
│   ├── mobile.css            # Home page styles
│   ├── icon.png              # OLEG logo
│   ├── add_image.png         # Add button icon
│   └── load_file.png         # Upload icon
├── templates/                 # HTML templates
│   ├── index.html            # Home page with course list
│   ├── new_course.html       # Course creation chat interface
│   ├── course_template.html  # Daily lesson interface
│   ├── login.html            # Login page
│   └── register.html         # Registration page
├── uploads/                   # Uploaded PDF files (gitignored)
├── flask_session/            # Session data (gitignored)
├── oleg.db                   # SQLite database (gitignored)
└── schedule.txt              # Temporary schedule files (gitignored)
```

## Database Schema

### Users
- `id` - Primary key
- `username` - Unique username
- `password_hash` - Hashed password

### Courses
- `id` - Primary key
- `user_id` - Foreign key to users
- `name` - Course name
- `study_guide` - Generated study guide content
- `schedule_data` - Full schedule text
- `duration_weeks` - Course duration (4, 8, or 20)
- `start_date` - Course start date
- `created_at` - Creation timestamp

### Activities
- `id` - Primary key
- `course_id` - Foreign key to courses
- `week_number` - Week in schedule
- `day_number` - Overall day number
- `day_of_week` - Day of week (1-7)
- `scheduled_date` - When activity is scheduled
- `title` - Activity title
- `description` - Activity description
- `duration_minutes` - Expected duration
- `activity_type` - Type (study, practice, test, checkpoint)
- `theory_content` - Generated theory content (JSON)
- `test_questions` - Generated test questions (JSON)
- `test_solutions` - Test solutions (JSON)
- `content_generated` - Whether content has been generated

### Activity Completions
- `id` - Primary key
- `activity_id` - Foreign key to activities
- `completed_at` - Completion timestamp
- `notes` - Optional notes

### Streaks
- `id` - Primary key
- `user_id` - Foreign key to users
- `course_id` - Foreign key to courses
- `current_streak` - Current consecutive days
- `longest_streak` - Best streak achieved
- `total_study_days` - Total days studied
- `last_study_date` - Last activity date

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FIREWORKS_API_KEY` | Your Fireworks AI API key | Yes |

### Customization Options

**Course Duration:**
- Modify duration options in `templates/new_course.html`
- Adjust schedule generation logic in `funcs.py`

**AI Prompts:**
- Study guide generation: `app.py` - `generate_study_guide()`
- Schedule generation: `app.py` - `generate_complete_schedule()`
- Content generation: `funcs.py` - `generate_task_content()`

**UI Styling:**
- Calendar colors: `static/course.css` - `.calendar-day` classes
- Theme colors: `static/course.css` - `:root` variables

## API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /register` - Registration page
- `POST /register` - Process registration
- `GET /logout` - Logout user

### Course Management
- `GET /` - Home page with course list
- `GET /new_course` - Course creation interface
- `POST /send` - Chat with OLEG
- `POST /finish` - Complete course creation
- `GET /course/<id>` - View course page
- `POST /delete_course/<id>` - Delete course

### Calendar & Lessons
- `GET /api/course/<id>/info` - Get course metadata
- `GET /api/course/<id>/calendar/<year>/<month>` - Get calendar data
- `GET /api/course/<id>/daily-lesson/<date>` - Get daily lesson content
- `GET /api/course/<id>/statistics` - Get progress stats

### Progress Tracking
- `POST /api/course/<id>/task/<task_id>/complete` - Mark activity complete
- `POST /api/course/<id>/task/<task_id>/incomplete` - Mark activity incomplete

## Cost Estimation

Approximate costs using Fireworks AI (Llama 3.3 70B):

| Operation | Tokens | Estimated Cost |
|-----------|--------|----------------|
| Course name extraction | ~50 | ~$0.001 |
| Study guide generation | ~4,000 | ~$0.02 |
| Schedule generation | ~8,000 | ~$0.04 |
| Daily content generation | ~1,500 | ~$0.008 |
| Chat message | ~500 | ~$0.003 |
| Practice feedback | ~800 | ~$0.004 |
| **Per Course (20 weeks)** | ~150,000 | ~$0.75 |

Note: Content is generated on-demand, so actual costs depend on usage.

*Prices may vary. Check [Fireworks AI pricing](https://fireworks.ai/pricing) for current rates.*

## Performance Optimizations

- **Lazy Content Generation** - Theory and tests generated only when accessed
- **Context Limiting** - Only last 10 messages used for chat context
- **Streaming Responses** - Automatic for responses over 5000 tokens
- **Database Indexing** - Optimized queries for calendar and progress
- **Session Caching** - Reduced database queries for user data
- **PDF Chunking** - Only first 3000 characters processed from uploads

## Features Comparison

### Previously Limited (Now Implemented)
- User authentication and accounts
- Database integration (SQLite)
- Progress tracking with streaks
- Interactive daily lessons
- Step-by-step learning interface
- Practice question feedback
- Calendar-based navigation

### Still In Development
- Export to PDF/Google Calendar/iCal
- Mobile app (web is responsive)
- Video content integration
- Spaced repetition algorithms
- Social features (share courses)
- Multiple AI model options

## Known Issues

- Content generation can take 5-10 seconds for complex topics
- Large PDFs (over 100 pages) may timeout during upload
- Session data persists indefinitely (manual cleanup required)
- Calendar navigation may be slow with many courses
- Streak calculation assumes daily study (doesn't account for rest days)

## Troubleshooting

### Database Issues
```bash
# Reset database
rm oleg.db
python migrate_db.py
```

### Content Not Generating
- Check Fireworks AI API key in `.env`
- Verify internet connection
- Check console for error messages
- Refresh the page and try again

### Login Issues
- Clear browser cookies and cache
- Check database exists: `ls oleg.db`
- Verify Flask session directory: `ls flask_session/`

## Contributing

Contributions are welcome! Areas for improvement:

1. **Backend**
   - Add database connection pooling
   - Implement caching layer (Redis)
   - Add API rate limiting
   - Improve error handling

2. **Frontend**
   - Add keyboard shortcuts
   - Implement dark mode toggle
   - Improve mobile responsiveness
   - Add loading skeletons

3. **Features**
   - Export functionality
   - Calendar integrations
   - Achievement system
   - Study reminders

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Fireworks AI](https://fireworks.ai) for providing the Llama 3.3 70B API
- [Flask](https://flask.palletsprojects.com/) for the web framework
- Inspired by Duolingo, Coursera, and Stepik learning platforms
- Community feedback and contributions

## Support

If you find this project helpful, please give it a star on GitHub!

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section

---

*Last Updated: January 2026*
