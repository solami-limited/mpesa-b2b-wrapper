# MPESA B2B API (wrapper)

[![PyTest](https://github.com/clovisphere/mpesa-b2b-wrapper/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/clovisphere/mpesa-b2b-wrapper/actions/workflows/pytest.yml)
[![Coverage Status](https://coveralls.io/repos/github/clovisphere/mpesa-b2b-wrapper/badge.svg)](https://coveralls.io/github/clovisphere/mpesa-b2b-wrapper)

A wrapper that makes it easy to integrate with the [MPESA B2B API](https://developer.safaricom.co.ke/Documentation).

The below endpoints are available:

```bash
[POST] api/v1.0/payment/initiate                      ✅
[POST] api/v1.0/payment/timeout                       ✅
[POST] api/v1.0/payment/confirm                       ✅
````

☝🏽 See [requests.http](requests.http) for sample requests + payloads.

TODO:
- [x] Unit tests
- [ ] Logging
- [x] CI/CD
- [ ] Dockerize
- [ ] Deployment (or how-to section on how to deploy or run the app in production)

## Usage

Make a copy of [.env.dev](.env.dev) file named `.env`, and make sure all the **ENVIRONMENT_VARIABLES** are set.

### Prerequisites:

- [Python](https://www.python.org/downloads/release/python-3112/)
- [Pipenv](https://pipenv.pypa.io/en/latest/)
- [SQLite](https://www.sqlite.org/index.html) (optional | for development and testing)
- [MySQL](https://www.mysql.com/) or [PostgreSQL](https://www.postgresql.org/) (optional)

#### Development:

```bash
$ cd mpesa-b2b-api  # cd into project root
$ export FLASK_ENV=development  # enable development mode
$ export SECRET_KEY=AS4rWWGq3ASDdU4EfqYfb545b3c1177c79de83216824a587  # set the secret key
$ pipenv install # install dependencies
$ pipenv shell  # activate virtualenv
$ flask db upgrade  # run migrations
$ flask run --debug  # run the app in debug mode
```

If you need any help with migration, please refer to [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/).

To run unittest,

```bash
$ python -m pytest
```

If all went well, your app should be available on [http://localhost:5000](http://localhost:5000)
