# Tips

## Run the application behind a reverse proxy

If you are running the application behind a reverse proxy (e.g. Nginx),
you will need to set the config file like this:

```
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Prefix /;
    }
}
```

If your application is running on a different URL prefix, you need to change
both the location and the `X-Forwarded-Prefix` header:

```hl_lines="5 10"
server {
    listen 80;
    server_name _;

    location /api {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Prefix /api;
    }
}
```

!!! notes

    From version 1.2.1, APIFlask will update the OpenAPI's `servers` field automatically.
    If you set the `AUTO_SERVERS` config to `False`, then you will need to update
    the `servers` field manually to specify the URL prefix:

    ```python
    app.config['SERVERS'] = [{'url': '/api'}]
    ```


Then apply the proxy fix middleware for your application:

```python
from werkzeug.middleware.proxy_fix import ProxyFix
from apiflask import APIFlask


app = APIFlask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
```


See also:

- [Deploying with Nginx](https://flask.palletsprojects.com/deploying/nginx/)
- [Tell Flask it is Behind a Proxy](https://flask.palletsprojects.com/deploying/proxy_fix/)
