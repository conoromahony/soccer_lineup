# soccer_lineup
#### Video Demo:  https://www.youtube.com/watch?v=JSshIOC_Nog
#### Description:
This website helps youth soccer coaches ensure all of their players get equal playing time.

## Background
I created this website after spending too much time each and every week, painstakingly planning my youth soccer team's 
substitution schedule in an attempt to ensure each player gets equal playing time. After manually figuring out my 
substitution strategy week-after-week, season-after-season, I created this website to automate what I had been manually 
doing. 

## Status
At present, this website is in the development phase, working only on my laptop. It has not yet been deployed to a 
production server for others to use. I plan to deploy it to a production server after I address the items marked in
the code comments as TODO items.

## Using the Website
When you first load this website, you are prompted to either create an account or to log in. Once you have created an
account and logged in, you see the home page:
![Soccer Lineup - Home Screen.png](Soccer%20Lineup%20-%20Home%20Screen.png?raw=true)

To get more context on the website, you can read the contents of the FAQs and About pages. When you are ready to use 
the website, you need to set up your team. Setting up your team is something that you will typically do once. It
consists of indicating information about the games you play and the players on your roster. After you set up your team, 
you typically only need to go to this website to generate lineups. The Team Setup page has configuration options for 
the Team Size, the Team Formation you typically plan to use, the Half Duration, and the Players on the roster. Here is 
what a Team Setup page might look like:
![Soccer Lineup - Team Setup.png](Soccer%20Lineup%20-%20Team%20Setup.png?raw=true)

As you add a player, you are prompted for their name, their preferred position, and the positions in which they play. 
Choose their Preferred Position from the dynamically-populated drop-down list, whose contents depend on the Team Size 
and Team Formation settings. Here is what the Add Player screen might look like:
![Soccer Lineup - Add Player.png](Soccer%20Lineup%20-%20Add%20Player.png?raw=true)

Now that the Team is set up, you can generate lineups for a game. Go back to the home page, and choose the Generate 
Lineup option. Specify the Opponent, the Date, the Team Formation for that game, the Players who are present, and who 
will play as Goalie. Here is what the Generate Lineup page looks like:
![Soccer Lineup - Generate Lineup.png](Soccer%20Lineup%20-%20Generate%20Lineup.png?raw=true)

When you generate the lineups for a game, this website determines the optimal number of substitution to perform and 
indicates the lineup after each of those substitutions. Here is what that page looks like:
![Soccer Lineups - Game Lineups.png](Soccer%20Lineups%20-%20Game%20Lineups.png?raw=true)

## Technologies
The technologies used to create this website are:
  - Python for server-side processing.
  - A Python virtual environment to contain the project.
  - The Django web framework (with HTML and JavaScript) to create the site.
  - A SQLite3 database.
  - The Bootstrap HTML and CSS front-end framework.
  - GitHub for version control.

## Project Organization
This project is organized into five Django applications:
 - **game_lineups**: The "main" application for the project. It includes configuration settings for the overall
   project, as well as settings for how to handle all URLs for the project.
 - **home**: Implements the Home page, the FAQs page, and the About page of the website.
 - **lineups**: Implements the part of the website for generating and viewing game lineups.
 - **team**: Implements the part of the website for setting up a team, including the roster of players.
 - **users**: Implements user accounts for the website, including the creation of accounts and logging in and out.

## Directories and Files
 - **.env**
   A file for storing environment variable settings.

 - **.gitignore**
   A file indicating the files not to push to the GitHub repository (because they contain sensitive information).

 - **db.sqlite3**
   The SQLite3 database for the Django project. 

 - **manage.py**
   A command-line utility that helps manage the Django project.

 - **README.md**
   This readme file (in markdown format). It describes the project and how it operates.

 - **requirements.txt**
   Indicates the libraries, modules, and packages required for this project.

 - **env**
   A directory containing the files for the Python environment for this project.

 - **game_lineups**
   The main project directory for this website.

 - **game_lineups/settings.py**
   The Django configuration settings for the project.

 - **game_lineups/urls.py**
   The main Django file for handling URLs for this project. It basically includes references to the urls.py for each 
   "application" in the project.

 - **home**
   The application that provides the "home" pages for the project.These include the Home page, the FAQs page, and the 
   About page.

 - **home/admin.py**
   Registers the models that we want to appear in the Django admin user interface. For the "home" application, only the 
   About page and it's Feedback form has any information that we want to store.

 - **home/apps.py**
   Specifies the configuration settings for the "home" application.

 - **home/forms.py**
   Specifies the forms that appear in web pages in the "home" application. That is, the Feedback form on the About page.

 - **home/models.py**
   Specifies the data models for the "home" application. That is, for the Feedback form on the About page.

 - **home/urls.py**
   Indicates how to handle URLs for the "home" application.

 - **home/views.py**
   Specifies the logic of the "home" application. Each view receives an HTTP request, processes it, and returns a 
   response (using the templates).

 - **home/templates/**
   The templates for the HTML pages that are rendered by the "home" application. There are five templates: 
   - *about.html* which is for the About page
   - *base.html* which is a base template file for all other files on the website. It includes the meta information as
     well as the navigation bar for the top of each page on the website.
   - *faqs.html* which is for the FAQs page
   - *index.html* which is the Home page for the website
   - *thanks.html* which is a version of the About page to be displayed after a user provides feedback (via the form).

 - **lineups**
   The application that allows users to generate lineups, and also allows them to see previously-generated lineups.

 - **lineups/admin.py**
   Registers the "lineups" application models that we want to appear in the Django admin user interface.

 - **lineups/apps.py**
   Specifies the configuration settings for the "lineups" application.

 - **lineups/forms.py**
   Specifies the forms that appear in web pages in the "lineups" application.

 - **lineups/models.py**
   Specifies the data models for the "lineups" application.

 - **lineups/urls.py**
   Indicates how to handle URLs for the "lineups" application.

 - **lineups/views.py**
   Specifies the logic of the "lineups" application. Each view receives an HTTP request, processes it, and returns a 
   response (using the templates).

 - **lineups/templates/**
   The templates for the HTML pages that are rendered by the "lineups" application. There are three templates: 
   - *list.html* which lists all previously-generated lineups
   - *new_lineup.html* which allows users to generate a set of lineups for a game
   - *view_lineup.html* which allows a user to view a set of lineups for a game

 - **team**
   The application that maintains information about a team, including details about games, information about the 
   players on the roster, and so on.

 - **team/admin.py**
   Registers the "team" application models that we want to appear in the Django admin user interface.

 - **team/apps.py**
   Specifies the configuration settings for the "team" application.

 - **team/forms.py**
   Specifies the forms that appear in web pages in the "team" application.

 - **team/models.py**
   Specifies the data models for the "team" application.

 - **team/urls.py**
   Indicates how to handle URLs for the "team" application.

 - **team/views.py**
   Specifies the logic of the "team" application. Each view receives an HTTP request, processes it, and returns a 
   response (using the templates).

 - **team/static/**
   The folder that stores the "static" items for this project. Static items include images and CSS files.

 - **team/templates/**
   The templates for the HTML pages that are rendered by the "team" application. There are three templates: 
   - *add.html* which allows a user to add a player to the roster
   - *list.html* which lists all players on a roster
   - *update.html* which allows a user to edit the information for a player

 - **users**
   The application that maintains information about the user accounts for this project.

 - **users/admin.py**
   Registers the "users" models that we want to appear in the Django admin user interface.

 - **users/apps.py**
   Specifies the configuration settings for the "users" application.

 - **users/models.py**
   Specifies the data models for the "user" application.

 - **users/urls.py**
   Indicates how to handle URLs for the "user" application.

 - **users/views.py**
   Specifies the logic of the "users" application. Each view receives an HTTP request, processes it, and returns a 
   response (using the templates).

 - **users/templates/**
   The templates for the HTML pages that are rendered by the "users" application. There are three templates: 
   - *logged_out.html* which is displayed when someone logs out
   - *login.html* which allows a registered user to log in
   - *register.html* which allows a visitor to the website to create a user account

## Notes: Deploying to Production
To deploy this project in a production environment, I’ll need to run it either:
 - As a WSGI application using a web server like Apache, Gunicorn, or uWSGI.
 - As an ASGI application using a server like Uvicorn or Daphne.

Also, I'll need to make sure to:
 - Change the DEBUG setting to False in settings.py.
 - Add the domain & host to the ALLOWED_HOSTS setting in settings.py.
