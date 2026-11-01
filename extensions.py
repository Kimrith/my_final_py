from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate(db)
csrf = CSRFProtect()

cors = CORS(resources={
    r"/api/*": {"origins": "http://localhost:3000"}
})

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],  # Rate limit only explicitly decorated routes (e.g. login, register)
    storage_uri="memory://",
)
