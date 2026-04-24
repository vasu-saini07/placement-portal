from flask import Flask
from flask_login import LoginManager
from models import db, User

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Initialize DB
db.init_app(app)

# Setup Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'   # because using Blueprint


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Register Blueprint
from routes import bp
app.register_blueprint(bp)


if __name__ == '__main__':
    app.run(debug=True)