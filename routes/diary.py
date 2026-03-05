from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, timedelta
import mysql.connector
from database import get_db_connection

diary_bp = Blueprint('diary', __name__)

@diary_bp.route('/')
def diary():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get recent entries
    cursor.execute("""
        SELECT * FROM diary_entries 
        ORDER BY entry_date DESC 
        LIMIT 10
    """)
    entries = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('diary.html', entries=entries)

@diary_bp.route('/entry/<entry_date>')
def view_entry(entry_date):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM diary_entries WHERE entry_date = %s", (entry_date,))
    entry = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('diary_entry.html', entry=entry, entry_date=entry_date)

@diary_bp.route('/write', methods=['GET', 'POST'])
def write_entry():
    if request.method == 'POST':
        entry_date = request.form['entry_date']
        content = request.form['content']
        mood = request.form['mood']
        word_count = len(content.split())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO diary_entries (entry_date, content, mood, word_count)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            content = %s, mood = %s, word_count = %s, updated_at = NOW()
        """, (entry_date, content, mood, word_count, content, mood, word_count))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Diary entry saved successfully!', 'success')
        return redirect(url_for('diary.diary'))
    
    # GET request - show form
    selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    
    # Check if entry exists for this date
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM diary_entries WHERE entry_date = %s", (selected_date,))
    existing_entry = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('write_diary.html', 
                         selected_date=selected_date, 
                         existing_entry=existing_entry)

@diary_bp.route('/delete/<entry_date>')
def delete_entry(entry_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM diary_entries WHERE entry_date = %s", (entry_date,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Diary entry deleted successfully!', 'success')
    return redirect(url_for('diary.diary'))

@diary_bp.route('/search')
def search():
    query = request.args.get('q', '')
    
    if not query:
        return redirect(url_for('diary.diary'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM diary_entries 
        WHERE content LIKE %s 
        ORDER BY entry_date DESC
    """, (f'%{query}%',))
    
    entries = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('diary.html', entries=entries, search_query=query)