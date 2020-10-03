import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="apifairy",
    version="0.6.0",
    author="Miguel Grinberg",
    author_email="miguel.grinberg@gmail.com",
    description=("A minimalistic API framework built on top of Flask, "
                 "Marshmallow and friends."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/miguelgrinberg/apifairy",
    packages=setuptools.find_packages(exclude=['tests']),
    install_requires=[
        'flask',
        'flask-marshmallow',
        'webargs',
        'flask-httpauth',
        'apispec',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
