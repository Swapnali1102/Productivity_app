from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, timedelta
import mysql.connector
from database import get_db_connection
import calendar

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/')
def tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all active tasks
    cursor.execute("SELECT * FROM tasks WHERE is_active = TRUE ORDER BY priority DESC, name")
    tasks = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('tasks.html', tasks=tasks)

@tasks_bp.route('/add', methods=['POST'])
def add_task():
    name = request.form['name']
    category = request.form['category']
    priority = request.form['priority']
    time_fixed = request.form.get('time_fixed') or None
    duration = request.form.get('duration_minutes') or None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO tasks (name, category, priority, time_fixed, duration_minutes)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, category, priority, time_fixed, duration))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Task added successfully!', 'success')
    return redirect(url_for('tasks.tasks'))

@tasks_bp.route('/edit/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    name = request.form['name']
    category = request.form['category']
    priority = request.form['priority']
    time_fixed = request.form.get('time_fixed') or None
    duration = request.form.get('duration_minutes') or None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE tasks 
        SET name = %s, category = %s, priority = %s, time_fixed = %s, duration_minutes = %s
        WHERE id = %s
    """, (name, category, priority, time_fixed, duration, task_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Task updated successfully!', 'success')
    return redirect(url_for('tasks.tasks'))

@tasks_bp.route('/delete/<int:task_id>')
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE tasks SET is_active = FALSE WHERE id = %s", (task_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks.tasks'))

@tasks_bp.route('/habit_grid')
def habit_grid():
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all active tasks
    cursor.execute("SELECT * FROM tasks WHERE is_active = TRUE ORDER BY name")
    tasks = cursor.fetchall()
    
    # Get days in month
    days_in_month = calendar.monthrange(year, month)[1]
    month_dates = [date(year, month, day) for day in range(1, days_in_month + 1)]
    
    # Get completions for the month
    cursor.execute("""
        SELECT task_id, completion_date, completed
        FROM task_completions
        WHERE completion_date >= %s AND completion_date <= %s
    """, (date(year, month, 1), date(year, month, days_in_month)))
    
    completions = {}
    for row in cursor.fetchall():
        key = f"{row['task_id']}_{row['completion_date']}"
        completions[key] = row['completed']
    
    cursor.close()
    conn.close()
    
    return render_template('habit_grid.html', 
                         tasks=tasks, 
                         month_dates=month_dates,
                         completions=completions,
                         year=year,
                         month=month,
                         month_name=calendar.month_name[month])

@tasks_bp.route('/toggle_completion', methods=['POST'])
def toggle_completion():
    task_id = request.json.get('task_id')
    completion_date = request.json.get('date')
    completed = request.json.get('completed')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO task_completions (task_id, completion_date, completed, completed_at)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE completed = %s, completed_at = %s
    """, (task_id, completion_date, completed, 
          datetime.now() if completed else None,
          completed, 
          datetime.now() if completed else None))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True})