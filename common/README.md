# EDA

This library contains common utils for event driven architecture implementation:

- Events
- Aggregates
- Units of Work

## Development

To install library dependencies, you should have [poetry](https://github.com/python-poetry/poetry) installed:

```shell script
poetry install
```

Enforce code style:
```shell script
poetry run black .
poetry run isort -y
poetry run flake8 --max-line-length=119 --max-complexity=10
```

Run tests (with coverage):
```shell script
poetry run pytest --cov=common
```
