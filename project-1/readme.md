# Fresh Tomatoes Movie Trailers
### [Full Stack Web Developer Nanodegree](https://classroom.udacity.com/nanodegrees/nd004/syllabus) (Project 1)
#### By Karen Barkemeyer ####

## Overview
The objective of this project is to display a list of movies on a website which provides basic information about the respective movies and lets visitors view the Youtube trailors.

The project consists of server-side code (written in Python 2.7) which stores a list of my 6 favorite movies, including the link to a movie poster and a movie trailer URL. The code is used to generate a static web page displaying the movie information and opening the respective trailers on click.

### Added functionalities
* tmdb.py: Makes a call to The Movie Database API and returns a storyline for the respective movie
* storyline will be displayed in a popover on hover over movie title
* navbar costumized with links and demo

### How to run this program
* Clone this repository
* cd [your path]/project-1
* Sign up for The Movie Database API, retrieve API key and paste into tmdb.py line 4
* Run movie_instances.py

### Preview
* Preview example webpage [here](https://kbarkemeyer.github.io/fresh-tomatoes-movie-trailers/)

### Costumize project
* [Python 2.7](https://www.python.org/downloads/)
* Clone this repository
* Navigate to project_one directory
* If applicable sign up for The Movie Database API and retrieve API key
* If NOT using Google Chrome comment out line 237 in fresh_tomatoes.py ('chrome_p = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s') and remove '.get(chrome_p)' from line 238 as this is only required for Google Chrome with Python 2.7.
* Make desired changes to code and run movie_instances.py. A new instance of fresh_tomatoes.html will be created.








