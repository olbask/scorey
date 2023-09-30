from datetime import datetime
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, url_for
)

from scorey.auth import login_required
from scorey.db import get_db
from . import get_calendar



bp = Blueprint('points', __name__, url_prefix='/points')


@bp.route('/')
def index():
    get_calendar.update_bets()
    get_calendar.update_points()
    db = get_db()
    users = db.execute(
        """
        SELECT u.username, p.season, p.points FROM points p
        JOIN users u on p.user_id = u.id
        ORDER BY p.points DESC;
        """
    ).fetchall()
    return render_template('points/points.html', users=users)
    