import os
import xml.etree.ElementTree as ET

from flask import Flask
from . import db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'scorey.sqlite'),
    )
    
    from . import db 
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import calendar
    app.register_blueprint(calendar.bp)
    
    from . import bets
    app.register_blueprint(bets.bp)
    app.add_url_rule('/', endpoint='index')
    
    from . import points
    app.register_blueprint(points.bp)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # return calendar xml for further parsing
    @app.route('/calendar_xml')
    def calendar_xml():
        with open (os.path.abspath(os.path.dirname(__file__)) + '/calendars/reg_2023_2024.xml', 'r') as xml:
            tree = ET.parse(xml)
            root = tree.getroot()
            return app.response_class(ET.tostring(root), mimetype='application/xml')

    return app
