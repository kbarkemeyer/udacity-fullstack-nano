# Oauth/Item Catalog App
### [Full Stack Web Developer Nanodegree](https://classroom.udacity.com/nanodegrees/nd004/syllabus) (Project 5)
#### By Karen Barkemeyer ####

## Overview
The objective of this project is to develop a web application that provides a list of items within a variety of categories and integrate a third party user registration and authentication.

## Specifics
This application uses the the [Flask microframework](http://flask.pocoo.org/) and [SQLAlchemy](https://www.sqlalchemy.org/) for database access. 
It is a book recommendation app where the user can register and log in (with Amazon), add bookbins and fill her bookbins with book recommendations. Logged iin user can view other users' bookbins and books, add their own bookbins, add books to their own bookbins and edit/delete their own bookbins and books. Users who are not logged in can view bookbins and books.
The application also provides to JSON endpoints for bookbins and books.

The webpage includes the following features:
* User registration and login (with Amazon)
* Front page that lists all bookbins and a button for registered users to add a bookbin
* Each bookbin links to a list of recommended books. Add/edit/delete buttons are displayed to logged-in users and bookbin owners only. 

### Prerequisites
* [Python 2.7](https://www.python.org/downloads/)
* [Flask](http://flask.pocoo.org/)
* [SQLAlchemy](https://www.sqlalchemy.org/)


### Installation and testing
* Install Python, Flask and SQLAlchemy on your machine
* Clone this repository.
* Register as a seller with Amazon and retrieve your client_id and client_secret. Save both as a JSON object "a", under the file name 'amazon_client_id_secret.json' in the same folder as your app, like so:
{
  "a": {
    "client_id": "YOUR_AMAZON_CLIENT_ID",
    "client_secret": "YOUR_AMAZON_CLIENT_SECRET"
  }
}
* To test this app locally:
Navigate to the directory that contains the cloned code. Run item_catalog_db.py to create the database. In your terminal type 'export FLASK_APP=item_catalog_app.py', or for Windows 'set FLASK_APP=item_catalog_app.py' then 'flask run'. This launches a simple server for testing. Next head to localhost:5000 in your browser and view and test the web app.


