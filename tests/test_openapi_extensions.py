from openapi_spec_validator import validate_spec


def test_specification_extensions(app, client):
    @app.get('/')
    @app.doc(extensions={'x-foo': {'foo': 'bar'}})
    def foo():
        pass

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    validate_spec(rv.json)
    assert rv.json['paths']['/']['get']['x-foo'] == {
        'foo': 'bar'
    }
