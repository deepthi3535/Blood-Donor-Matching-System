# run.py

from app import create_app, db
from app.database import init_db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        try:
            db.session.execute(db.text('SELECT 1'))
            print("Database connection successful.")
            init_db()
        except Exception as exc:
            print("ERROR: Could not connect to the database.")
            print(f"Details: {exc}")
            print("\nMake sure MySQL is running and .env credentials are correct.")
            print("Run: python setup_db.py  (to create database and user)")
            raise SystemExit(1) from exc

    app.run(debug=True, host='0.0.0.0', port=5000)
