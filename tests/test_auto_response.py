from flask.views import MethodView


def test_auto_200_response(app):
    app.config['AUTO_200_RESPONSE'] = True

    @app.get('/foo/<id>')
    def get_foo(id):
        return {}

    @app.delete('/foo/<id>')
    def delete_foo(id):
        return {}

    spec = app.spec
    get_foo_schema = spec['paths']['/foo/{id}']['get']['responses']['200']['content'][
        'application/json'
    ]['schema']
    delete_foo_schema = spec['paths']['/foo/{id}']['delete']['responses']['200']['content'][
        'application/json'
    ]['schema']
    assert get_foo_schema == delete_foo_schema
    assert get_foo_schema is not delete_foo_schema


def test_auto_200_response_method_view(app):
    app.config['AUTO_200_RESPONSE'] = True

    @app.route('/foo/<id>')
    class FooAPI(MethodView):
        def get(self, id):
            return {}

        def delete(self, id):
            return {}

    spec = app.spec
    get_foo_schema = spec['paths']['/foo/{id}']['get']['responses']['200']['content'][
        'application/json'
    ]['schema']
    delete_foo_schema = spec['paths']['/foo/{id}']['delete']['responses']['200']['content'][
        'application/json'
    ]['schema']
    assert get_foo_schema == delete_foo_schema
    assert get_foo_schema is not delete_foo_schema
