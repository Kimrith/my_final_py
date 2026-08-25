from flask import Blueprint, request, session, redirect, url_for

admin_bp = Blueprint('admin_bp', __name__,
                     template_folder= 'templetes')


from . import dashboard
from . import user
from . import product
from . import order
from . import auth