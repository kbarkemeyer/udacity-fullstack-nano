-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- 
DROP DATABASE IF EXISTS tournament;

-- Creates database 
CREATE DATABASE tournament;
\c tournament;


CREATE TABLE players (
	ID SERIAL PRIMARY KEY,
	name text
);


CREATE TABLE matches (
	ID SERIAL PRIMARY KEY,
	winner integer REFERENCES players(ID),
	loser integer REFERENCES players(ID)
);


CREATE VIEW standings AS 
	SELECT id, name,
	(SELECT COUNT(*) AS wins FROM matches WHERE matches.winner = players.id),
	(SELECT COUNT(*) AS match_nr FROM matches WHERE matches.winner = players.id OR matches.loser = players.id)
	FROM players
	ORDER BY wins DESC;
	

