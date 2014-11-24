from datetime import datetime
from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from valve.source.a2s import ServerQuerier, NoResponseError
from socket import gaierror

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///servers.db'

class Server(db.Model):
    __tablename__ = 'servers'

    name = db.Column(db.String(255))
    address = db.Column(db.String(255), primary_key=True)
    port = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean, default=False)
    last_checked = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)

    def __init__(self, name, address, port):
        self.name = name
        self.address = address
        self.port = port
        self.status = False
        self._query()

    def _query(self):
        try:
            server = ServerQuerier((self.address, self.port))
            info = server.get_info()
            self.status = True
        except (gaierror, NoResponseError):
            pass

    def update(self):
        self.status = False
        self._query()

    def __repr__(self):
        return '<Server %r:%r ON: %r>' % (self.address, self.port, self.status)

def update_all():
    servers = Server.query.all()
    for server in servers:
        server.update()

@app.route('/')
def index():
    return render_template('index.html', servers=Server.query.with_entities(Server.name, Server.address, Server.port, Server.status).all())

if __name__ == '__main__':
    app.run()
