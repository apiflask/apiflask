from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name='APIFlask',
    install_requires=[
        'flask >= 2',
        'flask-marshmallow >= 0.12.0',
        'webargs >= 8.3',
        'flask-httpauth >= 4',
        'apispec >= 6',
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
