# OpenAPI Generating


## Use the `flask spec` command to output the OpenAPI spec

!!! warning "Version >= 0.7.0"

    This feature was added in the [version 0.7.0](/changelog/#version-070).

The `flask spec` command will output the spec to stdout when you execute
the command:

```
$ flask spec
```

See the output of `flask spec --help` for the full API reference of this
command:

```
$ flask spec --help
```

You can skip the next three sections if you have executed the above command.


### Output the spec to a file

If you provide a path with the `--output` or `-o` option, APIFlask will write
the spec to the given path:

```
$ flask spec --output openapi.json
```

!!! note "No such file or directory?"

    If the given path does not exist, you have to create the directory by yourself,
    then APIFlask will create the file for you.

You can also set the path with the configuration variable `LOCAL_SPEC_PATH`, then the
value will be used in `flask spec` command when the `--output/-o` option is not passed:

```python
from apiflask import APIFlask

app = APIFlask(__name__)

app.config['LOCAL_SPEC_PATH'] = 'openapi.json'
```

```
$ flask spec
```


### Change the spec format

Similarly, the spec format can be set with the `--format` or `-f` option
(defaults to `json`):

```
$ flask spec --format json
```

You can also set the format with the configuration variable `SPEC_FORMAT` (defaults
to `'json'`), then the value will be used in `flask spec` command when the
`--format/-f` option is not passed:

```python
from apiflask import APIFlask

app = APIFlask(__name__)

app.config['SPEC_FORMAT'] = 'yaml'
```

```
$ flask spec
```


### Change the indent of JSON spec

For the local spec file, the indent is always for readability and easy to trace the
changes. The indent can be set with the `--indent` or `-i` option:

```
$ flask spec --indent 4
```

You can also set the indent with the configuration variable `LOCAL_SPEC_JSON_INDENT`
(defaults to `2`), then the value will be used in `flask spec` command when the
`--indent/-i` option is not passed:

```python
from apiflask import APIFlask

app = APIFlask(__name__)

app.config['LOCAL_SPEC_JSON_INDENT'] = 4
```

```
$ flask spec
```

!!! note "The indent of spec response (`/openapi.json`)"

    When you view the spec from your browser via `/openapi.json`, if you enabled the
    debug mode or set the configuration variable `JSONIFY_PRETTYPRINT_REGULAR` to
    `True`. Otherwise, the JSON spec will be sent without indent to save the bandwidth
    and speed the request.
