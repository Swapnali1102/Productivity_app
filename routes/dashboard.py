from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, date, timedelta
import mysql.connector
from database import get_db_connection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    
    cursor = conn.cursor(dictionary=True)
    today = date.today()
    
    # Get today's tasks
    cursor.execute("""
        SELECT t.*, tc.completed 
        FROM tasks t 
        LEFT JOIN task_completions tc ON t.id = tc.task_id AND tc.completion_date = %s
        WHERE t.is_active = TRUE
        ORDER BY t.priority DESC, t.time_fixed
    """, (today,))
    tasks = cursor.fetchall()
    
    # Calculate completion percentage
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task['completed'])
    completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Get current streaks
    cursor.execute("""
        SELECT t.name, COUNT(*) as current_streak
        FROM tasks t
        JOIN task_completions tc ON t.id = tc.task_id
        WHERE tc.completed = TRUE AND tc.completion_date >= %s
        GROUP BY t.id, t.name
    """, (today - timedelta(days=30),))
    streaks = cursor.fetchall()
    
    # Get today's diary entry status
    cursor.execute("SELECT id FROM diary_entries WHERE entry_date = %s", (today,))
    diary_exists = cursor.fetchone() is not None
    
    # Get focus sessions today
    cursor.execute("SELECT COUNT(*) as sessions FROM focus_sessions WHERE session_date = %s AND completed = TRUE", (today,))
    focus_sessions = cursor.fetchone()['sessions']
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', 
                         tasks=tasks,
                         completion_percentage=round(completion_percentage, 1),
                         streaks=streaks,
                         diary_exists=diary_exists,
                         focus_sessions=focus_sessions,
                         today=today)

@dashboard_bp.route('/toggle_task', methods=['POST'])
def toggle_task():
    task_id = request.json.get('task_id')
    completed = request.json.get('completed')
    today = date.today()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if completed:
        cursor.execute("""
            INSERT INTO task_completions (task_id, completion_date, completed, completed_at)
            VALUES (%s, %s, TRUE, NOW())
            ON DUPLICATE KEY UPDATE completed = TRUE, completed_at = NOW()
        """, (task_id, today))
    else:
        cursor.execute("""
            INSERT INTO task_completions (task_id, completion_date, completed)
            VALUES (%s, %s, FALSE)
            ON DUPLICATE KEY UPDATE completed = FALSE, completed_at = NULL
        """, (task_id, today))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True})