.. APIToolkit documentation master file, created by
   sphinx-quickstart on Sun Sep 27 17:34:58 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Getting Started
===============

APIToolkit is a Web API development toolkit for Python web frameworks (currently
only support Flask) with the following goals:

- Give you a way to specify what the input arguments for each endpoint are,
  and automatically validate them for you.
- Give you a way to specify what the response format for each endpoint is, and
  automatically serialize these responses for you.
- Automatically generate API documentation for your project.
- Introduce the least amount of rules. You should be able to code your
  endpoints in the style that you like.

Below you can see an example API endpoint augmented with
APIToolkit decorators::

    from apitoolkit import authenticate, body, response, other_responses

    # ...

    @posts_blueprint.route('/posts/<int:id>', methods=['PUT'])
    @authenticate(token_auth)
    @body(update_post_schema)
    @response(post_schema)
    @other_responses({404: 'Post not found'})
    def put(updated_post, id):
        """Edit a post."""
        post = Post.query.get_or_404(id)
        for attr, value in updated_post.items():
            setattr(post, attr, value)
        db.session.commit()
        return post

APIToolkit's decorators are simple wrappers for existing solutions. In the
example above, ``token_auth`` is an intialized authentication object from the
Flask-HTTPAuth extension, and ``post_schema`` and ``update_post_schema`` are
Flask-Marshmallow schema objects. These wrappers allow APIToolkit to
automatically generate documentation using the OpenAPI 3.x standard. Below is a
screenshot of the documentation for the above endpoint:

.. image:: _static/apispec-example.png
  :width: 100%
  :alt: Automatic documentation example

Installation
------------

APIToolkit is installed with ``pip``::

    pip install apitoolkit

Once installed, this package is initialized as a standard Flask extension::

    from flask import Flask
    from apitoolkit import APIToolkit

    app = Flask(__name__)
    apitoolkit = APIToolkit(app)

The two-phase initialization style is also supported::

    from flask import Flask
    from apitoolkit import APIToolkit

    apitoolkit = APIToolkit()

    def create_app():
        app = Flask(__name__)
        apitoolkit.init_app(app)
        return app

Once APIToolkit is initialized, automatically generated documentation can be
accessed at the */docs* URL. The raw OpenAPI documentation data in JSON format
can be accessed at the */apispec.json* URL. Both URLs can be changed in the
configuration if desired.

Configuration
-------------

APIToolkit imports its configuration from the Flask configuration object.
The available options are shown in the table below.

============================== ====== =============== ==============================================================================================
Name                           Type   Default         Description
============================== ====== =============== ==============================================================================================
``APITOOLKIT_TITLE``           String APIToolkit      The API's title.
``APITOOLKIT_VERSION``         String 1.0.0           The API's version.
``APITOOLKIT_APISPEC_PATH``    String */apispec.json* The URL path where the JSON OpenAPI specification for this project is served.
``APITOOLKIT_SWAGGER_UI_PATH`` String */swaggger*     The URL path where the Swagger UI documentation is served. Set it to ``None`` to disable it.
``APITOOLKIT_REDOC_PATH``      String */redoc*        The URL path where the Redoc documentation is served. Set it to ``None`` to disable it.
``APITOOLKIT_TAGS``            List   ``None``        The list of ordered tags to include in the documentation, if the default order is not optimal.
============================== ====== =============== ==============================================================================================
