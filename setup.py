from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name='APIFlask',
    install_requires=[
        'flask >= 1.1.0, <= 2.0.3',
        'flask-marshmallow >= 0.12.0',
        'marshmallow >= 3, <= 3.14.1',
        'webargs >= 6, <= 8',
        'flask-httpauth >= 4',
        'apispec >= 4.2.0, <= 5.1.1',
        'typing-extensions; python_version < "3.8"',
    ],
    tests_require=[
        'openapi-spec-validator',
    ],
    extras_require={
        'dotenv': ['python-dotenv'],
        'yaml': ['pyyaml'],
        'async': ['asgiref >= 3.2, <= 3.4.1'],
    },
)
