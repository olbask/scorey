from datetime import datetime
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from scorey.auth import login_required
from scorey.db import get_db

bp = Blueprint('bets', __name__)


@bp.route('/')
def index():
    db = get_db()
    bets = db.execute(
        """
        SELECT g.date, 
               g.home, 
               g.away, 
               g.time,
               g.score,
               ob.outcome as bet_outcome, 
               og.outcome as game_outcome,
               b.rowid,
               b.win, 
               b.user_id, 
               u.username, 
               b.created_at
        FROM bets b JOIN users u ON b.user_id = u.id
        JOIN games g on b.game_id = g.id
        JOIN outcomes ob on b.bet = ob.id
        JOIN outcomes og on g.result = og.id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC;
        """, (g.user['id'],)
    ).fetchall()
    now = datetime.now().date()
    
    return render_template('bets/index.html', bets=bets, now=now)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    now = datetime.now().date()
    now_time = datetime.now().strftime('%HH-%MM-%SS')
    db = get_db()
    games = db.execute(
        """
        SELECT g.id, g.date, g.time, g.home, g.away
        FROM games g
        WHERE g.id NOT IN 
            (SELECT game_id FROM bets WHERE user_id = ? AND g.result = 0)
        ORDER BY g.date ASC;
         """, (g.user['id'],)
    ).fetchall()
    bets = db.execute(
        'SELECT id, outcome' 
        ' FROM outcomes'
        ' WHERE id != 0;'
    )    
    if request.method == 'POST':
        game = request.form['game']
        bet = request.form['bet']
        current_app.logger.info('game=%s bet=%s', game, bet)
        
        error = None

        if not game or not bet:
            error = 'Select Game and Bet'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO bets (user_id, game_id, bet)'
                ' VALUES (?, ?, ?)',
                (g.user['id'], game, bet,)
            )
            db.commit()
            return redirect(url_for('bets.index'))

    return render_template('bets/create.html', games=games, bets=bets, now=now, now_time=now_time)


@bp.route('/delete', methods=('GET', 'POST'))
@login_required
def delete():
    if request.method == 'POST':
        bet_to_delete = request.form['bet_to_delete']
        db = get_db()
        db.execute(
            """
            DELETE FROM bets WHERE bets.rowid = ?
            """, (bet_to_delete,)
        )
        db.commit()
        
    return redirect(url_for('bets.index'))

