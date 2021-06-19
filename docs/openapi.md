# OpenAPI Generating


## The spec format

The default format of the OpenAPI spec is JSON, while YAML is also supported.
If you want to enable the YAML support, install APIFlask with the `yaml` extra
(it will install `PyYAML`):

```
$ pip install apiflask[yaml]
```

Now you can change the format via the `SPEC_FORMAT` config:

```
from apiflask import APIFlask

app = APIFlask(__name__)
app.config['SPEC_FORMAT'] == 'yaml'
```

This config will also control the format output by the `flask spec` command.


## The indentation of spec

When you view the spec from your browser via `/openapi.json`, if you enabled the
debug mode or set the configuration variable `JSONIFY_PRETTYPRINT_REGULAR` to
`True`, the indentation will set to `2`. Otherwise, the JSON spec will be sent
without indentation and spaces to save the bandwidth and speed the request.

The indentation of the local spec file is enabled by default. The default indentation
is the default value of the `LOCAL_SPEC_JSON_INDENT` config (i.e., `2`). When you
use the `flask spec` command, you can change the indentation with the `--indent`
or `-i` option.

The indentation of the YAML spec is always `2`, and it can't be changed for now.


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


### Change the indentation of JSON spec

For the local spec file, the indentation is always needed for readability and
easy to trace the changes. The indentation can be set with the `--indent` or
`-i` option:

```
$ flask spec --indent 4
```

You can also set the indentation with the configuration variable
`LOCAL_SPEC_JSON_INDENT` (defaults to `2`), then the value will be used in
the `flask spec` command when the `--indent/-i` option is not passed:

```python
from apiflask import APIFlask

app = APIFlask(__name__)

app.config['LOCAL_SPEC_JSON_INDENT'] = 4
```

```
$ flask spec
```


## Keep the local spec in sync automatically

!!! warning "Version >= 0.7.0"

    This feature was added in the [version 0.7.0](/changelog/#version-070).

With the `flask spec` command, you can easily generate the spec to a local file.
While it will be handy if the spec file is in sync with the project code.
To achieve this, you need to set a path to the config `LOCAL_SPEC_PATH`,
then enable the sync by setting the config `SYNC_LOCAL_SPEC` to `True`:

```python
from apiflask import APIFlask

app = APIFlask(__name__)

app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = 'openapi.json'
```

!!! warning

    If the path you passed is a relative path, do not put a leading slash in it.

APIFlask will create the file at your current working directory (where you execute the
`flask run` command). We recommend using an absolute path. For example, you can use
`app.root_path`, which stores the absolute root path to your app module:

```python
from pathlib import Path

app = APIFlask(__name__)
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = Path(app.root_path) / 'openapi.json'
```

Or use the `os` module:

```python
import os

app = APIFlask(__name__)
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = os.path.join(app.root_path, 'openapi.json')
```

You can also find the project root path manually based on the current module's
`__file_` variable when you are using an application factory:

```python
from pathlib import Path

base_path = Path(__file__).parent
# you may need to use the following if current module is
# inside the application package:
# base_path = Path(__file__).parent.parent

app = APIFlask(__name__)
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = base_path / 'openapi.json'
```

Or use the `os` module:

```python
import os

base_path = os.path.dirname(__file__)
# you may need to use the following if current module is
# inside the application package:
# base_path = os.path.dirname(os.path.dirname(__file__))

app = APIFlask(__name__)
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = os.path.join(base_path, 'openapi.json')
```
