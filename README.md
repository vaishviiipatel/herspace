# HerSpace

A simple Flask web application for sharing posts with moderation features.

## Features

- User registration, login, and logout
- Three user roles: user, moderator, and admin
- Create text-only posts with categories
- Optional anonymous posting
- Rule-based moderation using keyword filtering
- Flagged posts visible only to moderators
- Moderator approval and rejection system
- Admin panel to manage users and roles
- SQLite database with automatic table creation

## Requirements

- Python 3
- Flask
- Works on 8GB RAM laptop
- Runs locally

## Installation

1. Make sure you have Python 3 installed on your computer.

2. Install Flask using pip:
   ```
   pip install flask
   ```

3. Navigate to the HerSpace directory:
   ```
   cd HerSpace
   ```

## Running the Application

1. Run the application:
   ```
   python app.py
   ```

2. Open your web browser and go to:
   ```
   http://127.0.0.1:5000
   ```

## Default Admin Account

When you run the application for the first time, an admin account is automatically created:

- Username: `admin`
- Password: `admin123`

You can use this account to access the admin panel and manage other users.

## User Roles

- **User**: Can create posts and view approved posts
- **Moderator**: Can view flagged posts, approve or reject posts
- **Admin**: Can do everything a moderator can do, plus manage users and change roles

## Moderation System

The application uses a rule-based moderation system with a list of bad words. Posts containing these words are automatically flagged and require moderator approval before being visible to regular users.

## Categories

Posts can be categorized as:
- General
- Discussion
- Question
- Experience
- Advice
- Support

## Project Structure

```
HerSpace/
├── app.py                 # Main Flask application
├── herSpace.db            # SQLite database (auto-created)
├── templates/             # HTML templates
│   ├── login.html
│   ├── register.html
│   ├── home.html
│   ├── create_post.html
│   ├── moderator.html
│   └── admin.html
├── static/                # Static files
│   └── css/
│       └── style.css      # Stylesheet
└── README.md              # This file
```

## Usage

1. Register a new account or login with the admin account
2. Create posts with different categories
3. Choose to post anonymously if desired
4. Moderators can review flagged posts in the Moderator Panel
5. Admins can manage users in the Admin Panel

## Notes

- The database file (herSpace.db) is created automatically when you run the application
- All data is stored locally in the SQLite database
- The application runs in debug mode by default
"# herspace" 
