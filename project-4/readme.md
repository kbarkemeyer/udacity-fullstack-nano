# Tournament Database
### [Full Stack Web Developer Nanodegree](https://classroom.udacity.com/nanodegrees/nd004/syllabus) (Project 4)
#### By Karen Barkemeyer ####

## Overview
The objective of this project is to define a database schema and corresponding Python program to manipulate the data inside the database in order to track a Swiss style tournament. (In a Swiss style tournament players do not get eliminated but are playing a set number of rounds, determined by the number of participants. Players are paired according to their standing in the tournament -- winners play winners, losers play losers etc. Two players will only play each other once.) 

The project consists of three files:

* tournament.sql (Sets up the database schema which consists of a players table, a matches table and a view of their respective standings in the tournament.)


* tournament.py (Connects to the tournament database and provides functions to register, count and delete players, to delete and report the outcome of matches, report player standings and pair players for upcoming matches.)


* tournament_test.py (Testfile to test python functions)

### Prerequisites
* [Python 2.7](https://www.python.org/downloads/) 
* [Psycopg2](http://initd.org/psycopg/)
* [PostgresSQL](https://www.postgresql.org/)

### Installation and running the program
* Clone this repository.
* Navigate to the directory that contains the cloned code.
* From the psql command line interface import tournament.sql (\i tournament.sql)
* Run your test queries from the psql command line.
* Use functions in tournament.py to manage database content.
