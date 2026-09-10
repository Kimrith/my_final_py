from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate(db)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],  # Rate limit only explicitly decorated routes (e.g. login, register)
    storage_uri="memory://",
)