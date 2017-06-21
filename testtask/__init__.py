from pyramid.config import Configurator
from pyramid.events import NewRequest
import pymongo
from pymongo import MongoClient
from pyramid.session import SignedCookieSessionFactory
my_session_factory = SignedCookieSessionFactory('testtask')

def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.set_session_factory(my_session_factory)	
    config.include('pyramid_chameleon')
    config.add_static_view(name='static', path='testtask:static')
    config.add_static_view('deform_static', 'deform:static/')
    config.add_route('view', '/')
    config.add_route('view_res', '/results')
	
    def add_mongo_db(event):
        settings = event.request.registry.settings
        url = settings['mongodb.url']
        db_name = settings['mongodb.db_name']
        db = settings['mongodb_conn'][db_name]
        event.request.db = db
		
    db_uri = settings['mongodb.url']
    MongoDB = pymongo.Connection
    if 'pyramid_debugtoolbar' in set(settings.values()):
        class MongoDB(pymongo.Connection):
            def __html__(self):
                return 'MongoDB: <b>{}></b>'.format(self)

    conn = MongoClient('mongodb://localhost:27017')
    config.registry.settings['mongodb_conn'] = conn
    config.add_subscriber(add_mongo_db, NewRequest)
	
    config.scan('.views')
    return config.make_wsgi_app()