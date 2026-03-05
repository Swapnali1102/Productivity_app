from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, date, timedelta
import mysql.connector
from database import get_db_connection

goals_bp = Blueprint('goals', __name__)

@goals_bp.route('/')
def goals():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM goals 
        ORDER BY 
            CASE status 
                WHEN 'Active' THEN 1 
                WHEN 'Completed' THEN 2 
                WHEN 'Dropped' THEN 3 
            END,
            target_date ASC
    """)
    goals = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('goals.html', goals=goals, today=date.today())

@goals_bp.route('/add', methods=['POST'])
def add_goal():
    name = request.form['name']
    description = request.form['description']
    target_date = request.form.get('target_date') or None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO goals (name, description, target_date)
        VALUES (%s, %s, %s)
    """, (name, description, target_date))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Goal added successfully!', 'success')
    return redirect(url_for('goals.goals'))

@goals_bp.route('/update/<int:goal_id>', methods=['POST'])
def update_goal(goal_id):
    name = request.form['name']
    description = request.form['description']
    target_date = request.form.get('target_date') or None
    status = request.form['status']
    progress = int(request.form['progress'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE goals 
        SET name = %s, description = %s, target_date = %s, 
            status = %s, progress_percentage = %s
        WHERE id = %s
    """, (name, description, target_date, status, progress, goal_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Goal updated successfully!', 'success')
    return redirect(url_for('goals.goals'))

@goals_bp.route('/delete/<int:goal_id>')
def delete_goal(goal_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM goals WHERE id = %s", (goal_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Goal deleted successfully!', 'success')
    return redirect(url_for('goals.goals'))