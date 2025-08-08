# Authentication

Read [this section](/usage/#use-appauth_required-to-protect-your-views)
in the Basic Usage chapter first for the basics on authentication support.

Basic concepts on the authentication support:

- APIFlask uses Flask-HTTPAuth to implement the authentication support.
- Use [`apiflask.HTTPBasicAuth`](/api/security/#apiflask.security.HTTPBasicAuth)
  for the HTTP Basic authentication.
- Use [`apiflask.HTTPTokenAuth`](/api/security/#apiflask.security.HTTPTokenAuth)
  for the HTTP Bearer authentication.
- Use [`apiflask.APIKeyHeaderAuth`](/api/security/#apiflask.security.APIKeyHeaderAuth)[`apiflask.APIKeyCookieAuth`](/api/security/#apiflask.security.APIKeyCookieAuth)[`apiflask.APIKeyQueryAuth`](/api/security/#apiflask.security.APIKeyQueryAuth)
  for the API Keys authentication.
- Use [`apiflask.MultiAuth`](/api/security/#apiflask.security.MultiAuth)
  for protecting a route with more than one authentication object.
- Read [Flask-HTTPAuth's documentation](https://flask-httpauth.readthedocs.io/)
  for the implemention of each authentication types.
- Make sure to import `HTTPBasicAuth` and `HTTPTokenAuth` from APIFlask and use the
  `app.auth_required` decorator to protect the views.
- `auth.current_user` works just like `auth.current_user()`, but shorter.

!!! warning

    Cookie authentication is currently not supported for “try it out” requests due to browser security restrictions in Swagger UI.  See this [issue](https://github.com/swagger-api/swagger-js/issues/1163) for more information.

## Use external authentication library

!!! warning "Version >= 1.0.0"

    This feature was added in the [version 1.0.0](/changelog/#version-100).

When using the `HTTPBasicAuth`, `HTTPTokenAuth`, and `app.auth_required` to implement
the authentication, APIFlask can generate the OpenAPI security spec automatically. When
you use the external authentication library, APIFlask still offers the way to set the
OpenAPI spec.

You can use the `SECURITY_SCHEMES` config or the `app.security_schemes` attribute to
set the OpenAPI security schemes:

```python
app = APIFlask(__name__)
app.security_schemes = {  # equals to use config SECURITY_SCHEMES
    'ApiKeyAuth': {
      'type': 'apiKey',
      'in': 'header',
      'name': 'X-API-Key',
    }
}
```

Then you can set the security scheme with the `security` parameter in `app.doc()` decorator:

```python hl_lines="5"
@app.post('/pets')
@my_auth_lib.protect  # protect the view with the decorator provided by external authentication library
@app.input(PetIn)
@app.output(PetOut, status_code=201)
@app.doc(security='ApiKeyAuth')
def create_pet(json_data):
    pet_id = len(pets)
    data['id'] = pet_id
    pets.append(json_data)
    return pets[pet_id]
```

With [APIFlask 1.0.2](/changelog/#version-102), when using the built-in auth support and external auth
library at the same time, the security schemes will be combined.

`app.auth_required` will generate the operation security automatically, if you use the `@doc(security=...)`
with a view that already used `app.auth_required`, then the value passed in `@doc(security=...)` will be used.


## Handle authentication errors

See [this section](/error-handling/#handling-authentication-errors) in the Error Handling chapter for
handling authentication errors.
