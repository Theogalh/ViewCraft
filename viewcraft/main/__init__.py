from flask import Blueprint

bp = Blueprint('main', __name__)

from viewcraft.main import routes
