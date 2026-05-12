# HostelHub (Flask)

HostelHub is a single-user-role hostel marketplace where each student can buy, sell, donate, chat, request items, complete transactions, rate peers, and receive notifications.

## Tech Stack
- Backend: Flask, Flask-Login, Flask-SQLAlchemy
- Database: SQLite
- Frontend: HTML, CSS, JavaScript, Bootstrap 5
- Chat updates: Polling every 3 seconds via REST API

## Folder Structure

```text
HostelHub/
  app/
    __init__.py
    auth_routes.py
    main_routes.py
    api_routes.py
    models.py
    seed.py
    templates/
      base.html
      auth/
        login.html
        register.html
      items/
        index.html
        form.html
      chat/
        chat_home.html
        chat.html
      transactions/
        index.html
      users/
        profile.html
        notifications.html
    static/
      css/style.css
      js/main.js
    uploads/
  requirements.txt
  run.py
```

## Setup Instructions

1. Create and activate a virtual environment.

```powershell
cd HostelHub
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Initialize database with sample data.

```powershell
flask --app run.py init-db
```

4. Run the app.

```powershell
python run.py
```

5. Open in browser:

`http://127.0.0.1:5000`

## Sample Accounts
- `alice@example.com` / `password123`
- `bob@example.com` / `password123`
- `carol@example.com` / `password123`

## Core Feature Coverage
- Single role system (no admin/moderator)
- Auth: register/login/logout
- Item listings: create/read/update/delete + mark sold/available + image upload
- Marketplace: search/filter by category, keyword, max price
- Room-based discovery: seller hostel + room displayed
- Chat: one-to-one messaging + history in DB
- Transaction flow: request -> accept/reject -> completed (marks item sold)
- Ratings: 1-5 stars with average rating on profile
- Notifications: new message, new request, transaction update
- REST API used by frontend for chat, transaction, rating, notifications

## Notes
- This is a local development build (debug mode on).
- Uploaded images are stored in `app/uploads`.
