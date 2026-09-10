from flask import Blueprint

front_bp = Blueprint('front_bp', __name__)

from . import home
from . import about
from . import menu
from . import contact
from . import product
from . import cart
from . import checkout
from . import account
from . import auth