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

### Preview
* Preview this blog [here](https://backend-project-1.appspot.com/blog)

