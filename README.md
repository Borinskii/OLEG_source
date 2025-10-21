# 🎓 O.L.E.G. - Organizational Learning & Educational Guide

An AI-powered educational assistant that generates personalized study courses with comprehensive 20-week study plans, detailed study guides, and checkpoint assessments.

![O.L.E.G. Interface](static/icon.png)

## ✨ Features

- 🤖 **AI-Powered Conversations** - Chat with OLEG to describe what you want to learn
- 📚 **Comprehensive Study Guides** - Automatically generated guides with:
  - Clear definitions and explanations
  - Theoretical foundations
  - Practical applications
  - Key terms and concepts
  - Curated resources
- 📅 **20-Week Study Schedules** - Personalized daily study plans (max 1 hour/day)
- ✅ **Checkpoint Tests** - Regular assessments with detailed solutions
- 📄 **PDF Upload Support** - Upload course materials for AI analysis
- 💬 **Interactive Course Chat** - Ask questions about your courses anytime
- 🎨 **Modern UI** - Clean, dark-themed interface with smooth animations

## 🚀 Demo

### Creating a Course
1. Click "Create New Course"
2. Tell OLEG what you want to learn (e.g., "I want to learn Machine Learning")
3. Upload any relevant materials (optional)
4. Click "Finish Course"
5. Get your complete study guide and 20-week schedule!

### Example Courses
- Database Systems
- Machine Learning
- Web Development
- Data Structures
- Digital Marketing
- Any topic you want!

## 🛠️ Tech Stack

- **Backend:** Flask (Python 3.8+)
- **AI Model:** Llama 3.1 70B Instruct (via Fireworks AI)
- **Frontend:** HTML5, CSS3, JavaScript (jQuery)
- **Session Management:** Flask-Session (filesystem-based)
- **PDF Processing:** PyPDF2

## 📋 Prerequisites

- Python 3.8 or higher
- Fireworks AI API key ([Get one free here](https://fireworks.ai))
- Modern web browser

## 🔧 Installation

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

### 5. Create Required Directories
```bash
mkdir uploads flask_session
```

### 6. Run the Application
```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

## 📖 Usage Guide

### Creating Your First Course

1. **Start a New Course**
   - Click the "Create New Course" button
   - The chat interface will open

2. **Describe Your Course**
```
   Examples:
   - "I want to learn Python programming"
   - "Create a course on Digital Marketing"
   - "I need to study Database Management Systems"
```

3. **Upload Materials (Optional)**
   - Click the upload icon
   - Select PDF files with course content
   - OLEG will analyze and incorporate them

4. **Finish Course Creation**
   - Click "✓ FINISH COURSE" button
   - Wait while OLEG generates:
     - Comprehensive study guide
     - 20-week daily schedule
     - Checkpoint tests with solutions

5. **Access Your Course**
   - Course appears on home page
   - Click to view study guide
   - Check `schedule.txt` for detailed schedule


### Chatting with OLEG During Study

1. Open any course
2. Click "🎓 Ask OLEG" button
3. Ask questions about the course material
4. Get instant AI-powered explanations

### Managing Courses

- **View All:** All courses listed on home page
- **Delete All:** Click "🗑️ Clear All Courses" (requires confirmation)

## 📁 Project Structure
```
OLEG_source/
├── app.py                      # Main Flask application
├── funcs.py                    # AI/API helper functions
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (DO NOT COMMIT)
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── static/                    # Static assets
│   ├── style.css             # Main chat styles
│   ├── mobile.css            # Home page styles
│   ├── style_course.css      # Course page styles
│   ├── icon.png              # OLEG logo
│   ├── add_image.png         # Add button icon
│   └── load_file.png         # Upload icon
├── templates/                 # HTML templates
│   ├── index.html            # Home page
│   ├── new_course.html       # Course creation chat
│   └── course_template.html  # Course display page
├── uploads/                   # Uploaded PDF files (gitignored)
├── flask_session/            # Session data (gitignored)
└── schedule.txt              # Generated schedules (gitignored)
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FIREWORKS_API_KEY` | Your Fireworks AI API key | Yes |

### Customization

You can customize AI behavior in `app.py`:

**Study Guide Format:**
```python
def generate_study_guide(chat_history):
    # Modify the prompt to change structure
```

**Schedule Length:**
```python
def generate_complete_schedule(study_guide):
    # Change "20 weeks" to any duration
```

## 💰 Cost Estimation

Approximate costs using Fireworks AI (Llama 3.1 70B):

| Operation | Tokens | Cost |
|-----------|--------|------|
| Course name extraction | ~50 | ~$0.001 |
| Study guide generation | ~4,000 | ~$0.02 |
| Schedule generation | ~8,000 | ~$0.04 |
| Chat message | ~500 | ~$0.003 |
| **Per Course** | **~12,000** | **~$0.06** |

*Prices may vary. Check [Fireworks AI pricing](https://fireworks.ai/pricing) for current rates.*

## 🎯 Performance Optimizations

- **Context Limiting:** Only last 10 messages used for chat context
- **Token Efficiency:** Chat history capped at 20 messages
- **Streaming Responses:** Automatic for responses >5000 tokens
- **Single API Calls:** Entire 20-week schedule generated in one request
- **PDF Chunking:** Only first 3000 characters processed

## ⚠️ Limitations

- Single-user application (no authentication)
- Sessions stored on filesystem (not database)
- Schedules saved as text files only
- No progress tracking
- No mobile app (web-only)
- Limited to text/PDF inputs

## 🔮 Future Enhancements

- [ ] User authentication & multi-user support
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Export to PDF/Google Calendar/iCal
- [ ] Progress tracking & completion badges
- [ ] Mobile app (React Native)
- [ ] Video content integration
- [ ] Spaced repetition algorithms
- [ ] Social features (share courses)
- [ ] Premium AI models option

## 🤝 Contributing

Contributions are welcome! This is a prototype, so there's lots of room for improvement.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Known Issues

- Session data persists indefinitely (no cleanup)
- Large PDFs may timeout
- No input validation for course names
- Chat history not saved between sessions

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Fireworks AI](https://fireworks.ai) for providing the Llama 3.1 70B API
- [Flask](https://flask.palletsprojects.com/) for the web framework
- Inspired by modern educational technology and AI assistants


## ⭐ Show Your Support

If you find this project helpful, please give it a star on GitHub!

---

*Last Updated: January 2025*
