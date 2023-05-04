# Daraja-B2B

This API has the following endpoints:

```bash
[POST] api/v1/payment/initiate                      ✅
[POST] api/v1/payment/timeout                       ✅
[POST] api/v1/payment/confirm                       ✅
````

### Usage:

#### Development

You need [python](https://www.python.org/downloads/) and [pipenv](https://pypi.org/project/pipenv/). You can read more about pipenv [here](https://pipenv.pypa.io/en/latest/).

```bash
$ cd daraja-b2b
$ pipenv install
$ pipenv shell
$ export FLASK_ENV=development
$ export SECRET_KEY=AS4rWWGq3ASDdU4EfqYfb545b3c1177c79de83216824a587
$ flask db upgrade
$ flask run
```

To run unittest,

```bash
$ flask test
```

If all went well, your app should be available on [http://localhost:5000](http://localhost:5000)