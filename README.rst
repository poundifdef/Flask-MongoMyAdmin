Flask-MongoMyAdmin
==================

This is an Apache2-licensed Flask extension to perform basic queries and
updates to MongoDB collections. It is a thin wrapper around pymongo, and
as such it relies on it for validation and error checking.

This is a work in progres; I would love for this to become a feature-complete
frontend to MongoDB which makes it easy to add on to any flask project.

Features
--------

- Connect to Mongo databases or replica sets

- Browse all databases available to a given connection string

- Create new collections (specify capped, max size, etc)

- Run queries against collections

- Create and edit documents

- Handles AutoReconnect errors and connection string errors

There are many useful things which are not yet part of this extension.
Pull requests are absolutely welcome.

Installation
------------

Couldn't be easier:

.. code-block:: bash

    $ pip install Flask-MongoMyAdmin

Quickstart
----------

All you need is a valid MongoDB connection URI. This extension can manage
multiple databases. You set them via key-value pairs in 
:code:`app.config['MONGOMYADMIN_DATABASES']`.

The key is just a display name for that mongo connection. You may set it to
whatever you would like. The value is a mongo connection string.

Here is a sample Flask app to get started:

.. code-block:: python

    from flask import Flask
    from flask.ext.mongomyadmin import MongoMyAdmin

    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'app secret key'

    app.config['MONGOMYADMIN_DATABASES'] = {
        'local': 'mongodb://127.0.0.1:27017',
        'remote_qa': 'mongodb://user@pass:mongo.example.com:27017',
    }

    m = MongoMyAdmin(app)

    @app.route('/')
    def index():
        return 'hello'

    if __name__ == '__main__':
        app.run(debug=True)


From there, navigate to :code:`http://localhost:5000/MongoMyAdmin` and you will see
your databases.
