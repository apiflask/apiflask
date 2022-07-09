redoc_template = """
<!DOCTYPE html>
<html>

<head>
  <title>{{ title }} {{ version }} - Redoc</title>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {% if config.REDOC_USE_GOOGLE_FONT %}
  <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
  {% endif %}
  <link rel="icon" type="image/png"
    href="{{ config.DOCS_FAVICON }}">
  <style>
    body {
      margin: 0;
      padding: 0;
    }
  </style>
</head>

<body>
  <div id="redoc"></div>

  <script src="{{ config.REDOC_STANDALONE_JS }}"> </script>
  <script>
    Redoc.init(
      "{{ url_for('openapi.spec') }}",
      {% if config.REDOC_CONFIG %}{{ config.REDOC_CONFIG | tojson }}{% else %}{}{% endif %},
      document.getElementById("redoc")
    )
  </script>
</body>

</html>
"""

swagger_ui_template = """
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <title>{{ title }} {{ version }} - Swagger UI</title>
  <link rel="stylesheet" type="text/css" href="{{ config.SWAGGER_UI_CSS }}">
  <link rel="icon" type="image/png"
    href="{{ config.DOCS_FAVICON }}">
  <style>
    html {
      box-sizing: border-box;
      overflow: -moz-scrollbars-vertical;
      overflow-y: scroll;
    }

    *,
    *:before,
    *:after {
      box-sizing: inherit;
    }

    body {
      margin: 0;
      background: #fafafa;
    }
  </style>
</head>

<body>
  <div id="swagger-ui"></div>

  <script src="{{ config.SWAGGER_UI_BUNDLE_JS }}"></script>
  <script src="{{ config.SWAGGER_UI_STANDALONE_PRESET_JS }}"></script>
  <script>
    var baseConfig = {
      url: "{{ url_for('openapi.spec') }}",
      dom_id: "#swagger-ui",
      deepLinking: true,
      presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIStandalonePreset
      ],
      plugins: [
        SwaggerUIBundle.plugins.DownloadUrl
      ],
      layout: "{{ config.SWAGGER_UI_LAYOUT }}",
            {% if oauth2_redirect_path %} oauth2RedirectUrl: "{{ oauth2_redirect_path }}"{% endif %}
        }
    {% if config.SWAGGER_UI_CONFIG %}
    var userConfig = {{ config.SWAGGER_UI_CONFIG | tojson }}
    for (var attr in userConfig) {
      baseConfig[attr] = userConfig[attr]
    }
    {% endif %}
    window.onload = function () {
      const ui = SwaggerUIBundle(baseConfig)
      {% if config.SWAGGER_UI_OAUTH_CONFIG %}
      oauthConfig = {}
      var userOauthConfig = {{ config.SWAGGER_UI_OAUTH_CONFIG | tojson
    }}
    for (var attr in userOauthConfig) {
      oauthConfig[attr] = userOauthConfig[attr]
    }
    ui.initOAuth(oauthConfig)
    {% endif %}
        }
  </script>
</body>

</html>
"""

swagger_ui_oauth2_redirect_template = """
<!doctype html>
<html lang="en-US">

<head>
  <title>Swagger UI: OAuth2 Redirect</title>
</head>

<body>
  <script>
    'use strict';
    function run() {
      var oauth2 = window.opener.swaggerUIRedirectOauth2;
      var sentState = oauth2.state;
      var redirectUrl = oauth2.redirectUrl;
      var isValid, qp, arr;

      if (/code|token|error/.test(window.location.hash)) {
        qp = window.location.hash.substring(1);
      } else {
        qp = location.search.substring(1);
      }

      arr = qp.split("&");
      arr.forEach(function (v, i, _arr) { _arr[i] = '"' + v.replace('=', '":"') + '"'; });
      qp = qp ? JSON.parse('{' + arr.join() + '}',
        function (key, value) {
          return key === "" ? value : decodeURIComponent(value);
        }
      ) : {};

      isValid = qp.state === sentState;

      if ((
        oauth2.auth.schema.get("flow") === "accessCode" ||
        oauth2.auth.schema.get("flow") === "authorizationCode" ||
        oauth2.auth.schema.get("flow") === "authorization_code"
      ) && !oauth2.auth.code) {
        if (!isValid) {
          oauth2.errCb({
            authId: oauth2.auth.name,
            source: "auth",
            level: "warning",
            message: "Authorization may be unsafe, passed state was changed in server Passed state wasn't returned from auth server"
          });
        }

        if (qp.code) {
          delete oauth2.state;
          oauth2.auth.code = qp.code;
          oauth2.callback({ auth: oauth2.auth, redirectUrl: redirectUrl });
        } else {
          let oauthErrorMsg;
          if (qp.error) {
            oauthErrorMsg = "[" + qp.error + "]: " +
              (qp.error_description ? qp.error_description + ". " : "no accessCode received from the server. ") +
              (qp.error_uri ? "More info: " + qp.error_uri : "");
          }

          oauth2.errCb({
            authId: oauth2.auth.name,
            source: "auth",
            level: "error",
            message: oauthErrorMsg || "[Authorization failed]: no accessCode received from the server"
          });
        }
      } else {
        oauth2.callback({ auth: oauth2.auth, token: qp, isValid: isValid, redirectUrl: redirectUrl });
      }
      window.close();
    }

    window.addEventListener('DOMContentLoaded', function () {
      run();
    });
  </script>
</body>

</html>
"""

elements_template = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <title>{{ title }} {{ version }} - Elements</title>
  <link rel="icon" type="image/png"
    href="{{ config.DOCS_FAVICON }}">
  <script src="{{ config.ELEMENTS_JS }}"></script>
  <link rel="stylesheet" href="{{ config.ELEMENTS_CSS }}">
</head>
<body>

  <elements-api
    apiDescriptionUrl="{{ url_for('openapi.spec') }}"
    layout="{{ config.ELEMENTS_LAYOUT }}"
    {% if config.ELEMENTS_CONFIG %}
      {% for key, value in config.ELEMENTS_CONFIG.items() %}
        {{ key }}={{ value | tojson }}
      {% endfor %}
    {% endif %}
  />

</body>
</html>
"""

rapidoc_template = """
<!doctype html> <!-- Important: must specify -->
<html>
<head>
  <meta charset="utf-8"> <!-- Important: rapi-doc uses utf8 characters -->
  <title>{{ title }} {{ version }} - RapiDoc</title>
  <link rel="icon" type="image/png"
    href="{{ config.DOCS_FAVICON }}">
  <script type="module" src="{{ config.RAPIDOC_JS }}"></script>
</head>
<body>
  <rapi-doc
    spec-url="{{ url_for('openapi.spec') }}"
    theme="{{ config.RAPIDOC_THEME }}"
    {% if config.RAPIDOC_CONFIG and 'show-header' in config.RAPIDOC_CONFIG %}
      {% set show_header = config.RAPIDOC_CONFIG['show-header'] %}
    {% else %}
      {% set show_header = False %}
    {% endif %}
    show-header="{{ show_header | tojson }}"
    {% if config.RAPIDOC_CONFIG %}
      {% for key, value in config.RAPIDOC_CONFIG.items() %}
        {{ key }}={{ value | tojson }}
      {% endfor %}
    {% endif %}
  > </rapi-doc>
</body>
</html>
"""

rapipdf_template = """
<!doctype html>
<html>
<head>
  <title>{{ title }} {{ version }} - RapiPDF</title>
  <link rel="icon" type="image/png"
    href="{{ config.DOCS_FAVICON }}">
  <script src="{{ config.RAPIPDF_JS }}"></script>
</head>
<body>
  <rapi-pdf
    spec-url="{{ url_for('openapi.spec') }}"
    {% if config.RAPIPDF_CONFIG %}
      {% for key, value in config.RAPIPDF_CONFIG.items() %}
        {{ key }}={{ value | tojson }}
      {% endfor %}
    {% endif %}
  > </rapi-pdf>
</body>
  </html>
"""

ui_templates = {
    'swagger-ui': swagger_ui_template,
    'redoc': redoc_template,
    'elements': elements_template,
    'rapidoc': rapidoc_template,
    'rapipdf': rapipdf_template,
}
