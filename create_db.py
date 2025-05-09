from app import app, db
from models import User, ApiEndpoint
import bcrypt

def create_db():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username="admin").first():
            hashed_pw = bcrypt.hashpw("controlx".encode("utf-8"), bcrypt.gensalt())
            admin = User(username="admin", password=hashed_pw.decode("utf-8"), role="admin")
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username='admin', password='controlx', role='admin'")
        else:
            print("Admin user already exists.")

        print("Database and tables created!")

if __name__ == "__main__":
    create_db()
