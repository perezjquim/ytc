import gunicorn #dummy
from flask import Flask
from flask_cors import CORS
from handlers.APIHandler import APIHandler

api_handler = APIHandler( )

app = Flask( __name__ )
app.config[ 'JSONIFY_PRETTYPRINT_REGULAR' ] = False

CORS( app )
app.register_blueprint( api_handler.get_blueprint( ) )

if __name__ == "__main__":
    app.run()