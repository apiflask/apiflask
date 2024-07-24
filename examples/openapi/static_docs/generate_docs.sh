#!/bin/bash

spec_value=$(python3 -c "import json; print(open('openapi.json').read())")
# Replace var spec = {...} line in index.html
sed -i "s|var spec = {.*}|var spec = $spec_value|g" index.html
echo "Swagger HTML generated successfully!"
echo "Open index.html in your browser to view the Swagger UI."
