from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = 'herspace2024'
DB = 'herSpace.db'

# words we dont want in posts
BAD_WORDS = [
    'hate', 'kill', 'stupid', 'idiot', 'dumb', 'ugly', 'fat', 'loser',
    'shut up', 'shutup', 'hate you', 'i hate', 'you suck', 'sucks',
    'terrible', 'awful', 'worst', 'whore', 'bitch', 'fuck', 'ass', 'motherfucker'
]


# opens a connection to our sqlite database
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row  # so we can do row['username'] instead of row[0]
    return conn


# creates tables when we run the app for the first time
def setup_db():
    conn = get_db()
    c = conn.cursor()

    # users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')

    # posts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            user_id INTEGER,
            is_anonymous INTEGER DEFAULT 0,
            is_flagged INTEGER DEFAULT 0,
            is_approved INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # likes table
    c.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            post_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (post_id) REFERENCES posts (id),
            UNIQUE(user_id, post_id)
        )
    ''')

    # comments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            user_id INTEGER,
            post_id INTEGER,
            is_anonymous INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
    ''')

    conn.commit()
    conn.close()


# checks if a post has any bad words in it
def has_bad_words(text):
    text = text.lower()
    for word in BAD_WORDS:
        if word in text:
            return True
    return False


# decorator - checks if user is logged in, we learned this in class
def login_required(f):
    @wraps(f)
    def check_login(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return check_login


# decorator - checks if user is a mod or admin
def mod_required(f):
    @wraps(f)
    def check_mod(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') not in ['moderator', 'admin']:
            flash('You are not allowed to access this page.')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return check_mod


# decorator - checks if user is admin
def admin_required(f):
    @wraps(f)
    def check_admin(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Only admins can access this page.')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return check_admin


# home page - shows all approved posts, optionally filtered by category
@app.route('/')
@app.route('/category/<category>')
def home(category=None):
    conn = get_db()
    c = conn.cursor()

    if category:
        c.execute('''
            SELECT posts.*, users.username
            FROM posts
            LEFT JOIN users ON posts.user_id = users.id
            WHERE posts.is_approved = 1 AND posts.category = ?
            ORDER BY posts.created_at DESC
        ''', (category,))
    else:
        c.execute('''
            SELECT posts.*, users.username
            FROM posts
            LEFT JOIN users ON posts.user_id = users.id
            WHERE posts.is_approved = 1
            ORDER BY posts.created_at DESC
        ''')
    all_posts = c.fetchall()

    # get like counts for each post
    like_counts = {}
    c.execute('SELECT post_id, COUNT(*) as count FROM likes GROUP BY post_id')
    for row in c.fetchall():
        like_counts[row['post_id']] = row['count']

    # get comment counts for each post
    comment_counts = {}
    c.execute('SELECT post_id, COUNT(*) as count FROM comments GROUP BY post_id')
    for row in c.fetchall():
        comment_counts[row['post_id']] = row['count']

    # check which posts current user has liked
    user_likes = set()
    if 'user_id' in session:
        c.execute('SELECT post_id FROM likes WHERE user_id = ?', (session['user_id'],))
        for row in c.fetchall():
            user_likes.add(row['post_id'])

    conn.close()

    return render_template('home.html', posts=all_posts, current_category=category,
                           like_counts=like_counts, comment_counts=comment_counts,
                           user_likes=user_likes)


# like a post
@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO likes (user_id, post_id) VALUES (?, ?)',
                  (session['user_id'], post_id))
        conn.commit()
    except sqlite3.IntegrityError:
        # already liked
        pass
    conn.close()
    cat = request.args.get('category')
    if cat:
        return redirect(url_for('home', category=cat))
    return redirect(url_for('home'))


# unlike a post
@app.route('/unlike/<int:post_id>', methods=['POST'])
@login_required
def unlike_post(post_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM likes WHERE user_id = ? AND post_id = ?',
              (session['user_id'], post_id))
    conn.commit()
    conn.close()

    cat = request.args.get('category')
    if cat:
        return redirect(url_for('home', category=cat))
    return redirect(url_for('home'))


# add a comment
@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form['content']
    is_anon = 1 if request.form.get('anonymous') else 0

    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO comments (content, user_id, post_id, is_anonymous)
        VALUES (?, ?, ?, ?)
    ''', (content, session['user_id'], post_id, is_anon))
    conn.commit()
    conn.close()

    cat = request.args.get('category')
    if cat:
        return redirect(url_for('home', category=cat))
    return redirect(url_for('home'))


# delete own post
@app.route('/delete_post/<int:post_id>')
@login_required
def delete_post(post_id):
    conn = get_db()
    c = conn.cursor()
    # verify ownership
    c.execute('SELECT user_id FROM posts WHERE id = ?', (post_id,))
    post = c.fetchone()
    if post and post['user_id'] == session['user_id']:
        c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        flash('Post deleted.')
    else:
        flash('You can only delete your own posts.')
    conn.close()

    cat = request.args.get('category')
    if cat:
        return redirect(url_for('home', category=cat))
    return redirect(url_for('home'))


# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()

        # check if user exists and password matches
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Welcome back!')
            return redirect(url_for('home'))
        else:
            flash('Wrong username or password.')

    return render_template('login.html')


# register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm_password']

        # make sure both passwords are the same
        if password != confirm:
            flash('Passwords do not match.')
            return render_template('register.html')

        conn = get_db()
        c = conn.cursor()

        # check if username is already taken
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing = c.fetchone()

        if existing:
            conn.close()
            flash('That username is already taken.')
            return render_template('register.html')

        # save new user to database
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                  (username, password, 'user'))
        conn.commit()
        conn.close()

        flash('Account created! You can login now.')
        return redirect(url_for('login'))

    return render_template('register.html')


# logout - just clears the session
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))


# create a new post
@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        content = request.form['content']
        category = request.form['category']
        user_id = session['user_id']

        # check if user wants to post anonymously
        is_anon = 0
        if request.form.get('anonymous'):
            is_anon = 1

        # check if the post has bad words
        flagged = 0
        if has_bad_words(content):
            flagged = 1

        # if flagged, dont show it until a mod approves it
        approved = 1
        if flagged == 1:
            approved = 0

        conn = get_db()
        c = conn.cursor()
        c.execute('''
            INSERT INTO posts (content, category, user_id, is_anonymous, is_flagged, is_approved)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (content, category, user_id, is_anon, flagged, approved))
        conn.commit()
        conn.close()

        if flagged == 1:
            flash('Your post has been sent for review before it goes live.')
        else:
            flash('Post shared!')

        return redirect(url_for('home'))

    return render_template('create_post.html')


# moderator panel - shows flagged posts
@app.route('/moderator')
@mod_required
def moderator():
    conn = get_db()
    c = conn.cursor()

    # get all posts that are flagged or not approved yet
    c.execute('''
        SELECT posts.*, users.username
        FROM posts
        LEFT JOIN users ON posts.user_id = users.id
        WHERE posts.is_flagged = 1 OR posts.is_approved = 0
        ORDER BY posts.created_at DESC
    ''')
    flagged = c.fetchall()
    conn.close()

    return render_template('moderator.html', posts=flagged)


# approve a post
@app.route('/approve_post/<int:post_id>')
@mod_required
def approve_post(post_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE posts SET is_approved = 1, is_flagged = 0 WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    flash('Post approved.')
    return redirect(url_for('moderator'))


# reject and delete a post
@app.route('/reject_post/<int:post_id>')
@mod_required
def reject_post(post_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    flash('Post removed.')
    return redirect(url_for('moderator'))


# admin panel - shows all users
@app.route('/admin')
@admin_required
def admin():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users ORDER BY id')
    all_users = c.fetchall()
    conn.close()
    return render_template('admin.html', users=all_users)


# change a users role
@app.route('/change_role/<int:user_id>/<new_role>')
@admin_required
def change_role(user_id, new_role):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
    conn.commit()
    conn.close()
    flash('Role updated.')
    return redirect(url_for('admin'))


# delete a user and all their posts
@app.route('/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    # cant delete yourself
    if user_id == session['user_id']:
        flash('You cannot delete your own account.')
        return redirect(url_for('admin'))

    conn = get_db()
    c = conn.cursor()
    # delete their posts first then the user
    c.execute('DELETE FROM posts WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    flash('User deleted.')
    return redirect(url_for('admin'))


# makes a default admin account when app starts
def make_admin():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not c.fetchone():
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                  ('admin', 'admin123', 'admin'))
        conn.commit()
    conn.close()


if __name__ == '__main__':
    setup_db()
    make_admin()
    app.run(host='0.0.0.0', port=5000, debug=True)
