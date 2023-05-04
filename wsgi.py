import os
from src import create_app, db
from flask_migrate import Migrate

app = create_app(os.environ.get('FLASK_ENV', 'default'))
migrate = Migrate(app, db, include_schemas=True)


def test():
    """Run the unit tests."""
    import pytest
    pytest.main(['-s', './tests'])
