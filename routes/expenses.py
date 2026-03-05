from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
from database import get_db_connection
import calendar

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/')
def expenses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM expense_categories ORDER BY name")
    categories = cursor.fetchall()
    
    today = date.today()
    cursor.execute("""
        SELECT e.*, c.name as category_name 
        FROM expenses e
        JOIN expense_categories c ON e.category_id = c.id
        WHERE e.expense_date = %s
        ORDER BY e.created_at DESC
    """, (today,))
    today_expenses = cursor.fetchall()
    
    cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE expense_date = %s", (today,))
    today_total = cursor.fetchone()['total'] or 0
    
    cursor.close()
    conn.close()
    
    return render_template('expenses.html', categories=categories, today_expenses=today_expenses, today_total=today_total, today=today)

@expenses_bp.route('/add', methods=['POST'])
def add_expense():
    category_id = request.form['category_id']
    description = request.form['description']
    amount = request.form['amount']
    expense_date = request.form['expense_date']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (category_id, description, amount, expense_date) VALUES (%s, %s, %s, %s)",
                   (category_id, description, amount, expense_date))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Expense added successfully!', 'success')
    return redirect(url_for('expenses.expenses'))

@expenses_bp.route('/delete/<int:expense_id>')
def delete_expense(expense_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expenses.expenses'))

@expenses_bp.route('/calendar')
def expense_calendar():
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    days_in_month = calendar.monthrange(year, month)[1]
    cursor.execute("""
        SELECT expense_date, SUM(amount) as total
        FROM expenses
        WHERE YEAR(expense_date) = %s AND MONTH(expense_date) = %s
        GROUP BY expense_date
    """, (year, month))
    
    daily_totals = {str(row['expense_date']): float(row['total']) for row in cursor.fetchall()}
    
    cursor.execute("""
        SELECT SUM(amount) as monthly_total
        FROM expenses
        WHERE YEAR(expense_date) = %s AND MONTH(expense_date) = %s
    """, (year, month))
    monthly_total = cursor.fetchone()['monthly_total'] or 0
    
    cursor.close()
    conn.close()
    
    month_dates = [date(year, month, day) for day in range(1, days_in_month + 1)]
    
    return render_template('expense_calendar.html', month_dates=month_dates, daily_totals=daily_totals, 
                         year=year, month=month, month_name=calendar.month_name[month], monthly_total=monthly_total)

@expenses_bp.route('/day/<expense_date>')
def day_expenses(expense_date):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT e.*, c.name as category_name 
        FROM expenses e
        JOIN expense_categories c ON e.category_id = c.id
        WHERE e.expense_date = %s
        ORDER BY e.created_at DESC
    """, (expense_date,))
    expenses = cursor.fetchall()
    
    cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE expense_date = %s", (expense_date,))
    total = cursor.fetchone()['total'] or 0
    
    cursor.close()
    conn.close()
    
    return render_template('day_expenses.html', expenses=expenses, total=total, expense_date=expense_date)

@expenses_bp.route('/categories')
def manage_categories():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM expense_categories ORDER BY name")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('expense_categories.html', categories=categories)

@expenses_bp.route('/categories/add', methods=['POST'])
def add_category():
    name = request.form['name']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expense_categories (name) VALUES (%s)", (name,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Category added successfully!', 'success')
    return redirect(url_for('expenses.manage_categories'))

@expenses_bp.route('/categories/delete/<int:category_id>')
def delete_category(category_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expense_categories WHERE id = %s", (category_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('expenses.manage_categories'))
