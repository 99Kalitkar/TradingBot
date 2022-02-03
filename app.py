from flask import Flask
from flask_restful import Resource, Api, fields, marshal_with
from flask_apispec import marshal_with, doc, use_kwargs
from flask_apispec.views import MethodResource
from marshmallow import Schema, fields
from apispec import APISpec
from flask_cors import CORS, cross_origin
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from matplotlib import collections
from utils import *


class AuthReqParams(Schema):
    username = fields.String(required=True, description="Username")
    password = fields.String(required=True, description="Password")

class AuthResParams(Schema):
    authStatus = fields.Boolean(required=True, description="Authication Status")

class Authication(MethodResource, Resource):
    @doc(description='Authicate User', tags=['Authication'])
    @use_kwargs(AuthReqParams, location=('json'))
    @marshal_with(AuthResParams)
    def post(self,**args):
        auth = database.RetriveData(collectionName="Authication",filter={"Username":args['username'],"Password":args['password']})
        if(auth):
            # Generate Bearer token
            return {"authStatus": True}
        return {"authStatus": False}
        
    @doc(description='Add user for Authication', tags=['Authication'])
    @use_kwargs(AuthReqParams, location=('json'))
    @marshal_with(AuthResParams)
    def put(self,**args):
        auth = database.InjectData(collectionName="Authication",document={"Username":args['username'], "Password":args['password']})
        if(auth):
            return {"authStatus": True}
        return {"authStatus": False}

if __name__ == '__main__':
    app = Flask(__name__)  
    CORS(app)
    database = MongoDB()
    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='Trading Bot Backend',
            version='v1',
            plugins=[MarshmallowPlugin()],
            openapi_version='2.0.0'
        ),
        'APISPEC_SWAGGER_URL': '/documentationJson',
        'APISPEC_SWAGGER_UI_URL': '/docs'
    })

    api = Api(app)
    api.add_resource(Authication, '/auth')
    docs = FlaskApiSpec(app)
    docs.register(Authication)

    app.run(debug=True)
