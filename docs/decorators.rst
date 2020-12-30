.. APIFairy documentation master file, created by
   sphinx-quickstart on Sun Sep 27 17:34:58 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Decorators
==========

The core functionality of APIFairy is accessed through its five decorators,
which are used to define what the inputs and outputs of each endpoint are.

@arguments
----------

The ``arguments`` decorator specifies input arguments, given in the query
string of the request URL. The only argument this decorator requires is the
schema definition for the input data, which can be given as a schema class or
instance::

    from apifairy import arguments

    class PaginationSchema(ma.Schema):
       page = ma.Int(missing=1)
       limit = ma.Int(missing=10)

    @app.route('/api/user/<int:id>/followers')
    @arguments(PaginationSchema)
    def get_followers(pagination, id):
        page = pagination['page']
        limit = pagination['limit']
        # ...

The decorator will deserialize and validate the input data and will only
invoke the view function when the arguments are valid. In the case of a
validation error, the error handler is invoked to generate an error response
to the client.

The deserialized input data is passed to the view function as a positional
argument. Note that Flask passes path arguments as keyword arguments, so the
argument from this decorator must be defined first, as seen in the example
above. When multiple input decorators are used, the positional arguments are
given in the same order as the decorators.

Using multiple inputs
~~~~~~~~~~~~~~~~~~~~~

The ``arguments`` decorator can be given multiple times, but in that case the
schemas must have their ``unknown`` attribute set to ``EXCLUDE``, so that the
arguments from the different schemas are assigned properly::

    class PaginationSchema(ma.Schema):
        page = ma.Int(missing=1)
        limit = ma.Int(missing=10)

    class FilterSchema(ma.Schema):
        f = ma.Str()

    @app.route('/api/user/<int:id>/followers')
    @arguments(PaginationSchema(unknown=ma.EXCLUDE))
    @arguments(FilterSchema(unknown=ma.EXCLUDE))
    def get_followers(pagination, filter, id):
        page = pagination['page']
        limit = pagination['limit']
        f = filter.get('filter')
        # ...

Note that in this example the ``filter`` argument does not have ``missing`` or
``required`` attributes, so it will be considered optional. If the query string
does not include it, then ``filter`` will be empty.

Lists
~~~~~

A list can be defined in the usual way using Marshmallow's ``List`` field::

    class Filter(ma.Schema):
        f = ma.List(ma.Str())

    @app.route('/test')
    @arguments(Filter())
    def test(filter):
        f = filter.get('f', [])
        # ...

The client then must repeat the argument as many times as needed in the query
string. For example, the URL *http://localhost:5000/test?f=foo&f=bar* would
set the ``filter`` argument to ``{'f': ['foo', 'bar']}``.

Advanced Usage
~~~~~~~~~~~~~~

The ``arguments`` decorator is a thin wrapper around the ``use_args``
decorator from the `webargs <https://webargs.readthedocs.io/>`_ project with
the ``location`` argument set to ``query``. Any additional options are passed
directly into ``use_args``, which among other things allow the use of other
locations for input arguments besides the query string.

@body
-----

The ``body`` decorator defines the structure of the JSON body of the request.
The only required argument to this decorator is the schema definition for the
request body, which can be given as a schema class or instance::

    from apifairy import body

    class UserSchema(ma.Schema):
        id = ma.Int()
        username = ma.Str(required=True)
        email = ma.Str(required=True)
        about_me = ma.Str(missing='')

    @app.route('/users', methods=['POST'])
    @body(UserSchema)
    def create_user(user):
        # ...

The decorator will deserialize and validate the input data and will only
invoke the view function when the data passes validation. In the case of a
validation error, the error handler is invoked to generate an error response
to the client.

The deserialized input data is passed to the view function as a positional
argument. Note that Flask passes path arguments as keyword arguments, so the
argument from this decorator must be defined first. When multiple input
decorators are used, the positional arguments are given in the same order as
the decorators.

Advanced Usage
~~~~~~~~~~~~~~

The ``body`` decorator is a thin wrapper around the ``use_args`` decorator
from the `webargs <https://webargs.readthedocs.io/>`_ project with
the ``location`` argument set to ``json``. Any additional options are passed
directly into ``use_args``, which among other things allow the use of form
data as input instead of JSON.

@response
---------

The ``response`` decorator specifies the structure of the endpoint response.
The only required argument to this decorator is the schema that defines the
response, which can be given as a schema class or instance::

    from apifairy import response

    @app.route('/users/<int:id>')
    @response(UserSchema)
    def get_user(id):
        return User.query.get_or_404(id)

The decorator performs the serialization of the returned object or dictionary
to JSON through the schema's ``jsonify()`` method.

This decorator accepts two optional arguments. The ``status_code`` argument is
used to specify the HTTP status code for the response, when it is not the
default of 200. The ``description`` argument is used to provide a text
description of this response to be added to the documentation::

    @app.route('/users', methods=['POST'])
    @body(UserSchema)
    @response(UserSchema, status_code=201, description='A user was created.')
    def create_user(user):
        # ...
        
@other_responses
----------------

The ``other_responses`` decorator is used to specify additional responses the
endpoint can return, usually as a result of an error condition. The only
argument to this decorator is a dictionary with the keys set to numeric HTTP
status codes, and the values set to the description text for each response
code::

    from apifairy import response, other_responses

    @app.route('/users/<int:id>')
    @response(UserSchema)
    @other_responses({400: 'Invalid request.', 404: 'User not found.'})
    def get_user(id):
        # ...

This decorator does not perform any action other than adding the additional
responses to the documentation.

@authenticate
-------------

The ``authenticate`` decorator is used to specify the authentication and
authorization requirements of the endpoint. The only required argument for
this decorator is an authentication object from the `Flask-HTTPAuth
<https://flask-httpauth.readthedocs.io/>`_ extension::

    from flask_httpauth import HTTPBasicAuth
    from apifairy import authenticate

    auth = HTTPBasicAuth()

    @app.route('/users/<int:id>')
    @authenticate(auth)
    @response(UserSchema)
    def get_user(id):
        return User.query.get_or_404(id)

The decorator invokes the ``login_required`` method of the authentication
object, and also adds an Authentication section to the documentation.

If the roles feature of Flask-HTTPAuth is used, the documentation will include
the required role(s) for each endpoint. Any keyword arguments given to the
``authenticate`` decorator, including the ``role`` argument, are passed
through to Flask-HTTPAuth.
