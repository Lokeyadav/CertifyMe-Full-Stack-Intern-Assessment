from flask import Flask
from config import Config
from models import db
from flask_login import LoginManager

def create_app():
    app = Flask(__name__, static_folder='sky', static_url_path='')
    app.config.from_object(Config)

    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    from models import Admin
    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    from routes import api_bp
    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        return app.send_static_file('admin.html')

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
