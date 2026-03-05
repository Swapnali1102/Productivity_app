from flask import Blueprint, render_template, jsonify
from datetime import datetime, date, timedelta
import mysql.connector
from database import get_db_connection

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/')
def analytics():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get current streaks
    today = date.today()
    cursor.execute("""
        SELECT t.name, t.id,
               (SELECT COUNT(*) FROM task_completions tc 
                WHERE tc.task_id = t.id AND tc.completed = TRUE 
                AND tc.completion_date > (
                    SELECT COALESCE(MAX(tc2.completion_date), '1900-01-01')
                    FROM task_completions tc2 
                    WHERE tc2.task_id = t.id AND tc2.completed = FALSE 
                    AND tc2.completion_date < %s
                )) as current_streak,
               (SELECT MAX(streak_length) FROM (
                   SELECT COUNT(*) as streak_length
                   FROM task_completions tc3
                   WHERE tc3.task_id = t.id AND tc3.completed = TRUE
                   GROUP BY tc3.task_id
               ) as streaks) as longest_streak
        FROM tasks t 
        WHERE t.is_active = TRUE
    """, (today,))
    
    streaks = cursor.fetchall()
    
    # Get completion percentages
    cursor.execute("""
        SELECT t.name,
               COUNT(tc.id) as total_days,
               SUM(CASE WHEN tc.completed = TRUE THEN 1 ELSE 0 END) as completed_days,
               ROUND(SUM(CASE WHEN tc.completed = TRUE THEN 1 ELSE 0 END) / COUNT(tc.id) * 100, 1) as completion_rate
        FROM tasks t
        LEFT JOIN task_completions tc ON t.id = tc.task_id
        WHERE t.is_active = TRUE AND tc.completion_date >= %s
        GROUP BY t.id, t.name
    """, (today - timedelta(days=30),))
    
    completion_stats = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('analytics.html', 
                         streaks=streaks, 
                         completion_stats=completion_stats)

@analytics_bp.route('/weekly_data')
def weekly_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get last 7 days completion data
    today = date.today()
    week_start = today - timedelta(days=6)
    
    cursor.execute("""
        SELECT 
            DATE(tc.completion_date) as date,
            COUNT(CASE WHEN tc.completed = TRUE THEN 1 END) as completed,
            COUNT(tc.id) as total
        FROM task_completions tc
        JOIN tasks t ON tc.task_id = t.id
        WHERE tc.completion_date >= %s AND tc.completion_date <= %s
        AND t.is_active = TRUE
        GROUP BY DATE(tc.completion_date)
        ORDER BY tc.completion_date
    """, (week_start, today))
    
    data = cursor.fetchall()
    
    # Fill missing dates with 0
    date_range = [(week_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    result = []
    
    data_dict = {str(row['date']): row for row in data}
    
    for date_str in date_range:
        if date_str in data_dict:
            row = data_dict[date_str]
            percentage = (row['completed'] / row['total'] * 100) if row['total'] > 0 else 0
        else:
            percentage = 0
        
        result.append({
            'date': date_str,
            'percentage': round(percentage, 1)
        })
    
    cursor.close()
    conn.close()
    
    return jsonify(result)

@analytics_bp.route('/mood_productivity')
def mood_productivity():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
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
        GROUP BY ds.mood
    """)
    
    mood_data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify([{
        'mood': row['mood'],
        'completion_rate': round(row['avg_completion'], 1)
    } for row in mood_data])