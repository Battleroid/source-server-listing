from time import strftime
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from valve.source.a2s import ServerQuerier, NoResponseError
from socket import gaierror
from marshmallow import Schema, fields

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///servers.db'
app.config['DEBUG'] = True

class Server(db.Model):
    __tablename__ = 'servers'

    address = db.Column(db.String(255), primary_key=True)
    port = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), default='Unknown')
    map = db.Column(db.String(35))
    game = db.Column(db.String(255))
    version = db.Column(db.String(16))
    players = db.Column(db.Integer(), default=0)
    maxplayers = db.Column(db.Integer(), default=0)
    status = db.Column(db.Boolean(), default=False)
    last_checked = db.Column(db.DateTime(), default=datetime.now(), onupdate=datetime.now(), nullable=False)

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.status = False
        self._query()

    def _query(self):
        try:
            server = ServerQuerier((self.address, self.port))
            info = server.get_info()
            self.name = info['server_name']
            self.map = info['map']
            self.game = info['game']
            self.version = info['version']
            self.players = info['player_count']
            self.maxplayers = info['max_players']
            self.last_checked = datetime.now()
            self.status = True
        except (gaierror, NoResponseError):
            pass

    def update(self):
        self.status = False
        self._query()

    def __repr__(self):
        return '<Server %r:%r ON: %r>' % (self.address, self.port, self.status)

class ServerSchema(Schema):
    last_checked = fields.DateTime(format='%H:%M %Y-%m-%d')
    map = fields.Function(lambda obj: obj.map.title())

    class Meta:
        fields = ('address', 'port', 'name', 'game', 'map', 'version', 'players', 'maxplayers', 'status', 'last_checked')
        ordered = True

def update_all():
    for server in Server.query.all():
        server.update()

@app.template_filter('last_checked_format')
def last_checked_format(date):
    return date.strftime('%H:%M %Y-%m-%d')

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.route('/servers/<int:offset>', methods=['GET'])
@app.route('/servers', methods=['GET'])
def get_servers(offset=0):
    if request.method == 'GET':
        servers = Server.query.offset(offset * 10).limit(10).all()
        result = ServerSchema(servers, many=True)
        json = jsonify({ 'offset' : offset * 10, 'servers' : result.data})
        json.status_code = 200
        return json

@app.route('/server', methods=['GET'])
def get_server_info():
    if request.method == 'GET':
        address, port = request.args.get('address'), request.args.get('port')
        server = Server.query.get((address, int(port)))
        if server:
            result = ServerSchema(server)
            json = jsonify(result.data)
            json.status_code = 200
            return json
        else:
            result = jsonify({'status' : 404, 'message' : 'Not Found'})
            result.status_code = 404
            return result

@app.route('/')
def index():
    return render_template('index.html', servers=Server.query.with_entities(Server.address, Server.port, Server.status).all())

if __name__ == '__main__':
    app.run()
