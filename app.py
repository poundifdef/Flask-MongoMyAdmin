from flask import Flask
from flask.ext.mongomyadmin import MongoMyAdmin

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hello world'

app.config['MONGOMYADMIN_DATABASES'] = {
    'local': 'mongodb://127.0.0.1:27017',
#    'local_munge': 'mongodb://a@b:127.0.0.1:27017',
#    'remote': 'mongodb://a:b@candidate.2.mongolayer.com:10000',
}

m = MongoMyAdmin(app)

@app.route('/')
def index():
    return 'hello'

if __name__ == '__main__':
    app.run(debug=True)
