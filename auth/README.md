# Auth Service

## Development

To install service dependencies, you should have [poetry](https://github.com/python-poetry/poetry) installed:

```shell script
poetry install -E migrations
```

Apply migrations

```shell script
alembic upgrade head
```

Enforce code style:
```shell script
poetry run black .
poetry run isort -y
poetry run flake8 --max-line-length=119 --max-complexity=10
```

Run tests (with coverage):
```shell script
poetry run pytest --cov=auth
```
