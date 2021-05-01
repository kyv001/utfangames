"""
This script runs the blog application using a development server.
"""

from os import environ
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from utfangames import app
from utfangames.models import db
import utfangames.models

HOST = environ.get('SERVER_HOST', 'localhost')
try:
    PORT = int(environ.get('SERVER_PORT', '80'))
except ValueError:
    PORT = 80
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "阿巴阿巴阿巴阿巴"

with app.app_context():
    db.init_app(app)
    db.create_all()

manager = Manager(app)
Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)
manager.add_command('start', Server(host=HOST, port=PORT))

if __name__ == '__main__':
    manager.run()

