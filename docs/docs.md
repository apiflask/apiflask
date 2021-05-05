# Documentation Index

Welcome to APIFlask's documentation!

Documentation progress:

[=50%]

## Contents

Go through the following chapters to learn how to use APIFlask:

- **[Introduction](/)**: A general introduction for APIFlask.
- **[Migrating from Flask](/migrating)**: Migrating guide and notes.
- **[Basic Usage](/usage)**: Get started with APIFlask.
- **Schema, Fields, and Validators**: Introduce how to write an input/output schema.
- **Request Validating**: The detailed introduction of the `@input` decorator.
- **Response Formatting**:  The detailed introduction of the `@output` decorator.
- **OpenAPI Generating**: Introduce how the OpenAPI generation works and how to customize
it with `@doc` decorator and configuration variables.
- **Authentication**: Introduce how to implement HTTP Basic and Token-based authentication.
- **[Swagger UI and Redoc](/api-docs)**: Introduce the usage and configuration of the API
documentation tools.
- **[Configuration](/configuration)**: A list of all the built-in configuration variables
- **[Examples](/examples)**: A collection of application examples.

The following chapters are useful for contributors and who want to know more about
APIFlask:

- **[API Reference](/api/app)**: The API reference of APIFlask.
- **[Comparison and Motivations](/comparison)**: The differences between APIFlask and similar projects.
- **[Authors](/authors)**: The authors of APIFlask.
- **[Changelog](/changelog)**: The change log of each version of APIFlask.

## External Documentations

I will try to cover all the basic usages in APIFlask's documentation. However, for advanced
usages, you may need to read the documentation of the framework, tools that APIFlask based
on:

- **[Flask](https://flask.palletsprojects.com){target=_blank}**: The knowledge of Flask is required.
- **[Marshmallow](https://marshmallow.readthedocs.io/){target=_blank}**: Advanced reference for schema.
- **[Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/){target=_blank}**: Advanced reference for
the usage of `HTTPBasicAuth` and `HTTPTokenAuth`.
- **[Webargs](https://webargs.readthedocs.io/){target=_blank}**: Useful for contributors.
- **[APISpec](https://apispec.readthedocs.io/){target=_blank}**: Useful for contributors.
- **[OpenAPI](https://github.com/OAI/OpenAPI-Specification/tree/main/versions){target=_blank}**:
The OpenAPI Specification.
- **[JSON Schema](https://json-schema.org/){target=_blank}**: Useful when you want to set a custom
error schema and you don't want to use schema class.
