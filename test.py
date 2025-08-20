from app import app  # Import your Flask app
from models import db, User
from werkzeug.security import generate_password_hash

# Create an application context
with app.app_context():
    admin_user = User(username='admin12', password=generate_password_hash('adminpass'), is_admin=True)
    db.session.add(admin_user)
    db.session.commit()
