# Vóisa Recipes

We must develop without losing traditions. One of the most important to
maintain are the grandmother's culinary recipes. This app allows you to record
these recipes for eternity, in addition to knowing the recipes of other
grandparents around the world.

## Features
* User can create, edit and delete recipes
* User can log in through the Google or Facebook APIs
* No users can view recipes
* User can upload recipe image to illustrate
* Web app is responsive, then it can be used on mobile phones as well

## Use

### Online app
You can visit and use this app in https://voisa-recipe.herokuapp.com

It is a beta deployment

### Git repository

1. Clone or download this repository.
2. It use a development environment was created by Udacity, it already comes with the necessary libraries.
    * To run this environment you must to download Vagrant (https://www.vagrantup.com/) and VirtualBox (https://www.virtualbox.org/)
    * A list of libraries can be find in requirements.txt
3. Open directory cloned or downloaded in terminal and run:
    * vagrant up
    * vagrant ssh
    * cd /vagrant
    * cd catalog/
    * python application.py
4. Web app running in localhost:5000/

## How to contribute

### Bugs
The size limit of image to upload is 2MB. But when user try to upload a file
larger then 2MB an error is answered, but is not handled in the backend to not
break the application.

### Improvements
1. Each recipe is limited to 5 ingredients. It would be better if the user could
add as many ingredients as he wanted.

2. Create a function to edit image file name when upload to not have files with duplicate names

## Observation
The entire application is programmed in Python using Flask framework. The
database is SQLite and the CRUD functions use SQLAlchemy.
