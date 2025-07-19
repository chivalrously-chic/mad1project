from flask import Flask
from backend import models

app = None  # Initially none

def init_app():
    quiz_app = Flask(__name__)  # object of Flask
    quiz_app.debug = True
    quiz_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz.sqlite3"
    models.db.init_app(quiz_app)  # Use models.db to initialize

    # Create the database tables within the application context
    with quiz_app.app_context():
        models.db.create_all()  # Use models.db to create

        # Import controllers AFTER app context is set.
        from backend import controllers

    print("Quiz application started....")
    return quiz_app

app = init_app()  # set global app

if __name__ == "__main__":
    app.run()