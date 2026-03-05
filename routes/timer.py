from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, date, timedelta
import mysql.connector
from database import get_db_connection

timer_bp = Blueprint('timer', __name__)

@timer_bp.route('/')
def timer():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get active tasks for linking
    cursor.execute("SELECT id, name FROM tasks WHERE is_active = TRUE ORDER BY name")
    tasks = cursor.fetchall()
    
    # Get today's sessions
    today = date.today()
    cursor.execute("""
        SELECT fs.*, t.name as task_name
        FROM focus_sessions fs
        LEFT JOIN tasks t ON fs.task_id = t.id
        WHERE fs.session_date = %s
        ORDER BY fs.created_at DESC
    """, (today,))
    sessions = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('timer.html', tasks=tasks, sessions=sessions)

@timer_bp.route('/start_session', methods=['POST'])
def start_session():
    task_id = request.json.get('task_id')
    duration = request.json.get('duration', 25)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO focus_sessions (session_date, duration_minutes, task_id, completed)
        VALUES (%s, %s, %s, FALSE)
    """, (date.today(), duration, task_id if task_id else None))
    
    session_id = cursor.lastrowid
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'session_id': session_id})

@timer_bp.route('/complete_session', methods=['POST'])
def complete_session():
    session_id = request.json.get('session_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE focus_sessions 
        SET completed = TRUE 
        WHERE id = %s
    """, (session_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True})

@timer_bp.route('/daily_status', methods=['GET', 'POST'])
def daily_status():
    if request.method == 'POST':
        mood = request.form['mood']
        energy_level = int(request.form['energy_level'])
        stress_level = int(request.form['stress_level'])
        status_date = request.form.get('status_date', date.today())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO daily_status (status_date, mood, energy_level, stress_level)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            mood = %s, energy_level = %s, stress_level = %s
        """, (status_date, mood, energy_level, stress_level, mood, energy_level, stress_level))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
    
    # GET request
    today = date.today()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM daily_status WHERE status_date = %s", (today,))
    status = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('daily_status.html', status=status, today=today)