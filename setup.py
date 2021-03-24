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
    author='Grey Li',
    author_email='withlihui@gmail.com',
    description='A lightweight Web API framework based on Flask and marshmallow-code projects.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    platforms='any',
    url='https://github.com/greyli/apiflask',
    packages=setuptools.find_packages(exclude=['tests']),
    package_data={'apiflask': ['templates/apiflask/*.html']},
    include_package_data=True,
    install_requires=[
        'flask>=1.1.0',
        'flask-marshmallow',
        'webargs>=6',
        'flask-httpauth>=4',
        'apispec>=4.2.0',
    ],
    tests_require=[
        'openapi-spec-validator',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
