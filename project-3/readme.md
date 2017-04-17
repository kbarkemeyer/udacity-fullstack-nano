# Intro to Backend
### [Full Stack Web Developer Nanodegree](https://classroom.udacity.com/nanodegrees/nd004/syllabus) (Project 3)
#### By Karen Barkemeyer ####

## Overview
The objective of this project is to develop a blog application using Google App Engine. The blog includes the following features:
* User registration and login
* Front page that lists all blog posts and a link which opens a form to submit new entries
* Each blog post has their own page with like, edit, delete and comment buttons. Buttons are displayed when appropriate to users only. Users can like/unlike any post once (but not their own). Like/unlike buttons are only displayed if user is not the author of the post. Users can edit or delete their own posts. Those buttons are displayed to the authors of posts only. Users can all comment on posts. They can only edit or delete their own comments. 


### Added functionalities
* Handlers for editing, deleting, liking/unliking and commenting on posts, and handlers for editing and deleting comments.
* When user deletes her post, all comments are also deleted.
* script1.js (jquery.min.js) for like/unlike feature AJAX calls


### Prerequisites
* [Python 2.7](https://www.python.org/downloads/)
* [Google App Engine SDK](https://cloud.google.com/appengine/downloads)
* [Jinja2](http://jinja.pocoo.org/)


### Installation
* Clone this repository.
* Create a new Cloud Platform project and App Engine application using the Cloud Platform Console.
* Download and install the Google Cloud SDK


## Test Code Locally
* Navigate to the directory that contains the cloned code.
* To test the code on the local development server (included in the SDK), type in the following commend from within the project-3 directory (which contains the yaml file): dev_appserver.py app.yaml  
* Visit http://localhost:8080/ in your web browser to view the app.


### Deploy the App
* To deploy your app to App Engine, run the following command from within the root directory of your application where the app.yaml file is located: gcloud app deploy
* To launch your browser and view the app at http://[YOUR_PROJECT_ID].appspot.com, run the following command: gcloud app browse


### Preview
* Preview this blog [here](https://backend-project-1.appspot.com/blog)

