from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name='APIFlask',
    install_requires=[
        'flask >= 1.1.0',
        'flask-marshmallow >= 0.12.0',
        'webargs >= 6',
        'flask-httpauth >= 4',
        'apispec >= 4.2.0',
        'typing-extensions; python_version < "3.8"',
    ],
    tests_require=[
        'openapi-spec-validator',
    ],
    extras_require={
        'dotenv': ['python-dotenv'],
        'yaml': ['pyyaml'],
        'async': ['asgiref >= 3.2'],
    },
)
