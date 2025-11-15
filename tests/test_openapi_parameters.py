import openapi_spec_validator as osv

from .schemas import DelimitedListQuery


def test_query_delimited_list_support(app, client):
    @app.route('/users')
    @app.input(DelimitedListQuery, location='query')
    def get_users(query_data):
        """Get Users"""
        return query_data['tags']

    rv = client.get('/openapi.json')
    assert rv.status_code == 200
    osv.validate(rv.json)
    assert rv.json['paths']['/users']['get']['parameters'][0]['name'] == 'tags'
    assert rv.json['paths']['/users']['get']['parameters'][0]['style'] == 'form'
    assert rv.json['paths']['/users']['get']['parameters'][0]['explode'] is False

    rv = client.get('/users?tags=admin,editor,user')
    assert rv.status_code == 200
    assert rv.json == ['admin', 'editor', 'user']
