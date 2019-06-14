from flask import Blueprint

bp = Blueprint('auth', __name__)

from viewcraft.auth import routes
