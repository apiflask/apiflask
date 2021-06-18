import re
import setuptools

with open('apiflask/__init__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='APIFlask',
    version=version,
    license='MIT',
    author='Grey Li',
    author_email='withlihui@gmail.com',
    description='A lightweight web API framework based on Flask and marshmallow-code projects.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    platforms='any',
    url='https://apiflask.com',
    project_urls={
        'Documentation': 'https://apiflask.com/docs',
        'Source': 'https://github.com/greyli/apiflask',
        'Changelog': 'https://apiflask.com/changelog',
        'Issue Tracker': 'https://github.com/greyli/apiflask/issues',
    },
    packages=['apiflask'],
    package_data={
        'apiflask': [
            'templates/apiflask/*.html',
            'static/favicon.png',
            'py.typed'
        ]
    },
    include_package_data=True,
    install_requires=[
        'flask>=1.1.0',
        'flask-marshmallow',
        'webargs>=6',
        'flask-httpauth>=4',
        'apispec>=4.2.0',
        'typing-extensions; python_version<"3.8"',
    ],
    tests_require=[
        'openapi-spec-validator',
    ],
    extras_require={
        'dotenv': ['python-dotenv'],
        'yaml': ['pyyaml'],
        'async': ['asgiref>=3.2'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    entry_points={
        'flask.commands': [
            'spec=apiflask.commands:spec_command'
        ],
    },
)
