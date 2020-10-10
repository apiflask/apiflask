import re
import setuptools

with open('apifairy/__init__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="apifairy",
    version=version,
    author="Miguel Grinberg",
    author_email="miguel.grinberg@gmail.com",
    description=("A minimalistic API framework built on top of Flask, "
                 "Marshmallow and friends."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/miguelgrinberg/apifairy",
    packages=setuptools.find_packages(exclude=['tests']),
    package_data={'apifairy': ['templates/apifairy/*.html']},
    include_package_data=True,
    install_requires=[
        'flask>=1.1.0',
        'flask-marshmallow',
        'webargs>=6',
        'flask-httpauth>=4',
        'apispec>=4',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
