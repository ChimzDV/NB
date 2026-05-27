# NovaBridge - Loan Management Backend

NovaBridge is a modern loan management system backend built using Flask.

## Project Structure

```text
NB/
├── app/
│   ├── models/            # Database Models (User, Loan, Document, Payment, etc.)
│   ├── routes/            # Blueprint API Routes (Auth, Admin, Loans, Main)
│   ├── services/          # Business Logic & Core Services (Reminder, Loan service)
│   ├── templates/         # HTML templates (Auth, Dashboard, Admin, Main)
│   └── static/            # Static assets (CSS, JS, Images, Uploads)
├── database/              # Local Database storage (SQLite)
├── migrations/            # Database migration scripts
├── venv/                  # Python Virtual Environment
├── requirements.txt       # Project python dependencies
├── run.py                 # Application Entrypoint
├── .env                   # Local Environment Configuration
└── README.md              # Project Documentation
```

## Getting Started

1. **Clone the repository** and navigate to the project directory:
   ```bash
   cd NB
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   flask run
   # Or:
   python run.py
   ```
