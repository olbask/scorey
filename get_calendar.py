import pandas as pd
import xml.etree.ElementTree as ET
import urllib

from scorey.db import get_db

SEASON = '2023/2024'
OUTCOMES = {
    0: 'not_played_yet',
    1: 'win_home_osn', 
    2: 'win_away_osn',
    3: 'win_home_ovt',
    4: 'win_away_ovt',
    5: 'win_home_bul',
    6: 'win_away_bul'
    }


def decide_result(score: str, ots: str) -> int:
    if score is not None:
        scores = score.split(':')
        if scores[0] > scores[1]:
            if ots == '':
                return 1
            elif ots == 'OT':
                return 3
            elif ots == 'SO':
                return 5
        if scores[1] > scores[0]:
            if ots == '':
                return 2
            elif ots == 'OT':
                return 4
            elif ots == 'SO':
                return 6
    return 0


def make_calendar_df() -> pd.DataFrame():
    df = pd.DataFrame(columns=['id', 'season', 'date', 'time', 'score', 'home', 'away', 'result'], index=None)
    file = urllib.request.urlopen('http://185.182.111.51:5000/calendar_xml')
    tree = ET.parse(file)
    root = tree.getroot()
    
    for game in root.findall('Game'):
        id = int(game.get('id'))
        season = SEASON
        home = game.get('homeName')
        away = game.get('visitorName')
        date = game.get('date')
        time = game.get('time')
        score = game.get('score')
        result = decide_result(game.get('score'), game.get('ots'))
        new_row = {'id': id, 
                   'season': season, 
                   'date': date, 
                   'time': time, 
                   'score': score, 
                   'home': home, 
                   'away': away, 
                   'result': result
                }
        df = pd.concat([df, pd.Series(new_row).to_frame().T], ignore_index=True)
    return df


def update_bets():
    db = get_db()
    db.execute(
        """
        UPDATE bets
        SET win = 1
        WHERE bet = (SELECT result FROM games WHERE id = bets.game_id);
        """
    )
    db.commit()


def update_points():
    db = get_db()
    db.executescript(
        """
        WITH temp_points AS (
            SELECT user_id, games.season, SUM (win) as points
                FROM bets
                JOIN games on bets.game_id = games.id
                GROUP BY user_id, season
        )
        INSERT INTO points(user_id, season, points) 
        SELECT * FROM temp_points
        WHERE True
        ON CONFLICT(user_id, season) 
        DO UPDATE SET points = EXCLUDED.points;
        """
    )
    db.commit()


def main():
    make_calendar_df()
    update_bets()
    update_points()

if __name__ == 'main':
    main()
