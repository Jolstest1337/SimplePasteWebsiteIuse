# Simple Pastebin With Database

A simple pastebin application built with Flask, SQLAlchemy, and Flask-Migrate. This application allows users to create, view, and delete "pastes" (text snippets), with optional theme support for light and dark modes.

## Features

- **Create Pastes:** Submit a title and content to create a new paste.
- **View Pastes:** Access and view specific pastes.
- **Delete Pastes:** Remove pastes if created by the current user.
- **Theme Toggle:** Switch between light and dark modes.
- **Database:** Uses SQLite to store pastes.

## Prerequisites

- Python 3.6+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- SQLAlchemy

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Jols1337/SimplePasteWebsiteIuse.git
    cd SimplePasteWebsiteIuse
    ```

2. **Install the required packages:**

    ```bash
    pip install Flask==2.1.1
    pip install Flask-SQLAlchemy==2.5.1
    pip install Flask-Migrate==3.1.0
    pip install SQLAlchemy==1.4.29
    ```

3. **Initialize the database:**

    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

4. **Run the application:**

    ```bash
    python app.py
    ```


## Usage

1. **Home Page:** Navigate to the root URL to create new pastes and view existing ones.
2. **View Paste:** Click on a paste title to view its content.
3. **Delete Paste:** If you created a paste, you can delete it via the provided link.

## Development

### Database Schema

The `Paste` model includes the following columns:
- `id`: Integer, primary key
- `title`: String, not nullable
- `content`: Text, not nullable
- `ip_address`: String, not nullable

The `ip_address` column is used to identify the user who created the paste for deletion purposes.

### Migrations

The Alembic migration script includes:
- `upgrade()`: Adds the `ip_address` column to the `paste` table.
- `downgrade()`: Removes the `ip_address` column from the `paste` table

# Note
I'm still learning HTML, so there is a bug with the dark mode on the textbox i haven't fixed it yet but on the next update it will be fixed also it took longer than more than expected.

## License

This project is licensed under the  Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
