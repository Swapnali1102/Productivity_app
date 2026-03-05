-- Personal Productivity Tracker Database Schema

CREATE DATABASE IF NOT EXISTS productivity_tracker;
USE productivity_tracker;

-- Tasks table
CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category ENUM('Health', 'Study', 'Work', 'Personal') DEFAULT 'Personal',
    priority ENUM('Low', 'Medium', 'High') DEFAULT 'Medium',
    time_fixed TIME NULL,
    duration_minutes INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Task completions table
CREATE TABLE task_completions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    completion_date DATE NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    UNIQUE KEY unique_task_date (task_id, completion_date)
);

-- Diary entries table
CREATE TABLE diary_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entry_date DATE NOT NULL UNIQUE,
    content TEXT NOT NULL,
    mood ENUM('Happy', 'Neutral', 'Sad', 'Excited', 'Stressed') DEFAULT 'Neutral',
    word_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Goals table
CREATE TABLE goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    target_date DATE,
    status ENUM('Active', 'Completed', 'Dropped') DEFAULT 'Active',
    progress_percentage INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Focus sessions table
CREATE TABLE focus_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_date DATE NOT NULL,
    duration_minutes INT DEFAULT 25,
    task_id INT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
);

-- Daily status table
CREATE TABLE daily_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    status_date DATE NOT NULL UNIQUE,
    mood ENUM('Happy', 'Neutral', 'Sad', 'Excited', 'Stressed') DEFAULT 'Neutral',
    energy_level INT CHECK (energy_level BETWEEN 1 AND 5),
    stress_level INT CHECK (stress_level BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO tasks (name, category, priority, time_fixed) VALUES
('Morning Exercise', 'Health', 'High', '07:00:00'),
('Read for 30 minutes', 'Personal', 'Medium', NULL),
('Work on Project', 'Work', 'High', NULL);