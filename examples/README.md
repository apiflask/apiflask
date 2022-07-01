# Examples

- Basic example: [/examples/basic/app.py][_basic]
- Class-based view example: [/examples/cbv/app.py][_cbv]
- ORM example (with Flask-SQLAlchemy): [/examples/orm/app.py][_orm]
- Pagination example (with Flask-SQLAlchemy): [/examples/pagination/app.py][_pagination]
- OpenAPI example: [/examples/openapi/app.py][_openapi]
- Base response example: [/examples/base_response/app.py][_base_response]
- Token auth example: [/examples/auth/token_auth/app.py][_token_auth]
- Basic auth example: [/examples/auth/basic_auth/app.py][_basic_auth]
- Dataclass example (with marshmallow-dataclass): [/examples/dataclass/app.py][_dataclass]

[_basic]: https://github.com/apiflask/apiflask/tree/main/examples/basic/app.py
[_cbv]: https://github.com/apiflask/apiflask/tree/main/examples/cbv/app.py
[_orm]: https://github.com/apiflask/apiflask/tree/main/examples/orm/app.py
[_pagination]: https://github.com/apiflask/apiflask/tree/main/examples/pagination/app.py
[_openapi]: https://github.com/apiflask/apiflask/tree/main/examples/openapi/app.py
[_base_response]: https://github.com/apiflask/apiflask/tree/main/examples/base_response/app.py
[_token_auth]: https://github.com/apiflask/apiflask/tree/main/examples/auth/token_auth/app.py
[_basic_auth]: https://github.com/apiflask/apiflask/tree/main/examples/auth/basic_auth/app.py
[_dataclass]: https://github.com/apiflask/apiflask/tree/main/examples/dataclass/app.py

If you have built an application with APIFlask, feel free to submit a pull request to add the source link here.

- [Flog](https://github.com/flog-team/flog-api-v4) (under active construction)

Follow the commands in the *Installation* section to run these examples on your computer.


## Installation


### Build the environment

For macOS and Linux:

```bash
$ git clone https://github.com/apiflask/apiflask
$ cd apiflask/examples
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

For Windows:

```text
> git clone https://github.com/apiflask/apiflask
> cd apiflask\examples
> python -m venv venv
> venv\Scripts\activate
> pip install -r requirements.txt
```


### Choose the application

Each example application store in a sub-folder:

- `/basic`: Basic example
- `/cbv`: Classed-based view example
- `/orm`: ORM example (with Flask-SQLAlchemy)
- `/pagination`: Pagination example (with Flask-SQLAlchemy)
- `/openapi`: OpenAPI example
- `/base_response`: Base response example
- `/dataclass`: Dataclass example (with marshmallow-dataclass)

To run a specific example, you have to change into the corresponding folder.
For example, if you want to run the basic example:

```bash
$ cd basic
```


### Run, Flask, Run!

After change into the desired folder, use `flask run` command to run
the example application:

```bash
$ flask run
  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```


## Try it out

When the application is running, now you can visit the interactive API documentation at <http://localhost:5000/docs>. Inside the detail tab of each endpoint, you can click the "Try it out" button to test the APIs:

![](https://apiflask.com/_assets/try-it-out.png)

Then click the "Execute" button, it will send a request to the related endpoint and retrieve the response back:

![](https://apiflask.com/_assets/execute.png)


## Do some experiment

If you want to do some experiment on the example application, just open the `app.py` with your favorite editor. To make the application reload every time after you change the code, use the `--reload` option for `flask run`:

```bash
$ flask run --reload
```

Furthermore, you can run the application in debug mode; it will enable the reloader and debugger as default. To enable the debug mode, you will need to set the environment variable `FLASK_ENV` to `development` before executing `flask run`, see *[Debug Mode](https://flask.palletsprojects.com/en/main/quickstart/#debug-mode)* for more details.
