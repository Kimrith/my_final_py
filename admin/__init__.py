from flask import Blueprint

admin_bp = Blueprint('admin_bp', __name__,
                     template_folder= 'templetes')

from . import dashboard
from . import user