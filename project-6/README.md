# Neighborhood Map
### [Full Stack Web Developer Nanodegree](https://classroom.udacity.com/nanodegrees/nd004/syllabus) (Project 6)
#### By Karen Barkemeyer ####

## Overview
The objective of this project is to develop a single page application featuring a map of a specific neighborhood with highlighted locations that display third party information about these locations.

## Specifics
The application displays a list of gluten-free restaurants in Portland, OR. The list can be filtered according to geographical location and information about a particular restaurant by a third party API is delivered on click. The address of the chosen restaurant will be shown underneath the name and an google info window will open with a picture, the address and a link with further restaurant information.
The application uses the the [Knockout framework](http://knockoutjs.com/index.html) to handle changing information on the page. It is structured according to Knockout's MVVM (Model-View-ViewModel) pattern. It also uses [Google's Maps API](https://developers.google.com/maps/) to display the map and it calls the [Zomato API](https://developers.zomato.com/api#headline1) to provide information on the restaurants. 


The application includes the following features:
* List of restaurants that can be filtered according to location.
* Google map with markers corresponding to restaurant list.
* Clickable restaurant names and corresponding map markers to display additional information.


### Installation and testing
* Clone this repository.
* To test this application:
Navigate to the directory that contains the cloned code and open the index.html file in your browser. 


