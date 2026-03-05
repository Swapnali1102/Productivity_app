# Personal Productivity & Discipline Tracker

A comprehensive web application built with Flask and MySQL to help track daily habits, maintain streaks, monitor productivity, and write daily diary entries for self-improvement and discipline building.

## 🚀 Features

### 🏠 Dashboard
- Today's date and task overview
- Real-time completion percentage
- Current streaks display
- Quick access to diary and timer
- Focus session counter

### ✅ Daily Task & Habit Manager
- Add/edit/delete tasks with categories and priorities
- Set fixed times or durations
- Monthly habit tracking grid (calendar view)
- Streak tracking and statistics
- Task completion analytics

### 📓 Daily Diary / Journal
- Write and edit daily entries
- Mood tracking with each entry
- Search functionality across all entries
- Word count tracking
- Writing prompts for inspiration

### 🔥 Streaks & Analytics
- Current and longest streak tracking
- Weekly/monthly performance graphs
- Habit completion heatmaps
- Productivity trend analysis
- Mood vs productivity correlation

### 🎯 Goal Setting
- Create and track personal goals
- Progress visualization
- Target date tracking
- Status management (Active/Completed/Dropped)

### ⏳ Focus Timer (Pomodoro)
- 25-minute focus sessions with breaks
- Link sessions to specific tasks
- Daily session tracking
- Browser notifications

### 🌙 Daily Status Tracker
- Mood logging (Happy, Neutral, Sad, Excited, Stressed)
- Energy level tracking (1-5 scale)
- Stress level monitoring (1-5 scale)
- Correlation with productivity data

## 🛠 Technology Stack

- **Backend**: Python 3.8+ with Flask
- **Database**: MySQL 8.0+
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS with responsive design
- **Icons**: Font Awesome 6.0

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd productivity_app
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup

#### Create MySQL Database
```sql
-- Connect to MySQL as root
mysql -u root -p

-- Create database
CREATE DATABASE productivity_tracker;
```

#### Import Database Schema
```bash
mysql -u root -p productivity_tracker < database_schema.sql
```

### 4. Configure Database Connection

Edit `app.py` and update the database configuration:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',  # Change this
    'database': 'productivity_tracker'
}
```

### 5. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
productivity_app/
├── app.py                 # Main Flask application
├── database_schema.sql    # MySQL database schema
├── requirements.txt       # Python dependencies
├── routes/               # Route handlers
│   ├── dashboard.py      # Dashboard functionality
│   ├── tasks.py          # Task management
│   ├── diary.py          # Diary/journal features
│   ├── analytics.py      # Analytics and reports
│   ├── goals.py          # Goal setting
│   └── timer.py          # Focus timer & daily status
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── dashboard.html    # Dashboard page
│   ├── tasks.html        # Task management
│   ├── habit_grid.html   # Monthly habit grid
│   ├── diary.html        # Diary listing
│   └── write_diary.html  # Diary editor
└── static/              # Static assets
    ├── css/
    │   └── style.css     # Main stylesheet
    └── js/
        └── main.js       # JavaScript functionality
```

## 🎯 Usage Guide

### Getting Started
1. **Dashboard**: Start here to see today's overview
2. **Add Tasks**: Go to Tasks → Add your daily habits
3. **Track Habits**: Use the Habit Grid to mark completions
4. **Write Diary**: Document your daily thoughts and mood
5. **Set Goals**: Define your long-term objectives
6. **Use Timer**: Focus on tasks with Pomodoro sessions

### Daily Workflow
1. Check dashboard for today's tasks
2. Complete tasks and mark them as done
3. Use focus timer for concentrated work
4. Log daily status (mood, energy, stress)
5. Write diary entry reflecting on the day
6. Review analytics to track progress

## 🔍 Key Database Queries

### Get Current Streaks
```sql
SELECT t.name, COUNT(*) as current_streak
FROM tasks t
JOIN task_completions tc ON t.id = tc.task_id
WHERE tc.completed = TRUE 
AND tc.completion_date >= CURDATE() - INTERVAL 30 DAY
GROUP BY t.id, t.name;
```

### Weekly Completion Rate
```sql
SELECT 
    DATE(tc.completion_date) as date,
    COUNT(CASE WHEN tc.completed = TRUE THEN 1 END) as completed,
    COUNT(tc.id) as total,
    ROUND(COUNT(CASE WHEN tc.completed = TRUE THEN 1 END) / COUNT(tc.id) * 100, 1) as percentage
FROM task_completions tc
JOIN tasks t ON tc.task_id = t.id
WHERE tc.completion_date >= CURDATE() - INTERVAL 7 DAY
AND t.is_active = TRUE
GROUP BY DATE(tc.completion_date)
ORDER BY tc.completion_date;
```

### Mood vs Productivity Correlation
```sql
SELECT 
    ds.mood,
    AVG(daily_completion.completion_rate) as avg_completion
FROM daily_status ds
JOIN (
    SELECT 
        tc.completion_date,
        AVG(CASE WHEN tc.completed = TRUE THEN 100 ELSE 0 END) as completion_rate
    FROM task_completions tc
    JOIN tasks t ON tc.task_id = t.id
    WHERE t.is_active = TRUE
    GROUP BY tc.completion_date
) daily_completion ON ds.status_date = daily_completion.completion_date
GROUP BY ds.mood;
```

## 🎨 Customization

### Adding New Task Categories
Edit the `tasks.py` route and database schema to add new categories:

```sql
ALTER TABLE tasks MODIFY COLUMN category ENUM('Health', 'Study', 'Work', 'Personal', 'Fitness', 'Reading') DEFAULT 'Personal';
```

### Changing Timer Duration
Modify the default duration in `timer.py`:

```python
duration = request.json.get('duration', 30)  # 30 minutes instead of 25
```

### Custom Mood Options
Update the mood enum in the database schema:

```sql
ALTER TABLE daily_status MODIFY COLUMN mood ENUM('Happy', 'Neutral', 'Sad', 'Excited', 'Stressed', 'Motivated', 'Tired') DEFAULT 'Neutral';
```

## 🔒 Security Notes

- Change the Flask secret key in `app.py`
- Use environment variables for database credentials
- Consider adding user authentication for multi-user deployment
- Implement input validation and sanitization

## 🚀 Deployment

For production deployment:

1. Use a production WSGI server (Gunicorn, uWSGI)
2. Configure a reverse proxy (Nginx, Apache)
3. Use environment variables for configuration
4. Set up SSL/TLS certificates
5. Configure database connection pooling
6. Implement proper logging

## 🤝 Contributing

This is a personal productivity application, but feel free to:
- Report bugs or issues
- Suggest new features
- Submit improvements
- Share your customizations

## 📄 License

This project is for personal use. Feel free to modify and adapt it to your needs.

## 🆘 Troubleshooting

### Common Issues

**Database Connection Error**
- Verify MySQL is running
- Check database credentials in `app.py`
- Ensure database exists and schema is imported

**Module Import Errors**
- Install all requirements: `pip install -r requirements.txt`
- Check Python version compatibility

**Static Files Not Loading**
- Verify Flask static folder configuration
- Check file paths in templates

**Timer Not Working**
- Enable browser notifications
- Check JavaScript console for errors

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the database schema
3. Examine browser console for JavaScript errors
4. Verify all dependencies are installed

---

**Happy tracking! 🎯 Stay disciplined and achieve your goals! 💪**