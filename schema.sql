DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS bets;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS points;
DROP TABLE IF EXISTS outcomes;

CREATE TABLE bets (
  user_id integer,
  game_id integer,
  bet integer,
  created_at timestamp not null default current_timestamp,
  win boolean not null default 0,
  PRIMARY KEY (user_id, game_id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (game_id) REFERENCES games(id),
  FOREIGN KEY (bet) REFERENCES outcomes(id)
);

CREATE TABLE games (
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

CREATE TABLE points (
  user_id integer,
  season varchar,
  points integer,
  PRIMARY KEY (user_id, season),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE outcomes (
  id integer PRIMARY KEY,
  outcome varchar not null
);

CREATE TABLE users (
  id integer PRIMARY KEY,
  username varchar not null unique,
  password varchar not null,
  created_at timestamp not null default current_timestamp
);

INSERT INTO outcomes (id, outcome)
VALUES (0, 'not_played_yet');

INSERT INTO outcomes (id, outcome)
VALUES (1, 'win_home_osn');

INSERT INTO outcomes (id, outcome)
VALUES (2, 'win_away_osn');

INSERT INTO outcomes (id, outcome)
VALUES (3, 'win_home_ovt');

INSERT INTO outcomes (id, outcome)
VALUES (4, 'win_away_ovt');

INSERT INTO outcomes (id, outcome)
VALUES (5, 'win_home_bul');

INSERT INTO outcomes (id, outcome)
VALUES (6, 'win_away_bul');




