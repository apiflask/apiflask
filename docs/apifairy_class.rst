.. APIFairy documentation master file, created by
   sphinx-quickstart on Sun Sep 27 17:34:58 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The APIFairy Class
==================

The main function of the ``APIFairy`` instance is to gather all the information
registered by the decorators and generate an `OpenAPI 3.x
<https://swagger.io/specification/>`_ compliant schema with it. This schema is
then used to render the documentation site using one of the available
open-source documentation projects that are compatible with this specification.

In addition to ducmentation, ``APIFairy`` allows the application to
install a custom error handler to be used when a schema validation error occurs
in routes decorated with the ``@body`` or ``@arguments`` decorators. It also
registers routes to serve the OpenAPI definition in JSON format and a
documentation site based on one of the supported third-party documentation
projects.

APIFairy.apispec
----------------

The ``apispec`` property returns the complete OpenAPI definition for the
project as a Python dictionary. The information used to build this data is
obtained from several places:

- The project's name and version are obtained from the ``APIFAIRY_TITLE`` and
  ``APIFAIRY_VERSION`` configuration items respectively.
- The top-level documentation for the project, which appears above the API
  definitions, is obtained from the main module's docstring. Markdown can be
  used to organize this content in sections and use rich-text formatting.
- The paths are obtained from all the Flask routes that have been decorated
  with at least one of the five decorators from this project. Routes that have
  not been decorated with these decorators are not included in the
  documentation.
- The schemas and security schemes are collected from decorator usages.
- Each path is documented using the information provided in the decorators,
  plus the route definition for Flask and the docstring of the view function.
  The first line of the docstring is used as a summary and the remaining lines
  as a description.
- If a route belongs to a blueprint, the corresponding path is tagged with the
  blueprint name. Paths are grouped by their tag, which ensures that routes
  from each blueprint are rendered together in their own section. The
  ``APIFAIRY_TAGS`` configuration item can be used to provide a custom ordering
  for tags.
- Each security scheme is documented by inspecting the Flask-HTTPAuth object,
  plus the contents of the ``__doc__`` property if it exists.

APIFairy.error_handler
----------------------

The `error_handler`` method can be used to register a custom error handler
function that will be invoked whenever a validation error is raised by the
webargs project. This method can be used as a decorator as follows::

    @apifairy.error_handler
    def my_error_handler(status_code, messages):
        return {'code': status_code, 'messages': messages}, status_code

The ``status_code`` argument is the suggested HTTP status code, which is
typically 400 for a "bad request" response. The ``messages`` argument is a
dictionary with all the validation error messages that were found, organized as
a dictionary with the following structure::

    "location1": {
        "field1": ["message1", "message2", ...],
        "field2": [ ... ],
        ...
    },
    "location2": { ... },
    ...

The location keys can be ``'json'`` for the request body or ``'query'`` for the
query string.

The return value of the error handling function is interpreted as a standard
Flask response, and returned to the client as such.