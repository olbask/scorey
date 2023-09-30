import pandas as pd
import xml.etree.ElementTree as ET

from . import get_calendar
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from scorey.db import get_db

bp = Blueprint('calendar', __name__, url_prefix='/calendar')

@bp.route('/table_update')
def table_update():
    df = get_calendar.make_calendar_df()
    db = get_db()
    db.executescript(
        """
        DROP TABLE IF EXISTS temp_calendar;
        CREATE TABLE temp_calendar (
            id integer PRIMARY KEY,
            season varchar,
            home varchar,
            away varchar,
            date date,
            time varchar,
            score varchar,
            result integer,
            FOREIGN KEY (result) REFERENCES outcomes(id)
        ); 
        """
    )
    
    for i, row in df.iterrows():
        db.execute(
            f"""
            INSERT INTO temp_calendar (id, season, home, away, date, time, score, result)
            VALUES (
                {row['id']}, 
                '{row['season']}', 
                '{row['home']}', 
                '{row['away']}', 
                '{row['date']}', 
                '{row['time']}', 
                '{row['score']}', 
                {row['result']})
            """
        )
        
    upd_calend = db.executescript(
            """
            INSERT INTO games SELECT * FROM temp_calendar
            WHERE true
            ON CONFLICT(id) DO UPDATE 
            SET result = EXCLUDED.result, 
                date = EXCLUDED.date,
                time = EXCLUDED.time,
                score = EXCLUDED.score;
            DROP TABLE temp_calendar;
            """
    )

    get_calendar.update_bets()
    get_calendar.update_points()
    
    data = db.execute("""SELECT g.season, g.date, g.time, g.home, g.away, g.score, o.outcome FROM games AS g
                      LEFT JOIN outcomes as o ON g.result = o.id
                      """).fetchall()
    return render_template('calendar/table.html', data=data)
