from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import (ConfigurationError, OperationFailure,
                            PyMongoError, AutoReconnect)
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, flash, render_template, redirect, request, url_for


class MongoConnections:

    def __init__(self, connection_strings):
        self.connection_strings = connection_strings
        self.connections = {}

    def __getitem__(self, server_name):

        if not self.connections.get(server_name):
            try:
                self.connections[server_name] = MongoClient(
                    self.connection_strings[server_name])
            except Exception as ex:
                flash('Problem connecting to "%s": %s' %
                      (server_name, str(ex)))

        return self.connections.get(server_name)


class MongoMyAdmin(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def create_blueprint(self):

        def choose_database():
            return render_template('choose_database.html')

        def choose_collection(server, db):
            conn = self.mongo_connections[server]
            if not conn:
                return redirect(url_for('mongomyadmin.choose_database'))

            if request.method == 'POST':
                try:
                    collection_args = {}

                    collection_args['name'] = request.form['collection_name']
                    collection_args['capped'] = bool(
                        request.form['collection_capped'] == 'T'
                    )

                    if request.form['collection_size']:
                        collection_args['size'] = int(
                            request.form['collection_size']
                        )

                    if request.form['collection_max']:
                        collection_args['max'] = int(
                            request.form['collection_max']
                        )

                    conn[db].create_collection(**collection_args)
                    flash('created collection')
                except PyMongoError as ex:
                    flash(str(ex))

            collections = []
            try:
                collections = conn[db].collection_names()
            except PyMongoError as ex:
                flash(str(ex))

            return render_template('choose_collection.html', server=server,
                                   db=db, collections=collections)

        def search_collection(server, db, collection):
            conn = self.mongo_connections[server]
            if not conn:
                return redirect(url_for('mongomyadmin.choose_database'))

            db_collection = conn[db][collection]

            mongo_fields = request.args.get('fields')
            if mongo_fields:
                mongo_fields = dict((field, 1) for field in mongo_fields.split(','))
            else:
                mongo_fields = None

            mongo_sort = request.args.get('sort', None)
            if mongo_sort:
                new_mongo_sort = []
                for field in mongo_sort.split(','):
                    if len(field.split(':')) != 2:
                        new_mongo_sort = []
                        flash('sort needs to be valid')
                        break

                    field_name, field_order = field.split(':')
                    pymongo_order = ASCENDING if field_order == '1' else DESCENDING
                    new_mongo_sort.append((field_name, pymongo_order))

                mongo_sort = new_mongo_sort

            mongo_limit = request.args.get('limit')
            if mongo_limit:
                try:
                    mongo_limit = int(mongo_limit)
                except ValueError as ex:
                    mongo_limit = 10
            else:
                mongo_limit = 10

            mongo_offset = request.args.get('offset')
            if mongo_offset:
                try:
                    mongo_offset = int(mongo_offset)
                    if mongo_offset < 0:
                        mongo_offset = 0
                except ValueError as ex:
                    mongo_offset = 0
            else:
                mongo_offset = 0

            mongo_query = request.args.get('q')
            if mongo_query:
                try:
                    mongo_query = loads(mongo_query)
                except ValueError as ex:
                    flash(ex)
            else:
                mongo_query = None

            results = []
            count = 0
            try:
                pymongo_results = db_collection.find(
                    mongo_query,
                    sort=mongo_sort,
                    fields=mongo_fields,
                    skip=mongo_offset).limit(mongo_limit)

                count = pymongo_results.count()
                results = list(pymongo_results)
            except Exception as ex:
                flash(ex)

            return render_template('search_collection.html', server=server,
                                   db=db, collection=collection,
                                   results=results, count=count,
                                   limit=mongo_limit, offset=mongo_offset)

        def edit_document(server, db, collection, document):
            conn = self.mongo_connections[server]
            if not conn:
                return redirect(url_for('mongomyadmin.choose_database'))

            db_collection = conn[db][collection]

            mongo_json = {}
            if request.method == 'POST':
                document_id = document
                try:
                    oid = ObjectId(document)
                    document_id = oid
                except InvalidId:
                    pass

                try:
                    db_collection.update(
                        {'_id': document_id},
                        loads(request.form['document_contents']),
                    )
                    flash('saved')
                except Exception as ex:
                    mongo_json = request.form['document_contents']
                    flash(ex)

            if not mongo_json:
                document_id = document
                try:
                    oid = ObjectId(document)
                    document_id = oid
                except InvalidId:
                    pass

                mongo_json = dumps(db_collection.find_one(
                    {'_id': document_id}), indent=2)

            return render_template('mongo_document.html', server=server,
                                   db=db, collection=collection,
                                   document=document, mongo_json=mongo_json)

        def new_document(server, db, collection):
            conn = self.mongo_connections[server]
            if not conn:
                return redirect(url_for('mongomyadmin.choose_database'))

            mongo_json = ''

            if request.method == 'POST':
                try:
                    db_collection = conn[db][collection]

                    new_id = db_collection.insert(
                        loads(request.form['document_contents']),
                    )
                    flash('document created')
                    return redirect(url_for('mongomyadmin.edit_document',
                                    server=server, db=db,
                                    collection=collection, document=new_id))
                except Exception as ex:
                    mongo_json = request.form['document_contents']
                    flash(ex)

            return render_template('new_document.html', server=server, db=db,
                                   collection=collection,
                                   mongo_json=mongo_json)

        bp = Blueprint('mongomyadmin', __name__,
                       url_prefix='/MongoMyAdmin',
                       template_folder='templates/mongomyadmin',
                       static_folder='static/mongomyadmin',
                       static_url_path='/static',
             )

        bp.route('/', methods=['GET'],
                 endpoint='choose_database')(choose_database)
        bp.route('/db/<server>/<db>/', methods=['GET', 'POST'],
                 endpoint='choose_collection')(choose_collection)
        bp.route('/db/<server>/<db>/<collection>/', methods=['GET'],
                 endpoint='search_collection')(search_collection)
        bp.route('/db/<server>/<db>/<collection>/new', methods=['GET', 'POST'],
                 endpoint='new_document')(new_document)
        bp.route('/db/<server>/<db>/<collection>/<document>',
                 methods=['GET', 'POST'],
                 endpoint='edit_document')(edit_document)

        return bp

    def init_app(self, app):
        app.config.setdefault('MONGOMYADMIN_DATABASES', {})

        self.mongo_connections = MongoConnections(
            app.config['MONGOMYADMIN_DATABASES']
        )

        def get_databases(server):
            conn = self.mongo_connections[server]
            if not conn:
                return []

            databases = set()

            try:
                try:
                    db_list = conn.database_names()
                    databases |= set(db_list)
                except OperationFailure:
                    pass

                try:
                    databases.add(conn.get_default_database().name)
                except ConfigurationError:
                    pass
            except AutoReconnect as ex:
                flash('Problem autoreconnecting to %s: %s' % (server, str(ex)))
                return []

            return databases

        app.jinja_env.globals.update(get_databases=get_databases)
        app.jinja_env.globals.update(dumps=dumps)

        app.register_blueprint(self.create_blueprint())
