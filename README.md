# HerSpace 

HerSpace is a women-only social platform built with Python and Flask. The idea behind it was to create a safe, judgment-free space where women can share their thoughts, ask for advice, and support each other  kind of like a private community forum but with a warm, modern feel.

Users can post under their own name or stay completely anonymous, and every post goes through a moderation system to keep the space respectful and safe.

This project was built as part of our 2nd year Python course. We handled everything from scratch - the database, user authentication, role system, and moderation  using only Flask and SQLite with no extra frameworks.

---

## What it does

- Users can register, log in, and log out
- Posts can be made publicly or anonymously
- Posts are sorted into categories: General, Support, Advice, Experience, Question
- A keyword-based filter automatically flags posts with inappropriate language
- Flagged posts are hidden until a moderator reviews and approves them
- Three roles: regular user, moderator, and admin
- Admins can promote users to moderators or remove accounts entirely
- Clean, responsive UI that works on both desktop and mobile

---

## How to run it

Make sure you have Python 3 installed, then install Flask:

```
pip install flask
```

Navigate into the project folder:

```
cd HerSpace
```

Run the app:

```
python app.py
```

Open your browser and go to:

```
http://127.0.0.1:5000
```

That's it - the database gets created automatically on first run.

---

## Default admin account

An admin account is created automatically when you first run the app:

- **Username:** admin
- **Password:** admin123

Use this to access the admin panel and manage users.

---

## User roles

| Role & What they can do |

| User  - Register, log in, create posts, browse the feed |

| Moderator - Everything a user can do + review and approve/reject flagged posts |

| Admin - Everything a moderator can do + manage users, change roles, delete accounts |


---

## Moderation system

When a post is submitted, the app checks the text against a list of flagged keywords. If any match, the post is automatically hidden and sent to the moderator panel for review. Moderators can then approve it (makes it visible) or reject it (deletes it). This way the feed stays clean without needing to manually check every single post.

---

## Project structure

```
HerSpace/
├── app.py                 # all the routes and backend logic
├── herSpace.db            # sqlite database (created automatically)
├── templates/
│   ├── base.html          # shared layout used by all pages
│   ├── login.html
│   ├── register.html
│   ├── home.html          # main feed with filter pills
│   ├── create_post.html
│   ├── moderator.html     # flagged posts review panel
│   └── admin.html         # user management panel
└── static/
    └── css/
        └── style.css      # all the styling
```

---

## Tech used

- **Python 3** — backend logic
- **Flask** — web framework, routing, sessions
- **SQLite** — local database, no setup needed
- **Jinja2** — HTML templating (comes with Flask)
- **DM Sans** — font from Google Fonts
- **Vanilla CSS** — no frameworks, written from scratch

---

## Notes

- Everything runs locally, no internet connection needed after setup
- The database file (herSpace.db) is created automatically when you run the application
- All data is stored locally in the SQLite database
- The application runs in debug mode by default
- Passwords are stored as plain text — we know this isn't secure for real apps, but this is a local academic project
