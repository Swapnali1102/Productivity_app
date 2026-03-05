from flask import Flask, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Import and register routes
with app.app_context():
    from routes.dashboard import dashboard_bp
    from routes.tasks import tasks_bp
    from routes.diary import diary_bp
    from routes.analytics import analytics_bp
    from routes.goals import goals_bp
    from routes.timer import timer_bp
    from routes.expenses import expenses_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(diary_bp, url_prefix='/diary')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(goals_bp, url_prefix='/goals')
    app.register_blueprint(timer_bp, url_prefix='/timer')
    app.register_blueprint(expenses_bp, url_prefix='/expenses')

@app.route('/')
def index():
    return redirect(url_for('dashboard.dashboard'))

if __name__ == '__main__':
    app.run(debug=True)