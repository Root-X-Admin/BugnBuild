from flask import Flask
from config import Config
from models import db
from flask_login import LoginManager
import markdown  # ✅ Import markdown
from markupsafe import Markup

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # redirect to login when not logged in

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ✅ Register markdown filter
@app.template_filter('markdown')
def markdown_filter(text):
    return Markup(markdown.markdown(text))

from routes import *

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
