from alembic import op
import sqlalchemy as sa
from flask import Flask, request, redirect, url_for, render_template_string, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import OperationalError


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pastes.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Paste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)

# Home page displaying a form to create a paste
@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            ip_address = request.remote_addr  # Capture IP address
            paste = Paste(title=title, content=content, ip_address=ip_address)
            db.session.add(paste)
            db.session.commit()
            return redirect(url_for('view_paste', paste_id=paste.id))
        
        pastes_list = Paste.query.all()
        return render_template_string('''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Pastebin</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    transition: background-color 0.3s, color 0.3s;
                }
                body.light-mode {
                    background-color: #f0f0f0;
                    color: #333;
                }
                body.dark-mode {
                    background-color: #121212;
                    color: #e0e0e0;
                }
                .theme-toggle {
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    cursor: pointer;
                    background: #ddd;
                    border-radius: 50%;
                    padding: 10px;
                    transition: background-color 0.3s;
                }
                .theme-toggle:hover {
                    background: #ccc;
                }
                .theme-toggle img {
                    width: 24px;
                    height: 24px;
                }
                .container {
                    max-width: 800px;
                    margin: 20px auto;
                    padding: 20px;
                    background: #fff;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    transition: box-shadow 0.3s;
                }
                .container:hover {
                    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
                }
                input[type="text"], textarea {
                    width: 100%;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 10px;
                    box-sizing: border-box;
                    transition: border-color 0.3s;
                }
                input[type="text"]:focus, textarea:focus {
                    border-color: #007bff;
                    outline: none;
                }
                textarea {
                    resize: vertical;
                }
                button, input[type="submit"] {
                    background: #007bff;
                    border: none;
                    color: #fff;
                    padding: 10px 20px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    transition: background-color 0.3s;
                }
                button:hover, input[type="submit"]:hover {
                    background: #0056b3;
                }
                h1, h2 {
                    margin-top: 0;
                }
                ul {
                    list-style: none;
                    padding: 0;
                }
                ul li {
                    margin: 5px 0;
                }
                a {
                    color: #007bff;
                    text-decoration: none;
                    transition: color 0.3s;
                }
                a:hover {
                    color: #0056b3;
                }
            </style>
        </head>
        <body class="light-mode">
            <div class="theme-toggle" onclick="toggleTheme()">
                <img src="https://img.icons8.com/material-outlined/24/000000/sun.png" id="theme-icon" alt="Theme Toggle">
            </div>
            <div class="container">
                <h1>Create a new paste</h1>
                <form method="post">
                    <label for="title">Title:</label>
                    <input type="text" id="title" name="title" required><br>
                    <label for="content">Content:</label><br>
                    <textarea id="content" name="content" rows="10" required></textarea><br>
                    <input type="submit" value="Create Paste">
                </form>
                <h2>Past Pasts:</h2>
                <ul>
                    {% for paste in pastes_list %}
                        <li>
                            <a href="{{ url_for('view_paste', paste_id=paste.id) }}">{{ paste.title }}</a>
                            {% if paste.ip_address == request.remote_addr %}
                                <a href="{{ url_for('delete_paste', paste_id=paste.id) }}">Delete</a>
                            {% endif %}
                        </li>
                    {% endfor %}
                </ul>
            </div>
            <script>
                function toggleTheme() {
                    const body = document.body;
                    const icon = document.getElementById('theme-icon');
                    if (body.classList.contains('light-mode')) {
                        body.classList.replace('light-mode', 'dark-mode');
                        icon.src = 'https://img.icons8.com/material-outlined/24/000000/moon.png';
                        localStorage.setItem('theme', 'dark');
                    } else {
                        body.classList.replace('dark-mode', 'light-mode');
                        icon.src = 'https://img.icons8.com/material-outlined/24/000000/sun.png';
                        localStorage.setItem('theme', 'light');
                    }
                }

                document.addEventListener('DOMContentLoaded', () => {
                    const savedTheme = localStorage.getItem('theme') || 'light';
                    document.body.classList.add(savedTheme + '-mode');
                    document.getElementById('theme-icon').src = savedTheme === 'dark'
                        ? 'https://img.icons8.com/material-outlined/24/000000/moon.png'
                        : 'https://img.icons8.com/material-outlined/24/000000/sun.png';
                });
            </script>
        </body>
        </html>
        ''', pastes_list=pastes_list)

    except OperationalError as e:
        return f"Database error: {e}", 500

# Page to view a specific paste
@app.route('/paste/<int:paste_id>')
def view_paste(paste_id):
    paste = Paste.query.get(paste_id)
    if paste is None:
        return "Paste not found!", 404
    
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ paste.title }}</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                transition: background-color 0.3s, color 0.3s;
            }
            body.light-mode {
                background-color: #f0f0f0;
                color: #333;
            }
            body.dark-mode {
                background-color: #121212;
                color: #e0e0e0;
            }
            .theme-toggle {
                position: fixed;
                top: 10px;
                right: 10px;
                cursor: pointer;
                background: #ddd;
                border-radius: 50%;
                padding: 10px;
                transition: background-color 0.3s;
            }
            .theme-toggle:hover {
                background: #ccc;
            }
            .theme-toggle img {
                width: 24px;
                height: 24px;
            }
            .container {
                max-width: 800px;
                margin: 20px auto;
                padding: 20px;
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                transition: box-shadow 0.3s;
            }
            .container:hover {
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
            }
            pre {
                background: #f7f7f7;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                overflow: auto;
                white-space: pre-wrap;
                transition: background-color 0.3s, color 0.3s;
            }
            body.light-mode pre {
                background: #f7f7f7;
                color: #333;
            }
            body.dark-mode pre {
                background: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #444;
            }
            textarea {
                width: 100%;
                height: 300px;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 10px;
                box-sizing: border-box;
                font-family: 'Arial', sans-serif;
                font-size: 14px;
                resize: none;
                transition: background-color 0.3s, color 0.3s, border-color 0.3s;
            }
            body.light-mode textarea {
                background-color: #ffffff;
                color: #333;
                border-color: #ddd;
            }
            body.dark-mode textarea {
                background-color: #333333;
                color: #e0e0e0;
                border-color: #444444;
            }
            a {
                color: #007bff;
                text-decoration: none;
                transition: color 0.3s;
            }
            a:hover {
                color: #0056b3;
            }
        </style>
    </head>
    <body class="light-mode">
        <div class="theme-toggle" onclick="toggleTheme()">
            <img src="https://img.icons8.com/material-outlined/24/000000/sun.png" id="theme-icon" alt="Theme Toggle">
        </div>
        <div class="container">
            <h1>{{ paste.title }}</h1>
            <textarea readonly>{{ paste.content }}</textarea>
            <a href="{{ url_for('home') }}">Back</a>
        </div>
        <script>
            function toggleTheme() {
                const body = document.body;
                const icon = document.getElementById('theme-icon');
                if (body.classList.contains('light-mode')) {
                    body.classList.replace('light-mode', 'dark-mode');
                    icon.src = 'https://img.icons8.com/material-outlined/24/000000/moon.png';
                    localStorage.setItem('theme', 'dark');
                } else {
                    body.classList.replace('dark-mode', 'light-mode');
                    icon.src = 'https://img.icons8.com/material-outlined/24/000000/sun.png';
                    localStorage.setItem('theme', 'light');
                }
            }

            document.addEventListener('DOMContentLoaded', () => {
                const savedTheme = localStorage.getItem('theme') || 'light';
                document.body.classList.add(savedTheme + '-mode');
                document.getElementById('theme-icon').src = savedTheme === 'dark'
                    ? 'https://img.icons8.com/material-outlined/24/000000/moon.png'
                    : 'https://img.icons8.com/material-outlined/24/000000/sun.png';
            });
        </script>
    </body>
    </html>
    ''', paste=paste)



# Route to delete a specific paste
@app.route('/delete/<int:paste_id>')
def delete_paste(paste_id):
    paste = Paste.query.get(paste_id)
    if paste is None:
        return "Paste not found!", 404

    if paste.ip_address != request.remote_addr:
        abort(403)  # Forbidden

    db.session.delete(paste)
    db.session.commit()
    return redirect(url_for('home'))

def upgrade():
    op.add_column('paste', sa.Column('ip_address', sa.String(length=45), nullable=True))

def downgrade():
    op.drop_column('paste', 'ip_address')

if __name__ == '__main__':
    app.run(debug=True)
